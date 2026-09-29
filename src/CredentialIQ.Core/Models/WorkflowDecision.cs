using CredentialIQ.Core.Enums;

namespace CredentialIQ.Core.Models;

public class WorkflowDecision
{
    public Guid Id { get; set; }
    public Guid CaseId { get; set; }
    public CaseStatus Status { get; set; }
    public CaseStatus TargetStatus { get; set; }
    public string RecommendedAction { get; set; } = string.Empty;
    public string CaseSummary { get; set; } = string.Empty;
    public DateTime RecommendedAtUtc { get; set; } = DateTime.UtcNow;
    public string CorrelationId { get; set; } = string.Empty;

    // Human override fields
    public bool IsHumanOverride { get; set; } = false;
    public string? OverriddenBy { get; set; }
    public string? OverrideReason { get; set; }
    public DateTime? OverriddenAtUtc { get; set; }
}
