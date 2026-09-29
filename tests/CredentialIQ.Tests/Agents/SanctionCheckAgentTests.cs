using CredentialIQ.Agents;
using CredentialIQ.Core.Enums;
using CredentialIQ.Core.Interfaces;
using CredentialIQ.Core.Models;
using Microsoft.Extensions.Logging.Abstractions;
using Moq;
using Xunit;

namespace CredentialIQ.Tests.Agents;

public class SanctionCheckAgentTests
{
    [Fact]
    public async Task ExecuteAsync_SanctionMatchFound_AppendsResultAndSetsStatus()
    {
        var connectorMock = new Mock<ISanctionConnector>();
        connectorMock.Setup(c => c.CheckSanctionsAsync(It.IsAny<Provider>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(new SanctionCheckResult
            {
                Source = "MockOIG",
                Status = SanctionStatus.MatchFound,
                HumanReadableExplanation = "Match found in exclusion list."
            });

        var agent = new SanctionCheckAgent(connectorMock.Object, NullLogger<SanctionCheckAgent>.Instance);
        var caseObj = new CredentialingCase
        {
            Provider = new Provider { Npi = "1234567899", LastName = "SANCTIONED" }
        };

        var result = await agent.ExecuteAsync(caseObj);

        Assert.Equal(CaseStatus.RiskAssessment, result.Status);
        Assert.Single(result.SanctionResults);
        Assert.Equal(SanctionStatus.MatchFound, result.SanctionResults[0].Status);
    }
}
