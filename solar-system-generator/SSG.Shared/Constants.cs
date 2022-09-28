namespace SSG.Shared;

public static class Constants
{
    public const float SecondsPerDay = 3600 * 24;
    public const float SecondsPerYear = SecondsPerDay * 365.24f;

    /// <summary>
    /// Units: m^3 / (kg s^2)
    /// </summary>
    public const float GravitationalConstant = 6.67e-11F;

    /// <summary>
    /// Units: m/s
    /// </summary>
    public const float SpeedOfLight = 2.997e8F;

    /// <summary>
    /// Units: m
    /// </summary>
    public const float OneAU = 1.496e11F;

    /// <summary>
    /// Units: kg
    /// </summary>
    public const float SolarMass = 1.989e30F;
    /// <summary>
    /// Units: m
    /// </summary>
    public const float SolarRadius = 6.960e8F;

    /// <summary>
    /// Units: kg
    /// </summary>
    public const float EarthMass = 5.974e24F;
    /// <summary>
    /// Units: m
    /// </summary>
    public const float EarthRadius = 6.378e6F;
    /// <summary>
    /// Units: degrees/second
    /// </summary>
    public const float EarthAngularVelocity = 360 / SecondsPerYear;

    public static float OfSolarMass(float percentage) => SolarMass * percentage;
    public static float OfSolarRadius(float percentage) => SolarRadius * percentage;
    public static float OfEarthMass(float percentage) => EarthMass * percentage;
    public static float OfEarthRadius(float percentage) => EarthRadius * percentage;
    public static float OfEarthAngVel(float percentage) => EarthAngularVelocity * percentage;
    public static float OfAU(float percentage) => OneAU * percentage;

    public static float AsAU(float meters) => meters / OneAU;
    public static float AsEarthMasses(float kilograms) => kilograms / EarthMass;
    public static float AsSolarMasses(float kilograms) => kilograms / SolarMass;
    public static float AsEarthRadii(float meters) => meters / EarthRadius;
    public static float AsEarthAngVel(float degPerSec) => degPerSec / EarthAngularVelocity;
    public static float AsSolarRadii(float meters) => meters / SolarRadius;

    public static float AngVelByDays(float totalDays) => 360 / (totalDays * SecondsPerDay);
}