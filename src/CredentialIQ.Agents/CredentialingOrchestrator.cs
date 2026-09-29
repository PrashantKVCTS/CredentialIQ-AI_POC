using System.Diagnostics;
using CredentialIQ.Core.Enums;
using CredentialIQ.Core.Interfaces;
using CredentialIQ.Core.Models;
using Microsoft.Extensions.Logging;

namespace CredentialIQ.Agents;

public class CredentialingOrchestrator
{
    private readonly IEnumerable<ICredentialingAgent> _agents;
    private readonly ILogger<CredentialingOrchestrator> _logger;

    public CredentialingOrchestrator(
        IEnumerable<ICredentialingAgent> agents,
        ILogger<CredentialingOrchestrator> logger)
    {
        _agents = agents;
        _logger = logger;
    }

    public async Task<CredentialingCase> ProcessCaseAsync(CredentialingCase credentialingCase, CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Starting agentic credentialing pipeline for case {CaseId} (CorrelationId: {CorrelationId}).",
            credentialingCase.Id, credentialingCase.CorrelationId);

        var agentList = _agents.ToList();

        // Ensure 5-agent sequential order
        var orderedAgents = new List<ICredentialingAgent>
        {
            GetAgent<CredentialVerificationAgent>(agentList),
            GetAgent<LicenseVerificationAgent>(agentList),
            GetAgent<SanctionCheckAgent>(agentList),
            GetAgent<RiskAssessmentAgent>(agentList),
            GetAgent<WorkflowAgent>(agentList)
        };

        foreach (var agent in orderedAgents)
        {
            if (cancellationToken.IsCancellationRequested)
            {
                _logger.LogWarning("Pipeline cancelled before executing {AgentName}.", agent.AgentName);
                break;
            }

            var sw = Stopwatch.StartNew();
            var startTime = DateTime.UtcNow;

            try
            {
                _logger.LogInformation("Executing agent [{AgentName}]...", agent.AgentName);
                credentialingCase = await agent.ExecuteAsync(credentialingCase, cancellationToken);
                sw.Stop();

                _logger.LogInformation("Agent [{AgentName}] completed in {DurationMs} ms.", agent.AgentName, sw.ElapsedMilliseconds);

                credentialingCase.Metadata[$"Telemetry:{agent.AgentName}:DurationMs"] = sw.ElapsedMilliseconds.ToString();
                credentialingCase.Metadata[$"Telemetry:{agent.AgentName}:CompletedAtUtc"] = DateTime.UtcNow.ToString("o");
            }
            catch (Exception ex)
            {
                sw.Stop();
                _logger.LogError(ex, "Unrecoverable error in agent [{AgentName}] for case {CaseId}. Halting pipeline and preserving partial state.",
                    agent.AgentName, credentialingCase.Id);

                credentialingCase.Status = CaseStatus.OnHold;
                credentialingCase.AuditEvents.Add(new AuditEvent
                {
                    CaseId = credentialingCase.Id,
                    Source = agent.AgentName,
                    Action = "ExecutePipelineStep",
                    Outcome = "ERROR",
                    UtcTimestamp = DateTime.UtcNow,
                    CorrelationId = credentialingCase.CorrelationId,
                    EvidenceReference = $"ERR-{Guid.NewGuid():N}",
                    IsSimulated = true,
                    HumanReadableExplanation = $"Pipeline execution halted at agent {agent.AgentName}. Internal system exception recorded safely without exposing secret trace."
                });

                break;
            }
        }

        credentialingCase.UpdatedAtUtc = DateTime.UtcNow;
        _logger.LogInformation("Credentialing pipeline completed for case {CaseId}. Final Status: {Status}, Classification: {Classification}.",
            credentialingCase.Id, credentialingCase.Status, credentialingCase.RiskClassification);

        return credentialingCase;
    }

    private static ICredentialingAgent GetAgent<T>(List<ICredentialingAgent> agentList) where T : ICredentialingAgent
    {
        var agent = agentList.OfType<T>().FirstOrDefault();
        if (agent == null)
        {
            throw new InvalidOperationException($"Required agent {typeof(T).Name} is not registered in Dependency Injection container.");
        }
        return agent;
    }
}
