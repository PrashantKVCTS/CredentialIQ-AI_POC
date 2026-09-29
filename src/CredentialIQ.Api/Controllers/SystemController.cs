using CredentialIQ.Core.DTOs;
using CredentialIQ.Core.Interfaces;
using Microsoft.AspNetCore.Mvc;

namespace CredentialIQ.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
[Produces("application/json")]
public class SystemController : ControllerBase
{
    private readonly ILanguageModelService _llmService;
    private readonly IWebHostEnvironment _environment;

    public SystemController(ILanguageModelService llmService, IWebHostEnvironment environment)
    {
        _llmService = llmService;
        _environment = environment;
    }

    /// <summary>
    /// Returns system information, active LLM provider, and environment metadata without exposing secrets.
    /// </summary>
    [HttpGet("info")]
    [ProducesResponseType(typeof(SystemInfoResponse), StatusCodes.Status200OK)]
    public IActionResult GetSystemInfo()
    {
        var response = new SystemInfoResponse
        {
            ApplicationName = "CredentialIQ AI",
            Version = "1.0.0-poc",
            Environment = _environment.EnvironmentName,
            LlmProvider = _llmService.ProviderName,
            ConnectorMode = "MockPrimarySource",
            SyntheticDataEnabled = true,
            Disclaimer = "CredentialIQ AI Proof of Concept - Local Profile. Results require authorized human review."
        };

        return Ok(response);
    }
}
