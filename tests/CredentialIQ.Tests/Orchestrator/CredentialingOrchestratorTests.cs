using CredentialIQ.Agents;
using CredentialIQ.Core.Enums;
using CredentialIQ.Core.Interfaces;
using CredentialIQ.Core.Models;
using CredentialIQ.Infrastructure.Connectors;
using CredentialIQ.Infrastructure.Llm;
using CredentialIQ.Infrastructure.Rag;
using Microsoft.Extensions.Logging.Abstractions;
using Xunit;

namespace CredentialIQ.Tests.Orchestrator;

public class CredentialingOrchestratorTests
{
    private readonly CredentialingOrchestrator _orchestrator;

    public CredentialingOrchestratorTests()
    {
        var valAgent = new CredentialVerificationAgent(NullLogger<CredentialVerificationAgent>.Instance);
        var licAgent = new LicenseVerificationAgent(new MockStateBoardConnector(), NullLogger<LicenseVerificationAgent>.Instance);
        var sancAgent = new SanctionCheckAgent(new MockSanctionConnector(), NullLogger<SanctionCheckAgent>.Instance);
        var ragRepo = new LocalRagRepository(NullLogger<LocalRagRepository>.Instance);
        var llm = new DeterministicLanguageModelService(NullLogger<DeterministicLanguageModelService>.Instance);
        var riskAgent = new RiskAssessmentAgent(ragRepo, llm, NullLogger<RiskAssessmentAgent>.Instance);
        var wfAgent = new WorkflowAgent(NullLogger<WorkflowAgent>.Instance);

        var agents = new List<ICredentialingAgent> { valAgent, licAgent, sancAgent, riskAgent, wfAgent };

        _orchestrator = new CredentialingOrchestrator(agents, NullLogger<CredentialingOrchestrator>.Instance);
    }

    [Fact]
    public async Task ProcessCaseAsync_RunsAllFiveAgents_InOrder_WithTelemetry()
    {
        var caseObj = new CredentialingCase
        {
            Provider = new Provider
            {
                Npi = "1234567890",
                FirstName = "Jane",
                LastName = "Doe",
                PrimaryState = "CA",
                LicenseNumber = "C12345",
                ProviderType = "Medical Doctor"
            }
        };

        var result = await _orchestrator.ProcessCaseAsync(caseObj);

        Assert.Equal(CaseStatus.Approved, result.Status);
        Assert.Equal(RiskClassification.Clean, result.RiskClassification);
        Assert.Single(result.VerificationResults);
        Assert.Single(result.SanctionResults);
        Assert.Single(result.RiskAssessments);
        Assert.Single(result.WorkflowDecisions);

        // Check audit events count (1 for intake validation, 1 for lic, 1 for sanc, 1 for risk, 1 for wf)
        Assert.Equal(5, result.AuditEvents.Count);

        // Telemetry recorded
        Assert.True(result.Metadata.ContainsKey("Telemetry:CredentialVerificationAgent:DurationMs"));
        Assert.True(result.Metadata.ContainsKey("Telemetry:LicenseVerificationAgent:DurationMs"));
        Assert.True(result.Metadata.ContainsKey("Telemetry:SanctionCheckAgent:DurationMs"));
        Assert.True(result.Metadata.ContainsKey("Telemetry:RiskAssessmentAgent:DurationMs"));
        Assert.True(result.Metadata.ContainsKey("Telemetry:WorkflowAgent:DurationMs"));
    }
}
