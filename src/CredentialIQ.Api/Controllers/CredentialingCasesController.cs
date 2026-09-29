using CredentialIQ.Agents;
using CredentialIQ.Core.DTOs;
using CredentialIQ.Core.Enums;
using CredentialIQ.Core.Models;
using CredentialIQ.Infrastructure.Repositories;
using Microsoft.AspNetCore.Mvc;

namespace CredentialIQ.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
[Produces("application/json")]
public class CredentialingCasesController : ControllerBase
{
    private readonly CredentialingCaseRepository _repository;
    private readonly CredentialingOrchestrator _orchestrator;
    private readonly ILogger<CredentialingCasesController> _logger;

    public CredentialingCasesController(
        CredentialingCaseRepository repository,
        CredentialingOrchestrator orchestrator,
        ILogger<CredentialingCasesController> logger)
    {
        _repository = repository;
        _orchestrator = orchestrator;
        _logger = logger;
    }

    /// <summary>
    /// Creates and executes a new provider credentialing case through the 5-agent pipeline.
    /// </summary>
    [HttpPost]
    [ProducesResponseType(typeof(CredentialingCaseResponse), StatusCodes.Status201Created)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status400BadRequest)]
    public async Task<IActionResult> CreateCase([FromBody] CreateCredentialingCaseRequest request, CancellationToken cancellationToken)
    {
        if (!ModelState.IsValid)
        {
            return BadRequest(ModelState);
        }

        var correlationId = HttpContext.Items["X-Correlation-ID"]?.ToString() ?? Guid.NewGuid().ToString("N");

        var provider = new Provider
        {
            Npi = request.Npi,
            FirstName = request.FirstName,
            LastName = request.LastName,
            ProviderType = request.ProviderType,
            PrimaryState = request.PrimaryState,
            LicenseNumber = request.LicenseNumber,
            DateOfBirth = request.DateOfBirth,
            Email = request.Email,
            Phone = request.Phone,
            Address = request.Address
        };

        var credentialingCase = new CredentialingCase
        {
            CorrelationId = correlationId,
            Provider = provider,
            ProviderId = provider.Id,
            Status = CaseStatus.Intake,
            CreatedAtUtc = DateTime.UtcNow,
            UpdatedAtUtc = DateTime.UtcNow
        };

        // Save initial intake case
        await _repository.SaveCaseAsync(credentialingCase, cancellationToken);

        // Execute orchestrator pipeline
        credentialingCase = await _orchestrator.ProcessCaseAsync(credentialingCase, cancellationToken);

        // Save completed case state
        await _repository.SaveCaseAsync(credentialingCase, cancellationToken);

        var response = MapToResponse(credentialingCase);
        return CreatedAtAction(nameof(GetCaseById), new { id = response.Id }, response);
    }

    /// <summary>
    /// Retrieves a credentialing case by ID.
    /// </summary>
    [HttpGet("{id:guid}")]
    [ProducesResponseType(typeof(CredentialingCaseResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> GetCaseById(Guid id, CancellationToken cancellationToken)
    {
        var credentialingCase = await _repository.GetByIdAsync(id, cancellationToken);
        if (credentialingCase == null)
        {
            return NotFound(new ProblemDetails
            {
                Status = StatusCodes.Status404NotFound,
                Title = "Credentialing case not found.",
                Detail = $"No case found with ID {id}."
            });
        }

        return Ok(MapToResponse(credentialingCase));
    }

    /// <summary>
    /// Retrieves structured evidence and full audit trail for a case.
    /// </summary>
    [HttpGet("{id:guid}/evidence")]
    [ProducesResponseType(typeof(EvidenceAuditResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> GetCaseEvidence(Guid id, CancellationToken cancellationToken)
    {
        var credentialingCase = await _repository.GetByIdAsync(id, cancellationToken);
        if (credentialingCase == null)
        {
            return NotFound(new ProblemDetails
            {
                Status = StatusCodes.Status404NotFound,
                Title = "Credentialing case not found.",
                Detail = $"No case found with ID {id}."
            });
        }

        var response = new EvidenceAuditResponse
        {
            CaseId = credentialingCase.Id,
            CorrelationId = credentialingCase.CorrelationId,
            VerificationResults = credentialingCase.VerificationResults,
            SanctionResults = credentialingCase.SanctionResults,
            RiskAssessments = credentialingCase.RiskAssessments,
            WorkflowDecisions = credentialingCase.WorkflowDecisions,
            AuditEvents = credentialingCase.AuditEvents.OrderBy(a => a.UtcTimestamp).ToList()
        };

        return Ok(response);
    }

    /// <summary>
    /// Submits a manual human reviewer override decision for a case.
    /// </summary>
    [HttpPost("{id:guid}/override")]
    [ProducesResponseType(typeof(CredentialingCaseResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    public async Task<IActionResult> OverrideCase(Guid id, [FromBody] ManualOverrideRequest request, CancellationToken cancellationToken)
    {
        var credentialingCase = await _repository.GetByIdAsync(id, cancellationToken);
        if (credentialingCase == null)
        {
            return NotFound(new ProblemDetails
            {
                Status = StatusCodes.Status404NotFound,
                Title = "Credentialing case not found.",
                Detail = $"No case found with ID {id}."
            });
        }

        if (string.IsNullOrWhiteSpace(request.ReviewerName) || string.IsNullOrWhiteSpace(request.Reason))
        {
            return BadRequest(new ProblemDetails
            {
                Status = StatusCodes.Status400BadRequest,
                Title = "Invalid override request.",
                Detail = "ReviewerName and Reason are required for human override."
            });
        }

        var previousStatus = credentialingCase.Status;
        credentialingCase.Status = request.TargetStatus;
        credentialingCase.UpdatedAtUtc = DateTime.UtcNow;

        var overrideDecision = new WorkflowDecision
        {
            CaseId = credentialingCase.Id,
            Status = previousStatus,
            TargetStatus = request.TargetStatus,
            RecommendedAction = $"HUMAN OVERRIDE: Status manually updated to {request.TargetStatus} by {request.ReviewerName}.",
            CaseSummary = $"MANUAL OVERRIDE: Original agent recommendation overrode by authorized human reviewer {request.ReviewerName}. Reason: {request.Reason}",
            RecommendedAtUtc = DateTime.UtcNow,
            CorrelationId = credentialingCase.CorrelationId,
            IsHumanOverride = true,
            OverriddenBy = request.ReviewerName,
            OverrideReason = request.Reason,
            OverriddenAtUtc = DateTime.UtcNow
        };

        credentialingCase.WorkflowDecisions.Add(overrideDecision);

        credentialingCase.AuditEvents.Add(new AuditEvent
        {
            CaseId = credentialingCase.Id,
            Source = "HumanReviewer",
            Action = "ManualOverrideDecision",
            Outcome = request.TargetStatus.ToString(),
            UtcTimestamp = DateTime.UtcNow,
            CorrelationId = credentialingCase.CorrelationId,
            EvidenceReference = $"OVERRIDE-{overrideDecision.Id:N}",
            IsSimulated = false,
            HumanReadableExplanation = $"Human reviewer '{request.ReviewerName}' overrode case status from {previousStatus} to {request.TargetStatus}. Reason: {request.Reason}"
        });

        await _repository.SaveCaseAsync(credentialingCase, cancellationToken);

        return Ok(MapToResponse(credentialingCase));
    }

    private static CredentialingCaseResponse MapToResponse(CredentialingCase c)
    {
        return new CredentialingCaseResponse
        {
            Id = c.Id,
            CorrelationId = c.CorrelationId,
            ProviderId = c.ProviderId,
            Provider = c.Provider,
            Status = c.Status,
            RiskClassification = c.RiskClassification,
            Recommendation = c.Recommendation,
            CreatedAtUtc = c.CreatedAtUtc,
            UpdatedAtUtc = c.UpdatedAtUtc,
            LatestVerificationResult = c.VerificationResults.LastOrDefault(),
            LatestSanctionResult = c.SanctionResults.LastOrDefault(),
            LatestRiskAssessment = c.RiskAssessments.LastOrDefault(),
            LatestWorkflowDecision = c.WorkflowDecisions.LastOrDefault()
        };
    }
}
