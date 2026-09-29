using CredentialIQ.Core.Enums;
using CredentialIQ.Core.Interfaces;
using CredentialIQ.Core.Models;
using Microsoft.Extensions.Logging;

namespace CredentialIQ.Agents;

public class CredentialVerificationAgent : ICredentialingAgent
{
    private readonly ILogger<CredentialVerificationAgent> _logger;

    public CredentialVerificationAgent(ILogger<CredentialVerificationAgent> logger)
    {
        _logger = logger;
    }

    public string AgentName => "CredentialVerificationAgent";

    public Task<CredentialingCase> ExecuteAsync(CredentialingCase credentialingCase, CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("[{AgentName}] Executing for case {CaseId}.", AgentName, credentialingCase.Id);

        var provider = credentialingCase.Provider;
        var validationErrors = new List<string>();

        // Normalize
        provider.Npi = provider.Npi?.Trim() ?? string.Empty;
        provider.FirstName = provider.FirstName?.Trim() ?? string.Empty;
        provider.LastName = provider.LastName?.Trim() ?? string.Empty;
        provider.PrimaryState = provider.PrimaryState?.Trim().ToUpperInvariant() ?? string.Empty;
        provider.LicenseNumber = provider.LicenseNumber?.Trim() ?? string.Empty;
        provider.ProviderType = provider.ProviderType?.Trim() ?? string.Empty;

        // Validate
        if (string.IsNullOrWhiteSpace(provider.Npi) || provider.Npi.Length != 10 || !provider.Npi.All(char.IsDigit))
        {
            validationErrors.Add("Invalid NPI format: NPI must be exactly 10 digits.");
        }

        if (string.IsNullOrWhiteSpace(provider.FirstName) || string.IsNullOrWhiteSpace(provider.LastName))
        {
            validationErrors.Add("Missing mandatory provider name fields.");
        }

        if (string.IsNullOrWhiteSpace(provider.PrimaryState) || provider.PrimaryState.Length != 2)
        {
            validationErrors.Add("Invalid state abbreviation: State must be a 2-letter code.");
        }

        if (string.IsNullOrWhiteSpace(provider.LicenseNumber))
        {
            validationErrors.Add("Missing mandatory license number.");
        }

        if (string.IsNullOrWhiteSpace(provider.ProviderType))
        {
            validationErrors.Add("Missing mandatory provider type.");
        }

        bool isValid = !validationErrors.Any();
        string outcome = isValid ? "PASS" : "FAIL";
        string explanation = isValid
            ? "Provider intake verification successful. NPI, state, name, and license formatted correctly."
            : $"Provider intake verification failed validation rules: {string.Join(" ", validationErrors)}";

        credentialingCase.Status = isValid ? CaseStatus.Verifying : CaseStatus.OnHold;

        credentialingCase.AuditEvents.Add(new AuditEvent
        {
            CaseId = credentialingCase.Id,
            Source = AgentName,
            Action = "ValidateProviderFields",
            Outcome = outcome,
            UtcTimestamp = DateTime.UtcNow,
            CorrelationId = credentialingCase.CorrelationId,
            EvidenceReference = $"AUDIT-INTAKE-{Guid.NewGuid():N}",
            IsSimulated = true,
            HumanReadableExplanation = explanation
        });

        return Task.FromResult(credentialingCase);
    }
}
