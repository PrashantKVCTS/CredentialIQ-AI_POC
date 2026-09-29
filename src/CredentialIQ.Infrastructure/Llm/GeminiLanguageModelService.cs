using System.Net.Http.Json;
using System.Text;
using System.Text.Json;
using CredentialIQ.Core.Enums;
using CredentialIQ.Core.Interfaces;
using CredentialIQ.Core.Models;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;

namespace CredentialIQ.Infrastructure.Llm;

public class GeminiLanguageModelService : ILanguageModelService
{
    private readonly IHttpClientFactory _httpClientFactory;
    private readonly IConfiguration _configuration;
    private readonly ILogger<GeminiLanguageModelService> _logger;
    private readonly DeterministicLanguageModelService _fallbackService;

    public GeminiLanguageModelService(
        IHttpClientFactory httpClientFactory,
        IConfiguration configuration,
        ILogger<GeminiLanguageModelService> logger,
        DeterministicLanguageModelService fallbackService)
    {
        _httpClientFactory = httpClientFactory;
        _configuration = configuration;
        _logger = logger;
        _fallbackService = fallbackService;
    }

    public string ProviderName => "GeminiLlmAdapter";

    public async Task<RiskAssessment> AssessRiskAsync(
        CredentialingCase credentialingCase,
        List<PolicyChunk> retrievedPolicies,
        CancellationToken cancellationToken = default)
    {
        var apiKey = _configuration["GEMINI_API_KEY"] ?? _configuration["Gemini:ApiKey"];

        if (string.IsNullOrWhiteSpace(apiKey))
        {
            _logger.LogWarning("Gemini API key is not configured. Falling back to deterministic rules risk assessment.");
            return await _fallbackService.AssessRiskAsync(credentialingCase, retrievedPolicies, cancellationToken);
        }

        try
        {
            var endpoint = _configuration["Gemini:Endpoint"] ?? "https://generativelanguage.googleapis.com/v1beta/models/";
            var model = _configuration["Gemini:Model"] ?? "gemini-2.5-flash";
            var requestUri = $"{endpoint.TrimEnd('/')}/{model}:generateContent?key={apiKey}";

            var prompt = BuildSanitizedPrompt(credentialingCase, retrievedPolicies);

            var requestBody = new
            {
                contents = new[]
                {
                    new
                    {
                        parts = new[]
                        {
                            new { text = prompt }
                        }
                    }
                },
                generationConfig = new
                {
                    temperature = 0.1,
                    responseMimeType = "application/json"
                }
            };

            var client = _httpClientFactory.CreateClient("GeminiClient");
            client.Timeout = TimeSpan.FromSeconds(15);

            _logger.LogInformation("Sending risk assessment prompt to Gemini LLM endpoint.");
            var response = await client.PostAsJsonAsync(requestUri, requestBody, cancellationToken);

            if (!response.IsSuccessStatusCode)
            {
                _logger.LogWarning("Gemini API returned status code {StatusCode}. Falling back to deterministic service.", response.StatusCode);
                return await _fallbackService.AssessRiskAsync(credentialingCase, retrievedPolicies, cancellationToken);
            }

            var responseJson = await response.Content.ReadAsStringAsync(cancellationToken);
            var assessment = ParseAndValidateGeminiResponse(responseJson, credentialingCase, retrievedPolicies);

            if (assessment != null)
            {
                return assessment;
            }

            _logger.LogWarning("Gemini response parsing/validation failed. Falling back to deterministic service.");
            return await _fallbackService.AssessRiskAsync(credentialingCase, retrievedPolicies, cancellationToken);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Exception occurred during Gemini API call. Falling back to deterministic service.");
            return await _fallbackService.AssessRiskAsync(credentialingCase, retrievedPolicies, cancellationToken);
        }
    }

    private static string BuildSanitizedPrompt(CredentialingCase credentialingCase, List<PolicyChunk> retrievedPolicies)
    {
        var provider = credentialingCase.Provider;
        var latestLic = credentialingCase.VerificationResults.LastOrDefault();
        var latestSanc = credentialingCase.SanctionResults.LastOrDefault();

        var sb = new StringBuilder();
        sb.AppendLine("You are a medical credentialing risk assessment assistant. Analyze the following provider findings grounded strictly in the provided policy chunks.");
        sb.AppendLine("Return a valid JSON object matching this schema:");
        sb.AppendLine(@"{
  ""classification"": ""Clean"" | ""Exception"" | ""Hold"",
  ""confidenceScore"": number (0.0 to 1.0),
  ""rationale"": ""string explaining groundings"",
  ""appliedRuleReferences"": [""string""]
}");

        sb.AppendLine("\n--- RETRIEVED POLICIES ---");
        foreach (var policy in retrievedPolicies)
        {
            sb.AppendLine($"[ID: {policy.Id} | RuleRef: {policy.RuleReference}] {policy.Content}");
        }

        sb.AppendLine("\n--- PROVIDER FINDINGS (PII Redacted) ---");
        sb.AppendLine($"Provider Type: {provider.ProviderType}");
        sb.AppendLine($"State: {provider.PrimaryState}");
        sb.AppendLine($"License Status: {latestLic?.Status.ToString() ?? "Unknown"}");
        sb.AppendLine($"Sanction Screening Status: {latestSanc?.Status.ToString() ?? "Unknown"}");
        sb.AppendLine($"License Explanation: {latestLic?.HumanReadableExplanation ?? "None"}");
        sb.AppendLine($"Sanction Explanation: {latestSanc?.HumanReadableExplanation ?? "None"}");

        sb.AppendLine("\nEvaluate risk classification based strictly on policies. Never invent policy references.");

        return sb.ToString();
    }

    private RiskAssessment? ParseAndValidateGeminiResponse(
        string responseJson, CredentialingCase credentialingCase, List<PolicyChunk> retrievedPolicies)
    {
        try
        {
            using var doc = JsonDocument.Parse(responseJson);
            var root = doc.RootElement;
            var text = root.GetProperty("candidates")[0]
                           .GetProperty("content")
                           .GetProperty("parts")[0]
                           .GetProperty("text")
                           .GetString();

            if (string.IsNullOrWhiteSpace(text)) return null;

            using var parsedResult = JsonDocument.Parse(text);
            var resultRoot = parsedResult.RootElement;

            var classificationStr = resultRoot.GetProperty("classification").GetString();
            if (!Enum.TryParse<RiskClassification>(classificationStr, true, out var classification))
            {
                return null;
            }

            var confidence = resultRoot.TryGetProperty("confidenceScore", out var confProp) ? confProp.GetDouble() : 0.9;
            var rationale = resultRoot.TryGetProperty("rationale", out var ratProp) ? ratProp.GetString() ?? "" : "";
            var rules = new List<string>();

            if (resultRoot.TryGetProperty("appliedRuleReferences", out var rulesProp) && rulesProp.ValueKind == JsonValueKind.Array)
            {
                foreach (var elem in rulesProp.EnumerateArray())
                {
                    var r = elem.GetString();
                    if (!string.IsNullOrWhiteSpace(r)) rules.Add(r);
                }
            }

            // Ensure valid policy rule references exist
            if (!rules.Any())
            {
                rules.Add(retrievedPolicies.FirstOrDefault()?.RuleReference ?? "NCQA-CR1-LIC");
            }

            return new RiskAssessment
            {
                CaseId = credentialingCase.Id,
                Classification = classification,
                ConfidenceScore = confidence,
                Rationale = rationale,
                AppliedRuleReferences = rules,
                RetrievedSourceIds = retrievedPolicies.Select(p => p.Id).ToList(),
                AssessedAtUtc = DateTime.UtcNow,
                CorrelationId = credentialingCase.CorrelationId,
                EvaluatedBy = ProviderName
            };
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Failed to parse Gemini response payload.");
            return null;
        }
    }
}
