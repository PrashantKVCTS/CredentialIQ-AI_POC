using CredentialIQ.Core.Enums;
using CredentialIQ.Core.Interfaces;
using CredentialIQ.Core.Models;
using Microsoft.Extensions.Logging;

namespace CredentialIQ.Agents;

public class LicenseVerificationAgent : ICredentialingAgent
{
    private readonly IVerificationConnector _verificationConnector;
    private readonly ILogger<LicenseVerificationAgent> _logger;

    public LicenseVerificationAgent(IVerificationConnector verificationConnector, ILogger<LicenseVerificationAgent> logger)
    {
        _verificationConnector = verificationConnector;
        _logger = logger;
    }

    public string AgentName => "LicenseVerificationAgent";

    public async Task<CredentialingCase> ExecuteAsync(CredentialingCase credentialingCase, CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("[{AgentName}] Executing license verification for case {CaseId}.", AgentName, credentialingCase.Id);

        var verificationResult = await _verificationConnector.VerifyLicenseAsync(credentialingCase.Provider, cancellationToken);
        verificationResult.CaseId = credentialingCase.Id;
        verificationResult.CorrelationId = credentialingCase.CorrelationId;

        credentialingCase.VerificationResults.Add(verificationResult);
        credentialingCase.Status = CaseStatus.SanctionScreening;

        credentialingCase.AuditEvents.Add(new AuditEvent
        {
            CaseId = credentialingCase.Id,
            Source = AgentName,
            Action = "VerifyStateBoardLicense",
            Outcome = verificationResult.Status.ToString(),
            UtcTimestamp = DateTime.UtcNow,
            CorrelationId = credentialingCase.CorrelationId,
            EvidenceReference = verificationResult.EvidenceReference,
            IsSimulated = verificationResult.IsSimulated,
            HumanReadableExplanation = verificationResult.HumanReadableExplanation
        });

        return credentialingCase;
    }
}
