using CredentialIQ.Core.Enums;
using CredentialIQ.Core.Interfaces;
using CredentialIQ.Core.Models;

namespace CredentialIQ.Infrastructure.Connectors;

public class MockStateBoardConnector : IVerificationConnector
{
    public string SourceName => "MockStateMedicalBoardConnector";

    public Task<VerificationResult> VerifyLicenseAsync(Provider provider, CancellationToken cancellationToken = default)
    {
        var licenseNum = provider.LicenseNumber?.Trim().ToUpperInvariant() ?? string.Empty;
        LicenseStatus status;
        string explanation;
        DateTime? expirationDate = DateTime.UtcNow.AddYears(1);

        if (licenseNum.StartsWith("EXP-") || licenseNum.Contains("EXPIRED"))
        {
            status = LicenseStatus.Expired;
            expirationDate = DateTime.UtcNow.AddMonths(-2);
            explanation = $"[SIMULATED] License {licenseNum} in state {provider.PrimaryState} expired on {expirationDate:yyyy-MM-dd}.";
        }
        else if (licenseNum.StartsWith("SUSP-") || licenseNum.Contains("SUSPENDED"))
        {
            status = LicenseStatus.Suspended;
            explanation = $"[SIMULATED] License {licenseNum} in state {provider.PrimaryState} is SUSPENDED due to board disciplinary action.";
        }
        else if (licenseNum.StartsWith("NF-") || licenseNum.Contains("NOTFOUND"))
        {
            status = LicenseStatus.NotFound;
            expirationDate = null;
            explanation = $"[SIMULATED] License {licenseNum} not found in state board registry for {provider.PrimaryState}.";
        }
        else
        {
            status = LicenseStatus.Active;
            explanation = $"[SIMULATED] License {licenseNum} verified Active and in good standing with {provider.PrimaryState} State Licensing Board.";
        }

        var result = new VerificationResult
        {
            Source = SourceName,
            Status = status,
            ExpirationDate = expirationDate,
            VerifiedAtUtc = DateTime.UtcNow,
            EvidenceReference = $"SIM-DOC-STATEBOARD-{Guid.NewGuid():N}",
            IsSimulated = true,
            HumanReadableExplanation = explanation
        };

        return Task.FromResult(result);
    }
}
