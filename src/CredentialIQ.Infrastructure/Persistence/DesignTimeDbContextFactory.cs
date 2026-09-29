using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Design;

namespace CredentialIQ.Infrastructure.Persistence;

public class DesignTimeDbContextFactory : IDesignTimeDbContextFactory<CredentialIQDbContext>
{
    public CredentialIQDbContext CreateDbContext(string[] args)
    {
        var optionsBuilder = new DbContextOptionsBuilder<CredentialIQDbContext>();
        optionsBuilder.UseSqlite("Data Source=credentialiq.db");

        return new CredentialIQDbContext(optionsBuilder.Options);
    }
}
