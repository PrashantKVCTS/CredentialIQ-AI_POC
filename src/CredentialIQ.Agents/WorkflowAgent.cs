using CredentialIQ.Core.Enums;
using CredentialIQ.Core.Interfaces;
using CredentialIQ.Core.Models;
using Microsoft.Extensions.Logging;

namespace CredentialIQ.Agents;

public class WorkflowAgent : ICredentialingAgent
{
    private readonly ILogger<WorkflowAgent> _logger;

    public WorkflowAgent(ILogger<WorkflowAgent> logger)
    {
        _logger = logger;
    }

    public string AgentName => "WorkflowAgent";

    public Task<CredentialingCase> ExecuteAsync(CredentialingCase credentialingCase, CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("[{AgentName}] Determining final workflow recommendation for case {CaseId}.", AgentName, credentialingCase.Id);

        var latestLic = credentialingCase.VerificationResults.LastOrDefault();
        var latestSanc = credentialingCase.SanctionResults.LastOrDefault();
        var latestRisk = credentialingCase.RiskAssessments.LastOrDefault();

        CaseStatus targetStatus;
        string recommendedAction;
        string caseSummary;

        // HARD SAFETY REQUIREMENT: A sanction match or suspended license MUST NEVER be automatically approved!
        if (latestSanc?.Status == SanctionStatus.MatchFound || latestLic?.Status == LicenseStatus.Suspended)
        {
            targetStatus = CaseStatus.OnHold;
            recommendedAction = "MANDATORY HOLD: Immediate referral to Legal & Compliance Committee. Automatic approval strictly prohibited.";
            caseSummary = $"CRITICAL SAFETY ALERT: Provider {credentialingCase.Provider.FirstName} {credentialingCase.Provider.LastName} has a recorded Sanction Match or Suspended License. Application placed on HOLD.";
        }
        else if (latestRisk?.Classification == RiskClassification.Hold || latestLic?.Status == LicenseStatus.NotFound)
        {
            targetStatus = CaseStatus.OnHold;
            recommendedAction = "PLACE ON HOLD: Request missing primary-source verification or documentation from provider.";
            caseSummary = $"HOLD RECOMMENDATION: Application for {credentialingCase.Provider.FirstName} {credentialingCase.Provider.LastName} requires additional verification.";
        }
        else if (latestRisk?.Classification == RiskClassification.Exception || latestLic?.Status == LicenseStatus.Expired)
        {
            targetStatus = CaseStatus.CommitteeReview;
            recommendedAction = "ROUTE TO COMMITTEE REVIEW: License expiration policy exception detected. Escalate to Credentialing Committee.";
            caseSummary = $"EXCEPTION RECOMMENDATION: License for {credentialingCase.Provider.FirstName} {credentialingCase.Provider.LastName} is expired. Routed for Committee Review.";
        }
        else
        {
            targetStatus = CaseStatus.Approved;
            recommendedAction = "RECOMMEND APPROVAL: Expedited credentialing approval recommended based on clean primary-source verification and zero sanction matches.";
            caseSummary = $"APPROVAL RECOMMENDATION: Provider {credentialingCase.Provider.FirstName} {credentialingCase.Provider.LastName} passed all verification and screening checks.";
        }

        credentialingCase.Status = targetStatus;
        credentialingCase.Recommendation = recommendedAction;

        var decision = new WorkflowDecision
        {
            CaseId = credentialingCase.Id,
            Status = CaseStatus.RiskAssessment,
            TargetStatus = targetStatus,
            RecommendedAction = recommendedAction,
            CaseSummary = caseSummary,
            RecommendedAtUtc = DateTime.UtcNow,
            CorrelationId = credentialingCase.CorrelationId,
            IsHumanOverride = false
        };

        credentialingCase.WorkflowDecisions.Add(decision);

        credentialingCase.AuditEvents.Add(new AuditEvent
        {
            CaseId = credentialingCase.Id,
            Source = AgentName,
            Action = "MakeWorkflowDecision",
            Outcome = targetStatus.ToString(),
            UtcTimestamp = DateTime.UtcNow,
            CorrelationId = credentialingCase.CorrelationId,
            EvidenceReference = $"EVID-WORKFLOW-{decision.Id:N}",
            IsSimulated = true,
            HumanReadableExplanation = $"Workflow decision generated: {recommendedAction} (Target Status: {targetStatus}). POC Disclaimer: Requires authorized human credentialing committee review."
        });

        return Task.FromResult(credentialingCase);
    }
}
