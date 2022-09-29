using Microsoft.AspNetCore.Mvc;

namespace SSG.APIProxies;

[ApiController]
[Route("/api/solar-system")]
public class SolarSystemController : ControllerBase
{
    private static readonly ILogger MyLogger = Log.ForContext<SolarSystemController>();
    private readonly SolarSystemService solarSystemService;

    public SolarSystemController(SolarSystemService ssService)
    {
        solarSystemService = ssService;
    }

    [HttpGet]
    public Task<CelestialObject> Get(string? systemName = null)
    {
        return solarSystemService.LoadSolarSystem(systemName);
    }
}