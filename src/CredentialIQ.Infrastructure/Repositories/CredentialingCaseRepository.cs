using CredentialIQ.Core.Models;
using CredentialIQ.Infrastructure.Persistence;
using Microsoft.EntityFrameworkCore;

namespace CredentialIQ.Infrastructure.Repositories;

public class CredentialingCaseRepository
{
    private readonly CredentialIQDbContext _dbContext;

    public CredentialingCaseRepository(CredentialIQDbContext dbContext)
    {
        _dbContext = dbContext;
    }

    public async Task<CredentialingCase?> GetByIdAsync(Guid id, CancellationToken cancellationToken = default)
    {
        return await _dbContext.Cases
            .Include(c => c.Provider)
            .Include(c => c.VerificationResults)
            .Include(c => c.SanctionResults)
            .Include(c => c.RiskAssessments)
            .Include(c => c.WorkflowDecisions)
            .Include(c => c.AuditEvents)
            .FirstOrDefaultAsync(c => c.Id == id, cancellationToken);
    }

    public async Task SaveCaseAsync(CredentialingCase credentialingCase, CancellationToken cancellationToken = default)
    {
        var entry = _dbContext.Entry(credentialingCase);
        if (entry.State == EntityState.Detached)
        {
            await _dbContext.Cases.AddAsync(credentialingCase, cancellationToken);
        }

        await _dbContext.SaveChangesAsync(cancellationToken);
    }
}
