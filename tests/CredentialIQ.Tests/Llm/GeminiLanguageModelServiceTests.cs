using CredentialIQ.Core.Enums;
using CredentialIQ.Core.Models;
using CredentialIQ.Infrastructure.Llm;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging.Abstractions;
using Moq;
using Xunit;

namespace CredentialIQ.Tests.Llm;

public class GeminiLanguageModelServiceTests
{
    [Fact]
    public async Task AssessRiskAsync_NoApiKey_FallsBackToDeterministic()
    {
        var httpFactoryMock = new Mock<IHttpClientFactory>();
        var configMock = new Mock<IConfiguration>();
        configMock.Setup(c => c[It.IsAny<string>()]).Returns((string)null!);

        var fallback = new DeterministicLanguageModelService(NullLogger<DeterministicLanguageModelService>.Instance);
        var service = new GeminiLanguageModelService(httpFactoryMock.Object, configMock.Object, NullLogger<GeminiLanguageModelService>.Instance, fallback);

        var caseObj = new CredentialingCase
        {
            Provider = new Provider { LicenseNumber = "C12345", PrimaryState = "CA" },
            VerificationResults = new List<VerificationResult> { new VerificationResult { Status = LicenseStatus.Active } }
        };

        var policies = new List<PolicyChunk> { new PolicyChunk { Id = "POL-1", RuleReference = "NCQA-CR1-LIC" } };

        var result = await service.AssessRiskAsync(caseObj, policies);

        Assert.Equal("Deterministic", result.EvaluatedBy);
        Assert.Equal(RiskClassification.Clean, result.Classification);
    }
}
