using CredentialIQ.Core.Enums;
using CredentialIQ.Core.Interfaces;
using CredentialIQ.Core.Models;

namespace CredentialIQ.Infrastructure.Connectors;

public class MockSanctionConnector : ISanctionConnector
{
    public string SourceName => "MockSanctionScreeningConnector (OIG/SAM/NPDB)";

    public Task<SanctionCheckResult> CheckSanctionsAsync(Provider provider, CancellationToken cancellationToken = default)
    {
        var npi = provider.Npi?.Trim() ?? string.Empty;
        var lastName = provider.LastName?.Trim().ToUpperInvariant() ?? string.Empty;
        var license = provider.LicenseNumber?.Trim().ToUpperInvariant() ?? string.Empty;

        bool matchFound = npi.EndsWith("999") ||
                          lastName.Contains("SANCTIONED") ||
                          license.Contains("SANC");

        SanctionStatus status = matchFound ? SanctionStatus.MatchFound : SanctionStatus.Clear;
        string explanation = matchFound
            ? $"[SIMULATED] MATCH DETECTED: Provider NPI {npi} ({provider.FirstName} {provider.LastName}) matches entry in federal OIG/SAM exclusion list."
            : $"[SIMULATED] CLEAR: Provider NPI {npi} ({provider.FirstName} {provider.LastName}) searched across OIG LEIE, SAM.gov, and NPDB database. No exclusions or sanctions found.";

        var result = new SanctionCheckResult
        {
            Source = SourceName,
            Status = status,
            VerifiedAtUtc = DateTime.UtcNow,
            EvidenceReference = $"SIM-DOC-SANCTION-{Guid.NewGuid():N}",
            IsSimulated = true,
            HumanReadableExplanation = explanation
        };

        return Task.FromResult(result);
    }
}
