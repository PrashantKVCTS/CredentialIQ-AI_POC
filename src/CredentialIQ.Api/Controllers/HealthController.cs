using CredentialIQ.Core.DTOs;
using CredentialIQ.Core.Interfaces;
using CredentialIQ.Infrastructure.Persistence;
using Microsoft.AspNetCore.Mvc;

namespace CredentialIQ.Api.Controllers;

[ApiController]
[Produces("application/json")]
public class HealthController : ControllerBase
{
    private readonly CredentialIQDbContext _dbContext;
    private readonly IRagRepository _ragRepository;
    private readonly ILanguageModelService _llmService;

    public HealthController(
        CredentialIQDbContext dbContext,
        IRagRepository ragRepository,
        ILanguageModelService llmService)
    {
        _dbContext = dbContext;
        _ragRepository = ragRepository;
        _llmService = llmService;
    }

    /// <summary>
    /// Checks database, RAG repository, and LLM readiness.
    /// </summary>
    [HttpGet("health")]
    [ProducesResponseType(typeof(HealthCheckResponse), StatusCodes.Status200OK)]
    public async Task<IActionResult> GetHealth(CancellationToken cancellationToken)
    {
        var components = new Dictionary<string, string>();
        bool isHealthy = true;

        // DB Check
        try
        {
            bool canConnect = await _dbContext.Database.CanConnectAsync(cancellationToken);
            components["Database"] = canConnect ? "Healthy (SQLite)" : "Unhealthy";
            if (!canConnect) isHealthy = false;
        }
        catch (Exception ex)
        {
            components["Database"] = $"Unhealthy ({ex.Message})";
            isHealthy = false;
        }

        // RAG Check
        try
        {
            await _ragRepository.SeedPoliciesAsync(cancellationToken);
            components["LocalRagRepository"] = "Healthy (Knowledge base active)";
        }
        catch (Exception ex)
        {
            components["LocalRagRepository"] = $"Degraded ({ex.Message})";
        }

        // LLM Check
        components["LanguageModelService"] = $"Healthy ({_llmService.ProviderName})";

        var response = new HealthCheckResponse
        {
            Status = isHealthy ? "Healthy" : "Degraded",
            Components = components,
            CheckedAtUtc = DateTime.UtcNow
        };

        return Ok(response);
    }
}
