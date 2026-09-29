using CredentialIQ.Core.Enums;
using CredentialIQ.Core.Interfaces;
using CredentialIQ.Core.Models;
using Microsoft.Extensions.Logging;

namespace CredentialIQ.Infrastructure.Llm;

public class DeterministicLanguageModelService : ILanguageModelService
{
    private readonly ILogger<DeterministicLanguageModelService> _logger;

    public DeterministicLanguageModelService(ILogger<DeterministicLanguageModelService> logger)
    {
        _logger = logger;
    }

    public string ProviderName => "Deterministic";

    public Task<RiskAssessment> AssessRiskAsync(
        CredentialingCase credentialingCase,
        List<PolicyChunk> retrievedPolicies,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Performing deterministic rules-based risk assessment for case {CaseId}.", credentialingCase.Id);

        var latestLic = credentialingCase.VerificationResults.LastOrDefault();
        var latestSanc = credentialingCase.SanctionResults.LastOrDefault();

        RiskClassification classification;
        string rationale;
        var appliedRules = new List<string>();
        var sourceIds = retrievedPolicies.Select(p => p.Id).ToList();

        // Hard rule checks
        if (latestSanc?.Status == SanctionStatus.MatchFound)
        {
            classification = RiskClassification.Hold;
            rationale = "SANCTION MATCH DETECTED: Federal/State exclusion list match found. Mandatory hold required.";
            appliedRules.Add(retrievedPolicies.FirstOrDefault(p => p.RuleReference.Contains("SANC"))?.RuleReference ?? "FED-SANC-MATCH");
        }
        else if (latestLic?.Status == LicenseStatus.Suspended)
        {
            classification = RiskClassification.Hold;
            rationale = "SUSPENDED LICENSE: Primary state license is suspended. Mandatory hold required.";
            appliedRules.Add(retrievedPolicies.FirstOrDefault(p => p.RuleReference.Contains("SUSP"))?.RuleReference ?? "STATE-LIC-SUSP");
        }
        else if (latestLic?.Status == LicenseStatus.NotFound || latestLic?.Status == LicenseStatus.Unknown)
        {
            classification = RiskClassification.Hold;
            rationale = "UNVERIFIED LICENSE: State board license verification was not found or unverified. Hold for clarification.";
            appliedRules.Add(retrievedPolicies.FirstOrDefault(p => p.RuleReference.Contains("MISSING"))?.RuleReference ?? "SOP-MISSING-INFO");
        }
        else if (latestLic?.Status == LicenseStatus.Expired)
        {
            classification = RiskClassification.Exception;
            rationale = "EXPIRED LICENSE EXCEPTION: Primary state license has expired. Requires Credentialing Committee review for grace period.";
            appliedRules.Add(retrievedPolicies.FirstOrDefault(p => p.RuleReference.Contains("EXP") || p.RuleReference.Contains("LIC"))?.RuleReference ?? "STATE-LIC-EXP");
        }
        else
        {
            classification = RiskClassification.Clean;
            rationale = "CLEAN APPLICATION: Active state license verified with zero sanction or restriction matches.";
            appliedRules.Add(retrievedPolicies.FirstOrDefault(p => p.RuleReference.Contains("EXP-01") || p.RuleReference.Contains("CR1"))?.RuleReference ?? "NCQA-CR1-LIC");
        }

        var assessment = new RiskAssessment
        {
            CaseId = credentialingCase.Id,
            Classification = classification,
            ConfidenceScore = 1.0,
            Rationale = rationale,
            AppliedRuleReferences = appliedRules,
            RetrievedSourceIds = sourceIds,
            AssessedAtUtc = DateTime.UtcNow,
            CorrelationId = credentialingCase.CorrelationId,
            EvaluatedBy = ProviderName
        };

        return Task.FromResult(assessment);
    }
}
