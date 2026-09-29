namespace CredentialIQ.Core.Models;

public class Provider
{
    public Guid Id { get; set; }
    public string Npi { get; set; } = string.Empty;
    public string FirstName { get; set; } = string.Empty;
    public string LastName { get; set; } = string.Empty;
    public string ProviderType { get; set; } = string.Empty; // e.g. Medical Doctor, Nurse Practitioner
    public string PrimaryState { get; set; } = string.Empty;
    public string LicenseNumber { get; set; } = string.Empty;
    public DateTime? DateOfBirth { get; set; }
    public string? Email { get; set; }
    public string? Phone { get; set; }
    public string? Address { get; set; }
}
