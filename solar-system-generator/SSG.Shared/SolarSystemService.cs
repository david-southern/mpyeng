using System.Drawing;

namespace SSG.Shared;

public class SolarSystemService
{
    public SolarSystemService()
    {
    }

    public async Task<CelestialObject> LoadSolarSystem(string? solarSystemName = null)
    {
        await Task.CompletedTask;
        return MockSolarSystemData.MockSolarSystem;
    }
}


public static class MockSolarSystemData
{
    public static readonly CelestialObject Sol = new("Sol", null,
        0, 0, Constants.SolarMass, Constants.SolarRadius, "white")
    {
        IsStar = true
    };

    public static readonly CelestialObject Mercury = new("Mercury", Sol,
        Constants.OfAU(0.39F), 7.0F,
        Constants.OfEarthMass(0.055F), Constants.OfEarthRadius(0.38F), "gray");

    public static readonly CelestialObject Venus = new("Venus", Sol,
        Constants.OfAU(0.72F), 3.4F,
        Constants.OfEarthMass(0.815F), Constants.OfEarthRadius(0.95F), "greenyellow");

    public static readonly CelestialObject Earth = new("Earth", Sol,
        Constants.OfAU(1.0F), 0,
        Constants.OfEarthMass(1.0F), Constants.OfEarthRadius(1.0F), "blue");

    public static readonly CelestialObject Luna = new("Luna", Earth, 
        384_000_000, -23.0F, 735e20F, 3_476_000, "WhiteSmoke");

    public static readonly CelestialObject Mars = new("Mars", Sol,
        Constants.OfAU(1.52F), 1.9F,
        Constants.OfEarthMass(0.11F), Constants.OfEarthRadius(0.53F), "red");

    public static readonly CelestialObject Jupiter = new("Jupiter", Sol,
        Constants.OfAU(5.2F), 1.3F,
        Constants.OfEarthMass(318F), Constants.OfEarthRadius(10.9F), "OrangeRed");

    public static readonly CelestialObject Saturn = new("Saturn", Sol,
        Constants.OfAU(9.54F), 2.5F,
        Constants.OfEarthMass(95.2F), Constants.OfEarthRadius(9.13F), "Goldenrod");

    public static readonly CelestialObject Uranus = new("Uranus", Sol,
        Constants.OfAU(19.19F), 0.8F,
        Constants.OfEarthMass(14.5F), Constants.OfEarthRadius(3.98F), "Turquoise");

    public static readonly CelestialObject Neptune = new("Neptune", Sol,
        Constants.OfAU(30.06F), 1.8F,
        Constants.OfEarthMass(17.2F), Constants.OfEarthRadius(3.86F), "BlueViolet");

    public static readonly CelestialObject Pluto = new("Pluto", Sol,
        Constants.OfAU(39.5F), 17.0F,
        Constants.OfEarthMass(0.0024F), Constants.OfEarthRadius(0.18F), "DarkGray");

    public static readonly CelestialObject MockSolarSystem = Sol;
}