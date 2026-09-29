using CredentialIQ.Core.Models;

namespace CredentialIQ.Core.Interfaces;

public interface IRagRepository
{
    Task SeedPoliciesAsync(CancellationToken cancellationToken = default);
    Task<List<PolicyChunk>> SearchPoliciesAsync(string query, string state, string providerType, int topK = 5, CancellationToken cancellationToken = default);
}
