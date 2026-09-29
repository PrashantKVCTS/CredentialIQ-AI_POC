namespace CredentialIQ.Core.DTOs;

public class SystemInfoResponse
{
    public string ApplicationName { get; set; } = "CredentialIQ AI";
    public string Version { get; set; } = "1.0.0-poc";
    public string Environment { get; set; } = "Development";
    public string LlmProvider { get; set; } = "Deterministic";
    public string ConnectorMode { get; set; } = "MockPrimarySource";
    public bool SyntheticDataEnabled { get; set; } = true;
    public string Disclaimer { get; set; } = "Local POC Mode - No real live credentials or PII used.";
}
