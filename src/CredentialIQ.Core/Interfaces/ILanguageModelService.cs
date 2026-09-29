using CredentialIQ.Core.Models;

namespace CredentialIQ.Core.Interfaces;

public interface ILanguageModelService
{
    string ProviderName { get; }
    Task<RiskAssessment> AssessRiskAsync(
        CredentialingCase credentialingCase,
        List<PolicyChunk> retrievedPolicies,
        CancellationToken cancellationToken = default);
}
