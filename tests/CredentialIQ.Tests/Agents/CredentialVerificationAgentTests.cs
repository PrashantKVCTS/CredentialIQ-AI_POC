using CredentialIQ.Agents;
using CredentialIQ.Core.Enums;
using CredentialIQ.Core.Models;
using Microsoft.Extensions.Logging.Abstractions;
using Xunit;

namespace CredentialIQ.Tests.Agents;

public class CredentialVerificationAgentTests
{
    private readonly CredentialVerificationAgent _agent;

    public CredentialVerificationAgentTests()
    {
        _agent = new CredentialVerificationAgent(NullLogger<CredentialVerificationAgent>.Instance);
    }

    [Fact]
    public async Task ExecuteAsync_ValidProvider_SetsStatusVerifyingAndAddsAudit()
    {
        var caseObj = new CredentialingCase
        {
            Provider = new Provider
            {
                Npi = "1234567890",
                FirstName = "Jane",
                LastName = "Doe",
                PrimaryState = "ca",
                LicenseNumber = "C12345",
                ProviderType = "Medical Doctor"
            }
        };

        var result = await _agent.ExecuteAsync(caseObj);

        Assert.Equal(CaseStatus.Verifying, result.Status);
        Assert.Equal("CA", result.Provider.PrimaryState);
        Assert.Single(result.AuditEvents);
        Assert.Equal("PASS", result.AuditEvents[0].Outcome);
    }

    [Fact]
    public async Task ExecuteAsync_InvalidNpi_SetsStatusOnHoldAndLogsAuditFail()
    {
        var caseObj = new CredentialingCase
        {
            Provider = new Provider
            {
                Npi = "INVALID_NPI",
                FirstName = "Jane",
                LastName = "Doe",
                PrimaryState = "CA",
                LicenseNumber = "C12345",
                ProviderType = "Medical Doctor"
            }
        };

        var result = await _agent.ExecuteAsync(caseObj);

        Assert.Equal(CaseStatus.OnHold, result.Status);
        Assert.Single(result.AuditEvents);
        Assert.Equal("FAIL", result.AuditEvents[0].Outcome);
    }
}
