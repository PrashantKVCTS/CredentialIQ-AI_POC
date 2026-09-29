using CredentialIQ.Core.Models;

namespace CredentialIQ.Core.Interfaces;

public interface IVerificationConnector
{
    string SourceName { get; }
    Task<VerificationResult> VerifyLicenseAsync(Provider provider, CancellationToken cancellationToken = default);
}
