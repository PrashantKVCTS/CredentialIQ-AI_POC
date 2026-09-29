using CredentialIQ.Core.Enums;
using CredentialIQ.Core.Interfaces;
using CredentialIQ.Core.Models;
using Microsoft.Extensions.Logging;

namespace CredentialIQ.Agents;

public class RiskAssessmentAgent : ICredentialingAgent
{
    private readonly IRagRepository _ragRepository;
    private readonly ILanguageModelService _llmService;
    private readonly ILogger<RiskAssessmentAgent> _logger;

    public RiskAssessmentAgent(
        IRagRepository ragRepository,
        ILanguageModelService llmService,
        ILogger<RiskAssessmentAgent> logger)
    {
        _ragRepository = ragRepository;
        _llmService = llmService;
        _logger = logger;
    }

    public string AgentName => "RiskAssessmentAgent";

    public async Task<CredentialingCase> ExecuteAsync(CredentialingCase credentialingCase, CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("[{AgentName}] Executing RAG policy search & risk evaluation for case {CaseId}.", AgentName, credentialingCase.Id);

        var latestLic = credentialingCase.VerificationResults.LastOrDefault();
        var latestSanc = credentialingCase.SanctionResults.LastOrDefault();

        string searchQuery = $"credentialing license {latestLic?.Status} sanction {latestSanc?.Status} provider {credentialingCase.Provider.ProviderType}";
        var retrievedPolicies = await _ragRepository.SearchPoliciesAsync(
            searchQuery, credentialingCase.Provider.PrimaryState, credentialingCase.Provider.ProviderType, topK: 5, cancellationToken);

        _logger.LogInformation("Retrieved {Count} policy chunks from LocalRagRepository.", retrievedPolicies.Count);

        var riskAssessment = await _llmService.AssessRiskAsync(credentialingCase, retrievedPolicies, cancellationToken);
        riskAssessment.CaseId = credentialingCase.Id;
        riskAssessment.CorrelationId = credentialingCase.CorrelationId;

        credentialingCase.RiskAssessments.Add(riskAssessment);
        credentialingCase.RiskClassification = riskAssessment.Classification;

        credentialingCase.AuditEvents.Add(new AuditEvent
        {
            CaseId = credentialingCase.Id,
            Source = AgentName,
            Action = "AssessCredentialingRisk",
            Outcome = riskAssessment.Classification.ToString(),
            UtcTimestamp = DateTime.UtcNow,
            CorrelationId = credentialingCase.CorrelationId,
            EvidenceReference = $"EVID-RISK-{riskAssessment.Id:N}",
            IsSimulated = true,
            HumanReadableExplanation = $"Risk assessed as {riskAssessment.Classification} ({riskAssessment.EvaluatedBy}). Rationale: {riskAssessment.Rationale}. Applied Rules: {string.Join(", ", riskAssessment.AppliedRuleReferences)}"
        });

        return credentialingCase;
    }
}
