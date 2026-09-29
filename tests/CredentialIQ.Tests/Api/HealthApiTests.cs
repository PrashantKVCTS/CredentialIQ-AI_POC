using System.Net;
using System.Net.Http.Json;
using CredentialIQ.Core.DTOs;
using Xunit;

namespace CredentialIQ.Tests.Api;

public class HealthApiTests : IClassFixture<CustomWebApplicationFactory>
{
    private readonly HttpClient _client;
    private static readonly System.Text.Json.JsonSerializerOptions JsonOptions = new System.Text.Json.JsonSerializerOptions
    {
        PropertyNameCaseInsensitive = true,
        Converters = { new System.Text.Json.Serialization.JsonStringEnumConverter() }
    };

    public HealthApiTests(CustomWebApplicationFactory factory)
    {
        _client = factory.CreateClient();
    }

    [Fact]
    public async Task GetHealth_Returns200OK_WithHealthyStatus()
    {
        var response = await _client.GetAsync("/health");

        Assert.Equal(HttpStatusCode.OK, response.StatusCode);
        var health = await response.Content.ReadFromJsonAsync<HealthCheckResponse>(JsonOptions);
        Assert.NotNull(health);
        Assert.Equal("Healthy", health.Status);
        Assert.True(health.Components.ContainsKey("Database"));
        Assert.True(health.Components.ContainsKey("LocalRagRepository"));
    }

    [Fact]
    public async Task GetSystemInfo_Returns200OK_WithSystemMetadata()
    {
        var response = await _client.GetAsync("/api/system/info");

        Assert.Equal(HttpStatusCode.OK, response.StatusCode);
        var info = await response.Content.ReadFromJsonAsync<SystemInfoResponse>(JsonOptions);
        Assert.NotNull(info);
        Assert.Equal("CredentialIQ AI", info.ApplicationName);
        Assert.Equal("Deterministic", info.LlmProvider);
        Assert.True(info.SyntheticDataEnabled);
    }
}
