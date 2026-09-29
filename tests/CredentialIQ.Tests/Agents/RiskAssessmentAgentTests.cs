using CredentialIQ.Agents;
using CredentialIQ.Core.Enums;
using CredentialIQ.Core.Interfaces;
using CredentialIQ.Core.Models;
using Microsoft.Extensions.Logging.Abstractions;
using Moq;
using Xunit;

namespace CredentialIQ.Tests.Agents;

public class RiskAssessmentAgentTests
{
    [Fact]
    public async Task ExecuteAsync_RetrievesPoliciesAndEvaluatesRisk_GroundedInPolicies()
    {
        var ragMock = new Mock<IRagRepository>();
        ragMock.Setup(r => r.SearchPoliciesAsync(It.IsAny<string>(), It.IsAny<string>(), It.IsAny<string>(), It.IsAny<int>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(new List<PolicyChunk>
            {
                new PolicyChunk { Id = "POL-101", RuleReference = "NCQA-CR1-LIC", Content = "Active license required." }
            });

        var llmMock = new Mock<ILanguageModelService>();
        llmMock.Setup(l => l.AssessRiskAsync(It.IsAny<CredentialingCase>(), It.IsAny<List<PolicyChunk>>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(new RiskAssessment
            {
                Classification = RiskClassification.Clean,
                Rationale = "Clean active license.",
                AppliedRuleReferences = new List<string> { "NCQA-CR1-LIC" }
            });

        var agent = new RiskAssessmentAgent(ragMock.Object, llmMock.Object, NullLogger<RiskAssessmentAgent>.Instance);
        var caseObj = new CredentialingCase
        {
            Provider = new Provider { PrimaryState = "CA", ProviderType = "Medical Doctor" }
        };

        var result = await agent.ExecuteAsync(caseObj);

        Assert.Equal(RiskClassification.Clean, result.RiskClassification);
        Assert.Single(result.RiskAssessments);
        Assert.Contains("NCQA-CR1-LIC", result.RiskAssessments[0].AppliedRuleReferences);
    }
}
