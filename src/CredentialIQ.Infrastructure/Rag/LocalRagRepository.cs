using System.Text.Json;
using CredentialIQ.Core.Interfaces;
using CredentialIQ.Core.Models;
using Microsoft.Extensions.Logging;

namespace CredentialIQ.Infrastructure.Rag;

public class LocalRagRepository : IRagRepository
{
    private readonly List<PolicyChunk> _policies = new();
    private readonly ILogger<LocalRagRepository> _logger;
    private readonly string _knowledgeBasePath;

    public LocalRagRepository(ILogger<LocalRagRepository> logger, string? knowledgeBasePath = null)
    {
        _logger = logger;
        _knowledgeBasePath = knowledgeBasePath ?? Path.Combine(Directory.GetCurrentDirectory(), "knowledge");
    }

    public async Task SeedPoliciesAsync(CancellationToken cancellationToken = default)
    {
        if (_policies.Any()) return;

        try
        {
            if (!Directory.Exists(_knowledgeBasePath))
            {
                _logger.LogWarning("Knowledge base path {Path} not found. Creating fallback in-memory synthetic policies.", _knowledgeBasePath);
                AddFallbackPolicies();
                return;
            }

            var jsonFiles = Directory.GetFiles(_knowledgeBasePath, "*.json", SearchOption.AllDirectories);
            var options = new JsonSerializerOptions { PropertyNameCaseInsensitive = true };

            foreach (var file in jsonFiles)
            {
                var content = await File.ReadAllTextAsync(file, cancellationToken);
                var chunks = JsonSerializer.Deserialize<List<PolicyChunk>>(content, options);
                if (chunks != null)
                {
                    _policies.AddRange(chunks);
                }
            }

            _logger.LogInformation("Successfully loaded {Count} synthetic policy chunks into LocalRagRepository.", _policies.Count);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to load policy files from {Path}. Using fallback synthetic policies.", _knowledgeBasePath);
            AddFallbackPolicies();
        }
    }

    public async Task<List<PolicyChunk>> SearchPoliciesAsync(
        string query, string state, string providerType, int topK = 5, CancellationToken cancellationToken = default)
    {
        await SeedPoliciesAsync(cancellationToken);

        var queryTerms = NormalizeAndTokenize(query);
        var stateTerm = state.Trim().ToUpperInvariant();
        var pTypeTerm = providerType.Trim().ToLowerInvariant();

        var scoredPolicies = _policies.Select(p =>
        {
            double score = 0.0;
            var contentTerms = NormalizeAndTokenize(p.Content);

            // Term frequency match
            foreach (var term in queryTerms)
            {
                if (contentTerms.Contains(term)) score += 1.0;
            }

            // Metadata match bonuses
            if (p.Jurisdiction.Equals("National", StringComparison.OrdinalIgnoreCase) ||
                p.Jurisdiction.Equals(stateTerm, StringComparison.OrdinalIgnoreCase))
            {
                score += 1.5;
            }

            if (p.ProviderType.Equals("All", StringComparison.OrdinalIgnoreCase) ||
                p.ProviderType.ToLowerInvariant().Contains(pTypeTerm))
            {
                score += 1.5;
            }

            return new { Policy = p, Score = score };
        })
        .OrderByDescending(x => x.Score)
        .ThenBy(x => x.Policy.Id)
        .Take(topK)
        .Select(x => x.Policy)
        .ToList();

        return scoredPolicies;
    }

    private static HashSet<string> NormalizeAndTokenize(string text)
    {
        if (string.IsNullOrWhiteSpace(text)) return new HashSet<string>();

        char[] delimiters = new[] { ' ', '.', ',', ';', ':', '-', '_', '(', ')', '[', ']', '{', '}', '\r', '\n', '\t' };
        var words = text.ToLowerInvariant().Split(delimiters, StringSplitOptions.RemoveEmptyEntries);
        return new HashSet<string>(words);
    }

    private void AddFallbackPolicies()
    {
        _policies.Clear();
        _policies.AddRange(new[]
        {
            new PolicyChunk
            {
                Id = "SYN-POL-001",
                Content = "NCQA CR1: Primary source verification of medical state license is required prior to credentialing decision. Active unencumbered license required.",
                SourceType = "NCQA",
                Jurisdiction = "National",
                ProviderType = "All",
                RuleReference = "NCQA-CR1-LIC",
                IsSynthetic = true
            },
            new PolicyChunk
            {
                Id = "SYN-POL-002",
                Content = "State Board Rules: Expired licenses result in policy exception requiring administrative grace period verification or credentialing committee review.",
                SourceType = "StateLaw",
                Jurisdiction = "National",
                ProviderType = "All",
                RuleReference = "STATE-LIC-EXP",
                IsSynthetic = true
            },
            new PolicyChunk
            {
                Id = "SYN-POL-003",
                Content = "State Board Rules: Suspended licenses require immediate hold status and escalation to disciplinary committee.",
                SourceType = "StateLaw",
                Jurisdiction = "National",
                ProviderType = "All",
                RuleReference = "STATE-LIC-SUSP",
                IsSynthetic = true
            },
            new PolicyChunk
            {
                Id = "SYN-POL-004",
                Content = "Federal Sanction Policy: OIG, SAM.gov, or NPDB sanction matches mandate immediate Hold status and referral to legal committee.",
                SourceType = "NCQA",
                Jurisdiction = "National",
                ProviderType = "All",
                RuleReference = "FED-SANC-MATCH",
                IsSynthetic = true
            },
            new PolicyChunk
            {
                Id = "SYN-POL-005",
                Content = "Internal SOP-MISSING: Missing NPI or license details require application Hold pending provider response.",
                SourceType = "CommitteeSOP",
                Jurisdiction = "National",
                ProviderType = "All",
                RuleReference = "SOP-MISSING-INFO",
                IsSynthetic = true
            },
            new PolicyChunk
            {
                Id = "SYN-POL-006",
                Content = "Payer Rule: Clean credentialing application with active license and zero sanction matches qualifies for approval recommendation.",
                SourceType = "PayerRule",
                Jurisdiction = "National",
                ProviderType = "All",
                RuleReference = "PAYER-EXP-01",
                IsSynthetic = true
            }
        });
    }
}
