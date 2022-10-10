using SSG.Helpers;

namespace SSG.Client.Services;

public static class MockSolarSystemData
{
    public static readonly CelestialObject SpeedTest = new("SpeedTest", null,
    semiMajorAxis: 0, semiMinorAxis: 0,
    orbitalVelocity: 0, orbitalInclination: 0,
    objectRadius: Constants.OfSolarRadius(0.5F),
    objectColor: "#770000")
    {
        PhaseAngle = 0,
        IsStar = true
    };

    private static readonly CelestialObject S1 = new("One Day", SpeedTest,
        semiMajorAxis: Constants.OfAU(8F), semiMinorAxis: Constants.OfAU(8F),
        orbitalVelocity: Constants.AngVelFromDays(365f), orbitalInclination: 0,
        objectRadius: Constants.OfEarthRadius(3.3f),
        objectColor: "white", orbitColor: "#dddddd")
    {
        PhaseAngle = 0
    };


    public static readonly CelestialObject Wack = new("Wackmobile", null,
        semiMajorAxis: 0, semiMinorAxis: 0,
        orbitalVelocity: 0, orbitalInclination: 0,
        objectRadius: Constants.OfSolarRadius(2.5F),
        objectColor: "#d8ffff")
    {
        PhaseAngle = 0,
        IsStar = true
    };

    private static readonly CelestialObject P1 = new("Vanilla Circle", Wack,
        semiMajorAxis: Constants.OfAU(8F), semiMinorAxis: Constants.OfAU(8F),
        orbitalVelocity: Constants.AngVelFromDays(65.24f), orbitalInclination: 0,
        objectRadius: Constants.OfEarthRadius(3.3f),
        objectColor: "cyan", orbitColor: "#dddddd")
    {
        PhaseAngle = 0
    };

    private static readonly CelestialObject P2 = new("Vanilla Ellipse", Wack,
        semiMajorAxis: Constants.OfAU(8F), semiMinorAxis: Constants.OfAU(5F),
        orbitalVelocity: Constants.AngVelFromDays(165.24f), orbitalInclination: 0,
        objectRadius: Constants.OfEarthRadius(3.3f),
        objectColor: "magenta", orbitColor: "#777777")
    {
        PhaseAngle = 180
    };

    private static readonly CelestialObject P3 = new("Phased", Wack,
        semiMajorAxis: Constants.OfAU(15F), semiMinorAxis: Constants.OfAU(11F),
        orbitalVelocity: Constants.AngVelFromDays(65.24f), orbitalInclination: 0,
        objectRadius: Constants.OfEarthRadius(7.3f),
        objectColor: "yellow", orbitColor: "yellow")
    {
        PhaseAngle = 30
    };

    private static readonly CelestialObject P4 = new("Phased-Inclined", Wack,
        semiMajorAxis: Constants.OfAU(19F), semiMinorAxis: Constants.OfAU(13F),
        orbitalVelocity: Constants.AngVelFromDays(265.24f), orbitalInclination: 20,
        objectRadius: Constants.OfEarthRadius(3.3f),
        objectColor: "red", orbitColor: "#ff7777")
    {
        PhaseAngle = 90
    };


    // Planetary Fact Sheet:
    // https://nssdc.gsfc.nasa.gov/planetary/factsheet/

    public static readonly CelestialObject Sol = new("Sol", parentObject: null,
        semiMajorAxis: 0, semiMinorAxis: 0,
        orbitalVelocity: 0, orbitalInclination: 0,
        objectRadius: Constants.SolarRadius,
        objectColor: "white")
    {
        IsStar = true
    };

    private static readonly CelestialObject Mercury = new("Mercury", Sol,
        semiMajorAxis: Constants.OfAU(0.387F), semiMinorAxis: Constants.OfAU(0.379F),
        orbitalVelocity: Constants.AngVelFromDays(88), orbitalInclination: 7.0F,
        objectRadius: Constants.OfEarthRadius(0.38F),
        objectColor: "gray");

    private static readonly CelestialObject Venus = new("Venus", Sol,
        semiMajorAxis: Constants.OfAU(0.723F), semiMinorAxis: Constants.OfAU(0.723F),
        orbitalVelocity: Constants.AngVelFromDays(224.7f), orbitalInclination: 3.4F,
        objectRadius: Constants.OfEarthRadius(0.95F),
        objectColor: "GreenYellow");


    private static readonly CelestialObject Earth = new("Earth", Sol,
        semiMajorAxis: Constants.OfAU(1.0F), semiMinorAxis: Constants.OfAU(0.999F),
        orbitalVelocity: Constants.AngVelFromDays(365.24f), orbitalInclination: 0,
        objectRadius: Constants.OfEarthRadius(1.0F),
        objectColor: "blue");

    private static readonly CelestialObject Luna = new("Luna", Earth,
        semiMajorAxis: 384_000_000, semiMinorAxis: 384_000_000,
        orbitalVelocity: Constants.AngVelFromDays(27.3f), orbitalInclination: -23.0F,
        objectRadius: 3_476_000,
        objectColor: "WhiteSmoke");

    private static readonly CelestialObject Mars = new("Mars", Sol,
        semiMajorAxis: Constants.OfAU(1.524F), semiMinorAxis: Constants.OfAU(1.517F),
        orbitalVelocity: Constants.AngVelFromDays(687), orbitalInclination: 1.9F,
        objectRadius: Constants.OfEarthRadius(0.53F),
        objectColor: "red");

    private static readonly CelestialObject Asteroids = new("Asteroid Belt", Sol,
        semiMajorAxis: 0, semiMinorAxis: 0, orbitalVelocity: 0, orbitalInclination: 0F, objectRadius: 0)
    {
        RingInnerRadius = 7.7f,
        RingWidth = 6.3f,
        RingDensity = 0.05f,
        RingColor = "#ffffff"
    };

    private static readonly CelestialObject Jupiter = new("Jupiter", Sol,
        semiMajorAxis: Constants.OfAU(5.2F), semiMinorAxis: Constants.OfAU(5.198F),
        orbitalVelocity: Constants.AngVelFromDays(4331), orbitalInclination: 1.3F,
        objectRadius: Constants.OfEarthRadius(10.9F),
        objectColor: "OrangeRed", initialAngle: 330);

    private static readonly CelestialObject Saturn = new("Saturn", Sol,
        semiMajorAxis: Constants.OfAU(9.572F), semiMinorAxis: Constants.OfAU(9.559F),
        orbitalVelocity: Constants.AngVelFromDays(10747), orbitalInclination: 2.5F,
        objectRadius: Constants.OfEarthRadius(9.13F),
        objectColor: "Goldenrod", initialAngle: 0);

    // Ring layout ref: https://www.britannica.com/place/Saturn-planet/The-ring-system
    private static readonly CelestialObject SaturnRingsC = new("C-Ring", Saturn,
        semiMajorAxis: 0, semiMinorAxis: 0, orbitalVelocity: 0, orbitalInclination: -13.0F, objectRadius: 0)
    {
        RingInnerRadius = 1.23f,
        RingWidth = 0.28f,
        RingDensity = 0.1f,
        RingColor = "#ffffff"
    };

    private static readonly CelestialObject SaturnRingsB = new("B-Ring", Saturn,
        semiMajorAxis: 0, semiMinorAxis: 0, orbitalVelocity: 0, orbitalInclination: -13.0F, objectRadius: 0)
    {
        RingInnerRadius = 1.52f,
        RingWidth = 0.43f,
        RingDensity = 0.35f,
        RingColor = "#ffffff"
    };

    private static readonly CelestialObject SaturnRingsA = new("A-Ring", Saturn,
        semiMajorAxis: 0, semiMinorAxis: 0, orbitalVelocity: 0, orbitalInclination: -13.0F, objectRadius: 0)
    {
        RingInnerRadius = 2.02f,
        RingWidth = 0.25f,
        RingDensity = 0.25f,
        RingColor = "#ffffff"
    };

    private static readonly CelestialObject Uranus = new("Uranus", Sol,
        semiMajorAxis: Constants.OfAU(19.164F), semiMinorAxis: Constants.OfAU(19.143F),
        orbitalVelocity: Constants.AngVelFromDays(30589), orbitalInclination: 0.8F,
        objectRadius: Constants.OfEarthRadius(3.98F),
        objectColor: "Turquoise");

    private static readonly CelestialObject Neptune = new("Neptune", Sol,
        semiMajorAxis: Constants.OfAU(30.180F), semiMinorAxis: Constants.OfAU(30.179F),
        orbitalVelocity: Constants.AngVelFromDays(59800), orbitalInclination: 1.8F,
        objectRadius: Constants.OfEarthRadius(3.86F),
        objectColor: "BlueViolet");

    private static readonly CelestialObject Pluto = new("Pluto", Sol,
        semiMajorAxis: Constants.OfAU(39.481F), semiMinorAxis: Constants.OfAU(38.288F),
        orbitalVelocity: Constants.AngVelFromDays(90560), orbitalInclination: 17.0F,
        objectRadius: Constants.OfEarthRadius(0.18F),
        objectColor: "DarkGray");


    public static readonly CelestialObject CetiAlpha = new("Ceti Alpha", parentObject: null,
        semiMajorAxis: 0, semiMinorAxis: 0,
        orbitalVelocity: 0, orbitalInclination: 0,
        objectRadius: Constants.SolarRadius,
        objectColor: "#ffc8c8c")
    {
        IsStar = true
    };

    private static readonly CelestialObject CA1 = new("CA I", CetiAlpha,
        semiMajorAxis: Constants.OfAU(0.43F), semiMinorAxis: Constants.OfAU(0.5F),
        orbitalVelocity: Constants.AngVelFromDays(113.7f), orbitalInclination: 3.4F,
        objectRadius: Constants.OfEarthRadius(0.38F),
        objectColor: "gray")
    {
        PhaseAngle = -27
    };

    private static readonly CelestialObject CA2 = new("CA II", CetiAlpha,
            semiMajorAxis: Constants.OfAU(0.523F), semiMinorAxis: Constants.OfAU(0.523F),
            orbitalVelocity: Constants.AngVelFromDays(173.7f), orbitalInclination: -17F,
            objectRadius: Constants.OfEarthRadius(0.38F),
            objectColor: "gray")
    {
        PhaseAngle = 37,
    };

    private static readonly CelestialObject CA3 = new("CA III", CetiAlpha,
        semiMajorAxis: Constants.OfAU(0.613F), semiMinorAxis: Constants.OfAU(0.535F),
        orbitalVelocity: Constants.AngVelFromDays(203.7f), orbitalInclination: 0.4F,
        objectRadius: Constants.OfEarthRadius(0.38F),
        objectColor: "gray");

    private static readonly CelestialObject CA4 = new("CA IV", CetiAlpha,
        semiMajorAxis: Constants.OfAU(0.723F), semiMinorAxis: Constants.OfAU(0.723F),
        orbitalVelocity: Constants.AngVelFromDays(224.7f), orbitalInclination: 3.4F,
        objectRadius: Constants.OfEarthRadius(0.95F),
        objectColor: "#202070");

    private static readonly CelestialObject CA5 = new("CA V", CetiAlpha,
        semiMajorAxis: Constants.OfAU(1.0F), semiMinorAxis: Constants.OfAU(0.999F),
        orbitalVelocity: Constants.AngVelFromDays(365.24f), orbitalInclination: 0,
        objectRadius: Constants.OfEarthRadius(1.0F),
        objectColor: "blue");

    private static readonly CelestialObject CA6 = new("CA VI", CetiAlpha,
        semiMajorAxis: Constants.OfAU(5.0F), semiMinorAxis: Constants.OfAU(3F),
        orbitalVelocity: Constants.AngVelFromDays(589.24f), orbitalInclination: -7,
        objectRadius: Constants.OfEarthRadius(10.0F),
        objectColor: "#DEB887");



}