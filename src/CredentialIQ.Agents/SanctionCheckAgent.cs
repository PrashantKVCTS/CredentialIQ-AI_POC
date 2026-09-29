using CredentialIQ.Core.Enums;
using CredentialIQ.Core.Interfaces;
using CredentialIQ.Core.Models;
using Microsoft.Extensions.Logging;

namespace CredentialIQ.Agents;

public class SanctionCheckAgent : ICredentialingAgent
{
    private readonly ISanctionConnector _sanctionConnector;
    private readonly ILogger<SanctionCheckAgent> _logger;

    public SanctionCheckAgent(ISanctionConnector sanctionConnector, ILogger<SanctionCheckAgent> logger)
    {
        _sanctionConnector = sanctionConnector;
        _logger = logger;
    }

    public string AgentName => "SanctionCheckAgent";

    public async Task<CredentialingCase> ExecuteAsync(CredentialingCase credentialingCase, CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("[{AgentName}] Executing sanction screening for case {CaseId}.", AgentName, credentialingCase.Id);

        var sanctionResult = await _sanctionConnector.CheckSanctionsAsync(credentialingCase.Provider, cancellationToken);
        sanctionResult.CaseId = credentialingCase.Id;
        sanctionResult.CorrelationId = credentialingCase.CorrelationId;

        credentialingCase.SanctionResults.Add(sanctionResult);
        credentialingCase.Status = CaseStatus.RiskAssessment;

        credentialingCase.AuditEvents.Add(new AuditEvent
        {
            CaseId = credentialingCase.Id,
            Source = AgentName,
            Action = "ScreenExclusionDatabases",
            Outcome = sanctionResult.Status.ToString(),
            UtcTimestamp = DateTime.UtcNow,
            CorrelationId = credentialingCase.CorrelationId,
            EvidenceReference = sanctionResult.EvidenceReference,
            IsSimulated = sanctionResult.IsSimulated,
            HumanReadableExplanation = sanctionResult.HumanReadableExplanation
        });

        return credentialingCase;
    }
}
