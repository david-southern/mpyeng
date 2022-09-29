using Flurl;
using Flurl.Http;

public class SSGAPIClient
{
    private readonly ConfigurationService config;

    public SSGAPIClient(ConfigurationService _config)
    {
        config = _config;
    }

    public async Task<CelestialObject?> GetSolarSystem(string? systemName = null)
    {
        try
        {
            return await config.ServerBaseAddress
                .AppendPathSegment("/api/solar-system")
                .SetQueryParam("systemName", systemName)
                .GetJsonAsync<CelestialObject?>();
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Exception: {ex.Message}");
            return null;
        }
    }
}
