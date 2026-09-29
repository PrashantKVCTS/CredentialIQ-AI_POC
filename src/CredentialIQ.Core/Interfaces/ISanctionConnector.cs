using CredentialIQ.Core.Models;

namespace CredentialIQ.Core.Interfaces;

public interface ISanctionConnector
{
    string SourceName { get; }
    Task<SanctionCheckResult> CheckSanctionsAsync(Provider provider, CancellationToken cancellationToken = default);
}
