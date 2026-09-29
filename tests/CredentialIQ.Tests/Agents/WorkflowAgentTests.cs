using CredentialIQ.Agents;
using CredentialIQ.Core.Enums;
using CredentialIQ.Core.Models;
using Microsoft.Extensions.Logging.Abstractions;
using Xunit;

namespace CredentialIQ.Tests.Agents;

public class WorkflowAgentTests
{
    private readonly WorkflowAgent _agent;

    public WorkflowAgentTests()
    {
        _agent = new WorkflowAgent(NullLogger<WorkflowAgent>.Instance);
    }

    [Fact]
    public async Task ExecuteAsync_CleanCase_RecommendsApproval()
    {
        var caseObj = new CredentialingCase
        {
            Provider = new Provider { FirstName = "Jane", LastName = "Doe" },
            VerificationResults = new List<VerificationResult> { new VerificationResult { Status = LicenseStatus.Active } },
            SanctionResults = new List<SanctionCheckResult> { new SanctionCheckResult { Status = SanctionStatus.Clear } },
            RiskAssessments = new List<RiskAssessment> { new RiskAssessment { Classification = RiskClassification.Clean } }
        };

        var result = await _agent.ExecuteAsync(caseObj);

        Assert.Equal(CaseStatus.Approved, result.Status);
        Assert.Contains("RECOMMEND APPROVAL", result.Recommendation);
    }

    [Fact]
    public async Task ExecuteAsync_ExpiredLicense_RoutesToCommitteeReview()
    {
        var caseObj = new CredentialingCase
        {
            Provider = new Provider { FirstName = "Robert", LastName = "Smith" },
            VerificationResults = new List<VerificationResult> { new VerificationResult { Status = LicenseStatus.Expired } },
            SanctionResults = new List<SanctionCheckResult> { new SanctionCheckResult { Status = SanctionStatus.Clear } },
            RiskAssessments = new List<RiskAssessment> { new RiskAssessment { Classification = RiskClassification.Exception } }
        };

        var result = await _agent.ExecuteAsync(caseObj);

        Assert.Equal(CaseStatus.CommitteeReview, result.Status);
        Assert.Contains("COMMITTEE REVIEW", result.Recommendation);
    }

    [Fact]
    public async Task ExecuteAsync_SuspendedLicense_NeverAutoApproved_SetsOnHold()
    {
        var caseObj = new CredentialingCase
        {
            Provider = new Provider { FirstName = "Arthur", LastName = "Pendelton" },
            VerificationResults = new List<VerificationResult> { new VerificationResult { Status = LicenseStatus.Suspended } },
            SanctionResults = new List<SanctionCheckResult> { new SanctionCheckResult { Status = SanctionStatus.Clear } },
            RiskAssessments = new List<RiskAssessment> { new RiskAssessment { Classification = RiskClassification.Clean } } // Even if risk claimed clean!
        };

        var result = await _agent.ExecuteAsync(caseObj);

        Assert.Equal(CaseStatus.OnHold, result.Status);
        Assert.NotEqual(CaseStatus.Approved, result.Status);
        Assert.Contains("MANDATORY HOLD", result.Recommendation);
    }

    [Fact]
    public async Task ExecuteAsync_SanctionMatch_NeverAutoApproved_SetsOnHold()
    {
        var caseObj = new CredentialingCase
        {
            Provider = new Provider { FirstName = "Bad", LastName = "Actor" },
            VerificationResults = new List<VerificationResult> { new VerificationResult { Status = LicenseStatus.Active } },
            SanctionResults = new List<SanctionCheckResult> { new SanctionCheckResult { Status = SanctionStatus.MatchFound } },
            RiskAssessments = new List<RiskAssessment> { new RiskAssessment { Classification = RiskClassification.Clean } }
        };

        var result = await _agent.ExecuteAsync(caseObj);

        Assert.Equal(CaseStatus.OnHold, result.Status);
        Assert.NotEqual(CaseStatus.Approved, result.Status);
        Assert.Contains("MANDATORY HOLD", result.Recommendation);
    }
}
