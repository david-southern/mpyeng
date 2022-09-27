using Microsoft.AspNetCore.Mvc;

namespace SSG.APIProxies;

[ApiExplorerSettings(IgnoreApi = false)]
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
    public Task<CelestialObject> Get(string? solarSystemName = null)
    {
        return solarSystemService.LoadSolarSystem(solarSystemName);
    }
}