using CredentialIQ.Agents;
using CredentialIQ.Api.Middleware;
using CredentialIQ.Core.Interfaces;
using CredentialIQ.Infrastructure.Connectors;
using CredentialIQ.Infrastructure.Llm;
using CredentialIQ.Infrastructure.Persistence;
using CredentialIQ.Infrastructure.Rag;
using CredentialIQ.Infrastructure.Repositories;
using Microsoft.EntityFrameworkCore;
using Microsoft.OpenApi.Models;

var builder = WebApplication.CreateBuilder(args);

// Add Controllers and System services
builder.Services.AddControllers()
    .AddJsonOptions(options =>
    {
        options.JsonSerializerOptions.Converters.Add(new System.Text.Json.Serialization.JsonStringEnumConverter());
    });
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddHttpClient();

// Swagger Documentation setup
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new OpenApiInfo
    {
        Title = "CredentialIQ AI API",
        Version = "v1",
        Description = "Agentic Healthcare Provider Credentialing & Verification Proof-of-Concept API. " +
                      "\n\n**POC Disclaimer**: All results are generated locally using simulated connectors and synthetic policy rules. Final decisions require authorized human review."
    });
});

// Database setup (SQLite)
var connectionString = builder.Configuration.GetConnectionString("DefaultConnection") ?? "Data Source=credentialiq.db";
builder.Services.AddDbContext<CredentialIQDbContext>(options =>
    options.UseSqlite(connectionString));

builder.Services.AddScoped<CredentialingCaseRepository>();

// Connectors registration
builder.Services.AddScoped<IVerificationConnector, MockStateBoardConnector>();
builder.Services.AddScoped<ISanctionConnector, MockSanctionConnector>();

// RAG Repository registration
builder.Services.AddSingleton<IRagRepository, LocalRagRepository>();

// LLM Services registration
builder.Services.AddScoped<DeterministicLanguageModelService>();
builder.Services.AddScoped<GeminiLanguageModelService>();

builder.Services.AddScoped<ILanguageModelService>(sp =>
{
    var config = sp.GetRequiredService<IConfiguration>();
    var providerSetting = config["Llm:Provider"] ?? config["LLM_PROVIDER"] ?? "Deterministic";

    if (providerSetting.Equals("Gemini", StringComparison.OrdinalIgnoreCase))
    {
        return sp.GetRequiredService<GeminiLanguageModelService>();
    }

    return sp.GetRequiredService<DeterministicLanguageModelService>();
});

// Agents registration
builder.Services.AddScoped<ICredentialingAgent, CredentialVerificationAgent>();
builder.Services.AddScoped<ICredentialingAgent, LicenseVerificationAgent>();
builder.Services.AddScoped<ICredentialingAgent, SanctionCheckAgent>();
builder.Services.AddScoped<ICredentialingAgent, RiskAssessmentAgent>();
builder.Services.AddScoped<ICredentialingAgent, WorkflowAgent>();

// Orchestrator registration
builder.Services.AddScoped<CredentialingOrchestrator>();

var app = builder.Build();

// Enable Swagger UI
app.UseSwagger();
app.UseSwaggerUI(c =>
{
    c.SwaggerEndpoint("/swagger/v1/swagger.json", "CredentialIQ AI API v1");
    c.RoutePrefix = "swagger";
});

// Middleware pipeline
app.UseMiddleware<CorrelationIdMiddleware>();
app.UseMiddleware<ProblemDetailsExceptionMiddleware>();

app.UseAuthorization();
app.MapControllers();

// Ensure DB created & RAG policies seeded on startup
using (var scope = app.Services.CreateScope())
{
    var dbContext = scope.ServiceProvider.GetRequiredService<CredentialIQDbContext>();
    dbContext.Database.EnsureCreated();

    var ragRepo = scope.ServiceProvider.GetRequiredService<IRagRepository>();
    await ragRepo.SeedPoliciesAsync();
}

app.Run();

// Make public for WebApplicationFactory in Integration Tests
public partial class Program { }
