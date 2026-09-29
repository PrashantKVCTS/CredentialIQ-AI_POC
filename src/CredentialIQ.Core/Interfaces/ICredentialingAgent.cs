using CredentialIQ.Core.Models;

namespace CredentialIQ.Core.Interfaces;

public interface ICredentialingAgent
{
    string AgentName { get; }
    Task<CredentialingCase> ExecuteAsync(CredentialingCase credentialingCase, CancellationToken cancellationToken = default);
}
