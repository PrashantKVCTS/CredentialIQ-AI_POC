namespace CredentialIQ.Core.Models;

public class PolicyChunk
{
    public string Id { get; set; } = string.Empty;
    public string Content { get; set; } = string.Empty;
    public string SourceType { get; set; } = string.Empty; // e.g. NCQA, StateLaw, PayerRule, CommitteeSOP
    public string Jurisdiction { get; set; } = string.Empty; // e.g. National, CA, NY, TX
    public string ProviderType { get; set; } = string.Empty; // e.g. All, MD, NP, DO
    public string RuleReference { get; set; } = string.Empty;
    public DateTime EffectiveDate { get; set; } = DateTime.UtcNow;
    public bool IsSynthetic { get; set; } = true;
}
