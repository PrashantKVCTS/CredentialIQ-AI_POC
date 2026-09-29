using CredentialIQ.Infrastructure.Rag;
using Microsoft.Extensions.Logging.Abstractions;
using Xunit;

namespace CredentialIQ.Tests.Rag;

public class LocalRagRepositoryTests
{
    [Fact]
    public async Task SearchPoliciesAsync_ReturnsScoredTopKPolicies_FlaggedSynthetic()
    {
        var repo = new LocalRagRepository(NullLogger<LocalRagRepository>.Instance);

        var results = await repo.SearchPoliciesAsync("expired license grace period", "CA", "Medical Doctor", topK: 3);

        Assert.NotEmpty(results);
        Assert.True(results.Count <= 3);
        Assert.All(results, p => Assert.True(p.IsSynthetic));
        Assert.All(results, p => Assert.False(string.IsNullOrWhiteSpace(p.RuleReference)));
    }
}
