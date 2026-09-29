using System.Net;
using System.Net.Http.Json;
using CredentialIQ.Core.DTOs;
using CredentialIQ.Core.Enums;
using CredentialIQ.Infrastructure.Persistence;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using Xunit;

namespace CredentialIQ.Tests.Api;

public class CustomWebApplicationFactory : WebApplicationFactory<Program>
{
    private readonly string _dbName = Guid.NewGuid().ToString("N");

    protected override void ConfigureWebHost(IWebHostBuilder builder)
    {
        builder.ConfigureServices(services =>
        {
            var descriptor = services.SingleOrDefault(
                d => d.ServiceType == typeof(DbContextOptions<CredentialIQDbContext>));

            if (descriptor != null)
            {
                services.Remove(descriptor);
            }

            services.AddDbContext<CredentialIQDbContext>(options =>
            {
                options.UseInMemoryDatabase(_dbName);
            });
        });
    }
}

public class CredentialingCasesApiTests : IClassFixture<CustomWebApplicationFactory>
{
    private readonly HttpClient _client;
    private static readonly System.Text.Json.JsonSerializerOptions JsonOptions = new System.Text.Json.JsonSerializerOptions
    {
        PropertyNameCaseInsensitive = true,
        Converters = { new System.Text.Json.Serialization.JsonStringEnumConverter() }
    };

    public CredentialingCasesApiTests(CustomWebApplicationFactory factory)
    {
        _client = factory.CreateClient();
    }

    [Fact]
    public async Task PostCredentialingCase_CleanProvider_Returns201Created_AndApprovedStatus()
    {
        var request = new CreateCredentialingCaseRequest
        {
            Npi = "1234567890",
            FirstName = "Jane",
            LastName = "Doe",
            ProviderType = "Medical Doctor",
            PrimaryState = "CA",
            LicenseNumber = "C12345"
        };

        var response = await _client.PostAsJsonAsync("/api/credentialingcases", request);

        Assert.Equal(HttpStatusCode.Created, response.StatusCode);
        var caseResp = await response.Content.ReadFromJsonAsync<CredentialingCaseResponse>(JsonOptions);
        Assert.NotNull(caseResp);
        Assert.Equal(CaseStatus.Approved, caseResp.Status);
        Assert.Equal(RiskClassification.Clean, caseResp.RiskClassification);
    }

    [Fact]
    public async Task PostCredentialingCase_ExceptionProvider_Returns201Created_AndCommitteeReviewStatus()
    {
        var request = new CreateCredentialingCaseRequest
        {
            Npi = "9876543210",
            FirstName = "Robert",
            LastName = "Smith",
            ProviderType = "Medical Doctor",
            PrimaryState = "CA",
            LicenseNumber = "EXP-998877"
        };

        var response = await _client.PostAsJsonAsync("/api/credentialingcases", request);

        Assert.Equal(HttpStatusCode.Created, response.StatusCode);
        var caseResp = await response.Content.ReadFromJsonAsync<CredentialingCaseResponse>(JsonOptions);
        Assert.NotNull(caseResp);
        Assert.Equal(CaseStatus.CommitteeReview, caseResp.Status);
        Assert.Equal(RiskClassification.Exception, caseResp.RiskClassification);
    }

    [Fact]
    public async Task PostCredentialingCase_HoldProvider_Returns201Created_AndOnHoldStatus()
    {
        var request = new CreateCredentialingCaseRequest
        {
            Npi = "5556667778",
            FirstName = "Arthur",
            LastName = "Pendelton",
            ProviderType = "Nurse Practitioner",
            PrimaryState = "NY",
            LicenseNumber = "SUSP-112233"
        };

        var response = await _client.PostAsJsonAsync("/api/credentialingcases", request);

        Assert.Equal(HttpStatusCode.Created, response.StatusCode);
        var caseResp = await response.Content.ReadFromJsonAsync<CredentialingCaseResponse>(JsonOptions);
        Assert.NotNull(caseResp);
        Assert.Equal(CaseStatus.OnHold, caseResp.Status);
        Assert.Equal(RiskClassification.Hold, caseResp.RiskClassification);
    }

    [Fact]
    public async Task GetEvidenceAndOverride_Flow_Succeeds()
    {
        // 1. Create
        var createRequest = new CreateCredentialingCaseRequest
        {
            Npi = "1234567890",
            FirstName = "Jane",
            LastName = "Doe",
            ProviderType = "Medical Doctor",
            PrimaryState = "CA",
            LicenseNumber = "C12345"
        };

        var createResponse = await _client.PostAsJsonAsync("/api/credentialingcases", createRequest);
        var caseResp = await createResponse.Content.ReadFromJsonAsync<CredentialingCaseResponse>(JsonOptions);
        Assert.NotNull(caseResp);

        // 2. Get Evidence
        var evidenceResponse = await _client.GetAsync($"/api/credentialingcases/{caseResp.Id}/evidence");
        Assert.Equal(HttpStatusCode.OK, evidenceResponse.StatusCode);
        var evidence = await evidenceResponse.Content.ReadFromJsonAsync<EvidenceAuditResponse>(JsonOptions);
        Assert.NotNull(evidence);
        Assert.NotEmpty(evidence.AuditEvents);

        // 3. Post Override
        var overrideReq = new ManualOverrideRequest
        {
            TargetStatus = CaseStatus.Approved,
            ReviewerName = "Dr. Alice Vance (Committee Chair)",
            Reason = "Manually reviewed primary source verification documents."
        };

        var overrideResp = await _client.PostAsJsonAsync($"/api/credentialingcases/{caseResp.Id}/override", overrideReq);
        Assert.Equal(HttpStatusCode.OK, overrideResp.StatusCode);
        var updatedCase = await overrideResp.Content.ReadFromJsonAsync<CredentialingCaseResponse>(JsonOptions);
        Assert.NotNull(updatedCase);
        Assert.Equal(CaseStatus.Approved, updatedCase.Status);
    }
}
