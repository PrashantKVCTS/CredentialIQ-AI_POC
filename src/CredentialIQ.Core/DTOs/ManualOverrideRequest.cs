using CredentialIQ.Core.Enums;

namespace CredentialIQ.Core.DTOs;

public class ManualOverrideRequest
{
    public CaseStatus TargetStatus { get; set; }
    public string ReviewerName { get; set; } = string.Empty;
    public string Reason { get; set; } = string.Empty;
}
