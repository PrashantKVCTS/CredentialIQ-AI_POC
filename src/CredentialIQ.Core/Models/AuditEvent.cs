namespace CredentialIQ.Core.Models;

public class AuditEvent
{
    public Guid Id { get; set; }
    public Guid CaseId { get; set; }
    public string Source { get; set; } = string.Empty;
    public string Action { get; set; } = string.Empty;
    public string Outcome { get; set; } = string.Empty;
    public DateTime UtcTimestamp { get; set; } = DateTime.UtcNow;
    public string CorrelationId { get; set; } = string.Empty;
    public string EvidenceReference { get; set; } = string.Empty;
    public bool IsSimulated { get; set; } = true;
    public string HumanReadableExplanation { get; set; } = string.Empty;
}
