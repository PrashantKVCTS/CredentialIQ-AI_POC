using CredentialIQ.Core.Enums;

namespace CredentialIQ.Core.Models;

public class RiskAssessment
{
    public Guid Id { get; set; }
    public Guid CaseId { get; set; }
    public RiskClassification Classification { get; set; } = RiskClassification.Clean;
    public double ConfidenceScore { get; set; } = 1.0;
    public string Rationale { get; set; } = string.Empty;
    public List<string> AppliedRuleReferences { get; set; } = new();
    public List<string> RetrievedSourceIds { get; set; } = new();
    public DateTime AssessedAtUtc { get; set; } = DateTime.UtcNow;
    public string CorrelationId { get; set; } = string.Empty;
    public string EvaluatedBy { get; set; } = "Deterministic"; // Deterministic or Gemini
}
