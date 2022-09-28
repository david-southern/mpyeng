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

    public static readonly CelestialObject TestSystem = new("Binary", null,
        semiMajorAxis: 0, semiMinorAxis: 0,
        orbitalVelocity: 0, orbitalInclination: 0,
        objectMass: Constants.SolarMass, objectRadius: Constants.SolarRadius,
        objectColor: "white")
    {
        IsStar = false
    };

    public static readonly CelestialObject TCyg = new("Cygnus X-1", TestSystem,
        semiMajorAxis: Constants.OfAU(8F), semiMinorAxis: Constants.OfAU(7F),
        orbitalVelocity: 0, orbitalInclination: 0,
        objectMass: Constants.OfEarthMass(0.055F), objectRadius: Constants.OfSolarRadius(1.3f),
        objectColor: "#ffffd8")
        {
            PhaseAngle = 0,
            IsStar = true
        };

    public static readonly CelestialObject THDE = new("HDE", TestSystem,
        semiMajorAxis: Constants.OfAU(0.72F), semiMinorAxis: Constants.OfAU(0.52F),
        orbitalVelocity: 0, orbitalInclination: 0,
        objectMass: Constants.OfEarthMass(0.815F), objectRadius: Constants.OfSolarRadius(2.5F),
        objectColor: "#d8ffff")
        {
            PhaseAngle = 180,
            IsStar = true
        };

    public static readonly CelestialObject TPlanet = new("Pln", TestSystem,
        semiMajorAxis: Constants.OfAU(4.72F), semiMinorAxis: Constants.OfAU(4.72F),
        orbitalVelocity: 0, orbitalInclination: 0,
        objectMass: Constants.OfEarthMass(0.815F), objectRadius: Constants.OfEarthRadius(3.5F),
        objectColor: "#cccccc")
        {
            PhaseAngle = 75
        };


    // Planetary Fact Sheet:
    // https://nssdc.gsfc.nasa.gov/planetary/factsheet/

    public static readonly CelestialObject Sol = new("Sol", parentObject: null,
        semiMajorAxis: 0, semiMinorAxis: 0,
        orbitalVelocity: 0, orbitalInclination: 0,
        objectMass: Constants.SolarMass, objectRadius: Constants.SolarRadius,
        objectColor: "white")
    {
        IsStar = true
    };

    public static readonly CelestialObject Mercury = new("Mercury", Sol,
        semiMajorAxis: Constants.OfAU(0.387F), semiMinorAxis: Constants.OfAU(0.379F),
        orbitalVelocity: Constants.AngVelByDays(88), orbitalInclination: 7.0F,
        objectMass: Constants.OfEarthMass(0.055F), objectRadius: Constants.OfEarthRadius(0.38F),
        objectColor: "gray");

    public static readonly CelestialObject Venus = new("Venus", Sol,
        semiMajorAxis: Constants.OfAU(0.723F), semiMinorAxis: Constants.OfAU(0.723F),
        orbitalVelocity: Constants.AngVelByDays(224.7f), orbitalInclination: 3.4F,
        objectMass: Constants.OfEarthMass(0.815F), objectRadius: Constants.OfEarthRadius(0.95F),
        objectColor: "greenyellow");


    public static readonly CelestialObject Earth = new("Earth", Sol,
        semiMajorAxis: Constants.OfAU(1.0F), semiMinorAxis: Constants.OfAU(0.999F),
        orbitalVelocity: Constants.AngVelByDays(365.24f), orbitalInclination: 0,
        objectMass: Constants.OfEarthMass(1.0F), objectRadius: Constants.OfEarthRadius(1.0F),
        objectColor: "blue");

    public static readonly CelestialObject Luna = new("Luna", Earth,
        semiMajorAxis: 384_000_000, semiMinorAxis: 384_000_000,
        orbitalVelocity: Constants.AngVelByDays(27.3f), orbitalInclination: -23.0F,
        objectMass: 735e20F, objectRadius: 3_476_000,
        objectColor: "WhiteSmoke");

    public static readonly CelestialObject Mars = new("Mars", Sol,
        semiMajorAxis: Constants.OfAU(1.524F), semiMinorAxis: Constants.OfAU(1.517F),
        orbitalVelocity: Constants.AngVelByDays(687), orbitalInclination: 1.9F,
        objectMass: Constants.OfEarthMass(0.11F), objectRadius: Constants.OfEarthRadius(0.53F),
        objectColor: "red");

    public static readonly CelestialObject Jupiter = new("Jupiter", Sol,
        semiMajorAxis: Constants.OfAU(5.2F), semiMinorAxis: Constants.OfAU(5.198F),
        orbitalVelocity: Constants.AngVelByDays(4331), orbitalInclination: 1.3F,
        objectMass: Constants.OfEarthMass(318F), objectRadius: Constants.OfEarthRadius(10.9F),
        objectColor: "OrangeRed");

    public static readonly CelestialObject Saturn = new("Saturn", Sol,
        semiMajorAxis: Constants.OfAU(9.572F), semiMinorAxis: Constants.OfAU(9.559F),
        orbitalVelocity: Constants.AngVelByDays(10747), orbitalInclination: 2.5F,
        objectMass: Constants.OfEarthMass(95.2F), objectRadius: Constants.OfEarthRadius(9.13F),
        objectColor: "Goldenrod");

    public static readonly CelestialObject Uranus = new("Uranus", Sol,
        semiMajorAxis: Constants.OfAU(19.164F), semiMinorAxis: Constants.OfAU(19.143F),
        orbitalVelocity: Constants.AngVelByDays(30589), orbitalInclination: 0.8F,
        objectMass: Constants.OfEarthMass(14.5F), objectRadius: Constants.OfEarthRadius(3.98F),
        objectColor: "Turquoise");

    public static readonly CelestialObject Neptune = new("Neptune", Sol,
        semiMajorAxis: Constants.OfAU(30.180F), semiMinorAxis: Constants.OfAU(30.179F),
        orbitalVelocity: Constants.AngVelByDays(59800), orbitalInclination: 1.8F,
        objectMass: Constants.OfEarthMass(17.2F), objectRadius: Constants.OfEarthRadius(3.86F),
        objectColor: "BlueViolet");

    public static readonly CelestialObject Pluto = new("Pluto", Sol,
        semiMajorAxis: Constants.OfAU(39.481F), semiMinorAxis: Constants.OfAU(38.288F),
        orbitalVelocity: Constants.AngVelByDays(90560), orbitalInclination: 17.0F,
        objectMass: Constants.OfEarthMass(0.0024F), objectRadius: Constants.OfEarthRadius(0.18F),
        objectColor: "DarkGray");

    public static readonly CelestialObject MockSolarSystem = Sol;
}