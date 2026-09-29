using CredentialIQ.Core.Enums;

namespace CredentialIQ.Core.Models;

public class CredentialingCase
{
    public Guid Id { get; set; }
    public string CorrelationId { get; set; } = Guid.NewGuid().ToString("N");
    public Guid ProviderId { get; set; }
    public Provider Provider { get; set; } = default!;
    public CaseStatus Status { get; set; } = CaseStatus.Intake;
    public RiskClassification? RiskClassification { get; set; }
    public string? Recommendation { get; set; }
    public DateTime CreatedAtUtc { get; set; } = DateTime.UtcNow;
    public DateTime UpdatedAtUtc { get; set; } = DateTime.UtcNow;

    public List<VerificationResult> VerificationResults { get; set; } = new();
    public List<SanctionCheckResult> SanctionResults { get; set; } = new();
    public List<RiskAssessment> RiskAssessments { get; set; } = new();
    public List<WorkflowDecision> WorkflowDecisions { get; set; } = new();
    public List<AuditEvent> AuditEvents { get; set; } = new();

    // Key-value metadata dictionary for transient or execution telemetry
    public Dictionary<string, string> Metadata { get; set; } = new();
}
