using CredentialIQ.Core.Models;

namespace CredentialIQ.Core.DTOs;

public class EvidenceAuditResponse
{
    public Guid CaseId { get; set; }
    public string CorrelationId { get; set; } = string.Empty;
    public List<VerificationResult> VerificationResults { get; set; } = new();
    public List<SanctionCheckResult> SanctionResults { get; set; } = new();
    public List<RiskAssessment> RiskAssessments { get; set; } = new();
    public List<WorkflowDecision> WorkflowDecisions { get; set; } = new();
    public List<AuditEvent> AuditEvents { get; set; } = new();
}
