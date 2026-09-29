using CredentialIQ.Core.Models;
using Microsoft.EntityFrameworkCore;

namespace CredentialIQ.Infrastructure.Persistence;

public class CredentialIQDbContext : DbContext
{
    public CredentialIQDbContext(DbContextOptions<CredentialIQDbContext> options) : base(options)
    {
    }

    public DbSet<CredentialingCase> Cases => Set<CredentialingCase>();
    public DbSet<Provider> Providers => Set<Provider>();
    public DbSet<ProviderLicense> Licenses => Set<ProviderLicense>();
    public DbSet<VerificationResult> VerificationResults => Set<VerificationResult>();
    public DbSet<SanctionCheckResult> SanctionResults => Set<SanctionCheckResult>();
    public DbSet<RiskAssessment> RiskAssessments => Set<RiskAssessment>();
    public DbSet<WorkflowDecision> WorkflowDecisions => Set<WorkflowDecision>();
    public DbSet<AuditEvent> AuditEvents => Set<AuditEvent>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        modelBuilder.Entity<CredentialingCase>(entity =>
        {
            entity.HasKey(c => c.Id);
            entity.HasOne(c => c.Provider)
                  .WithMany()
                  .HasForeignKey(c => c.ProviderId)
                  .OnDelete(DeleteBehavior.Cascade);

            entity.HasMany(c => c.VerificationResults)
                  .WithOne()
                  .HasForeignKey(v => v.CaseId)
                  .OnDelete(DeleteBehavior.Cascade);

            entity.HasMany(c => c.SanctionResults)
                  .WithOne()
                  .HasForeignKey(s => s.CaseId)
                  .OnDelete(DeleteBehavior.Cascade);

            entity.HasMany(c => c.RiskAssessments)
                  .WithOne()
                  .HasForeignKey(r => r.CaseId)
                  .OnDelete(DeleteBehavior.Cascade);

            entity.HasMany(c => c.WorkflowDecisions)
                  .WithOne()
                  .HasForeignKey(w => w.CaseId)
                  .OnDelete(DeleteBehavior.Cascade);

            entity.HasMany(c => c.AuditEvents)
                  .WithOne()
                  .HasForeignKey(a => a.CaseId)
                  .OnDelete(DeleteBehavior.Cascade);

            entity.Ignore(c => c.Metadata); // Handled in-memory or transient
        });

        modelBuilder.Entity<Provider>(entity =>
        {
            entity.HasKey(p => p.Id);
            entity.HasIndex(p => p.Npi);
        });

        modelBuilder.Entity<VerificationResult>().HasKey(v => v.Id);
        modelBuilder.Entity<SanctionCheckResult>().HasKey(s => s.Id);
        modelBuilder.Entity<RiskAssessment>(entity =>
        {
            entity.HasKey(r => r.Id);
            entity.Property(r => r.AppliedRuleReferences)
                  .HasConversion(
                      v => string.Join(',', v),
                      v => v.Split(',', StringSplitOptions.RemoveEmptyEntries).ToList());
            entity.Property(r => r.RetrievedSourceIds)
                  .HasConversion(
                      v => string.Join(',', v),
                      v => v.Split(',', StringSplitOptions.RemoveEmptyEntries).ToList());
        });

        modelBuilder.Entity<WorkflowDecision>().HasKey(w => w.Id);
        modelBuilder.Entity<AuditEvent>().HasKey(a => a.Id);
    }
}
