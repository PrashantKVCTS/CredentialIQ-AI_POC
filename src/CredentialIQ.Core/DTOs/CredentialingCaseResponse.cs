using CredentialIQ.Core.Enums;
using CredentialIQ.Core.Models;

namespace CredentialIQ.Core.DTOs;

public class CredentialingCaseResponse
{
    public Guid Id { get; set; }
    public string CorrelationId { get; set; } = string.Empty;
    public Guid ProviderId { get; set; }
    public Provider Provider { get; set; } = default!;
    public CaseStatus Status { get; set; }
    public RiskClassification? RiskClassification { get; set; }
    public string? Recommendation { get; set; }
    public DateTime CreatedAtUtc { get; set; }
    public DateTime UpdatedAtUtc { get; set; }

    public VerificationResult? LatestVerificationResult { get; set; }
    public SanctionCheckResult? LatestSanctionResult { get; set; }
    public RiskAssessment? LatestRiskAssessment { get; set; }
    public WorkflowDecision? LatestWorkflowDecision { get; set; }

    public string Disclaimer { get; set; } = "POC Disclaimer: CredentialIQ AI recommendations are simulated for demonstration purposes only and require review and authorization by a qualified human credentialing committee before any official action.";
}
