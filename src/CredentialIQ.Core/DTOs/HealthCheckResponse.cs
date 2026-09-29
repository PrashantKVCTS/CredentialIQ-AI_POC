namespace CredentialIQ.Core.DTOs;

public class HealthCheckResponse
{
    public string Status { get; set; } = "Healthy"; // Healthy, Degraded, Unhealthy
    public Dictionary<string, string> Components { get; set; } = new();
    public DateTime CheckedAtUtc { get; set; } = DateTime.UtcNow;
}
