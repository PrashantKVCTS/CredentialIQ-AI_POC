using CredentialIQ.Core.Enums;

namespace CredentialIQ.Core.Models;

public class SanctionCheckResult
{
    public Guid Id { get; set; }
    public Guid CaseId { get; set; }
    public string Source { get; set; } = string.Empty; // e.g. OIG, SAM.gov, NPDB
    public SanctionStatus Status { get; set; } = SanctionStatus.Clear;
    public DateTime VerifiedAtUtc { get; set; } = DateTime.UtcNow;
    public string CorrelationId { get; set; } = string.Empty;
    public string EvidenceReference { get; set; } = string.Empty;
    public bool IsSimulated { get; set; } = true;
    public string HumanReadableExplanation { get; set; } = string.Empty;
}
