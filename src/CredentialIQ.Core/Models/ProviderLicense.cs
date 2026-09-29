using CredentialIQ.Core.Enums;

namespace CredentialIQ.Core.Models;

public class ProviderLicense
{
    public Guid Id { get; set; }
    public Guid ProviderId { get; set; }
    public string LicenseNumber { get; set; } = string.Empty;
    public string State { get; set; } = string.Empty;
    public DateTime? IssueDate { get; set; }
    public DateTime? ExpirationDate { get; set; }
    public LicenseStatus Status { get; set; } = LicenseStatus.Unknown;
    public DateTime VerifiedDate { get; set; } = DateTime.UtcNow;
    public bool IsSimulated { get; set; } = true;
    public string Explanation { get; set; } = string.Empty;
}
