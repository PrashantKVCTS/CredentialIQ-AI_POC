using CredentialIQ.Agents;
using CredentialIQ.Core.Enums;
using CredentialIQ.Core.Interfaces;
using CredentialIQ.Core.Models;
using Microsoft.Extensions.Logging.Abstractions;
using Moq;
using Xunit;

namespace CredentialIQ.Tests.Agents;

public class LicenseVerificationAgentTests
{
    [Theory]
    [InlineData(LicenseStatus.Active)]
    [InlineData(LicenseStatus.Expired)]
    [InlineData(LicenseStatus.Suspended)]
    public async Task ExecuteAsync_InvokesConnector_RecordsEvidenceAndUpdatesStatus(LicenseStatus expectedStatus)
    {
        var connectorMock = new Mock<IVerificationConnector>();
        connectorMock.Setup(c => c.VerifyLicenseAsync(It.IsAny<Provider>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(new VerificationResult
            {
                Source = "MockStateBoard",
                Status = expectedStatus,
                HumanReadableExplanation = "Test license verification result."
            });

        var agent = new LicenseVerificationAgent(connectorMock.Object, NullLogger<LicenseVerificationAgent>.Instance);
        var caseObj = new CredentialingCase
        {
            Provider = new Provider { LicenseNumber = "TEST-LIC", PrimaryState = "CA" }
        };

        var result = await agent.ExecuteAsync(caseObj);

        Assert.Equal(CaseStatus.SanctionScreening, result.Status);
        Assert.Single(result.VerificationResults);
        Assert.Equal(expectedStatus, result.VerificationResults[0].Status);
        Assert.True(result.VerificationResults[0].IsSimulated);
    }
}
