using Microsoft.AspNetCore.Mvc;

namespace CredentialIQ.Api.Middleware;

public class ProblemDetailsExceptionMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<ProblemDetailsExceptionMiddleware> _logger;

    public ProblemDetailsExceptionMiddleware(RequestDelegate next, ILogger<ProblemDetailsExceptionMiddleware> logger)
    {
        _next = next;
        _logger = logger;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        try
        {
            await _next(context);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Unhandled exception captured by ProblemDetailsExceptionMiddleware.");

            var correlationId = context.Items["X-Correlation-ID"]?.ToString() ?? Guid.NewGuid().ToString("N");

            var problemDetails = new ProblemDetails
            {
                Status = StatusCodes.Status500InternalServerError,
                Title = "An error occurred while processing your request.",
                Detail = "An unexpected error occurred. Please refer to the correlation ID when contacting support.",
                Instance = context.Request.Path,
                Extensions =
                {
                    ["correlationId"] = correlationId,
                    ["timestamp"] = DateTime.UtcNow
                }
            };

            context.Response.ContentType = "application/problem+json";
            context.Response.StatusCode = StatusCodes.Status500InternalServerError;

            await context.Response.WriteAsJsonAsync(problemDetails);
        }
    }
}
