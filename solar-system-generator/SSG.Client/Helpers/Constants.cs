namespace SSG.Helpers;

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

    public static float AngVelFromDays(float totalDays) => 360 / (totalDays * SecondsPerDay);
    public static float AngVelToDays(float angVel) => 360 / (angVel * SecondsPerDay);
}

public class BackgroundImageData
{
    public static readonly List<BackgroundImageData> BackgroundImages = new() {
        new BackgroundImageData("None - DkBlue", null, "#080820"),
        new BackgroundImageData("None - Black", null, "#000000"),
        new BackgroundImageData("None - DkGreen", null, "#081008"),
        new BackgroundImageData("Milky Way 1", "images/milky-way-alec-favale-unsplash.jpg"),
        new BackgroundImageData("Milky Way 2", "images/milky-way-marc-schulte-unsplash.jpg"),
        new BackgroundImageData("Nebula 1 - Carina", "images/nebula_apod_carina-PillarJet_VIShst.jpg"),
        new BackgroundImageData("Nebula 2 - Carina/Clombari", "images/nebula_apod_CarinaNorth_Colombari_3000.jpg"),
        new BackgroundImageData("Nebula 3 - Horse & Flame", "images/nebula_apod_HorseFlame_Ayoub_4305.jpg"),
        new BackgroundImageData("Nebula 4 - Flaming Star", "images/nebula_apod_IC405FlamingstarDetail_geissinger1700.jpg"),
        new BackgroundImageData("Nebula 5 - M42", "images/nebula_apod_m42_gleason.jpg"),
        new BackgroundImageData("Nebula 6", "images/nebula_apod_ngc6751_hst_715.jpg"),
        new BackgroundImageData("Stars 1 - M46/M47", "images/stars_apod__m46m47_hetlage.jpg"),
        new BackgroundImageData("Stars 2 - Deep Field", "images/stars_apod_Hubble_ultra_deep_field_high_rez_edit1.jpg"),
        new BackgroundImageData("Stars 3 - M34", "images/stars_apod_m34Franke.jpg"),
        new BackgroundImageData("Stars 4 - M67", "images/stars_apod_M67_Greg_Noel.jpg"),
        new BackgroundImageData("Stars 5", "images/stars_wikimedia_stars_Cevennes_France_night_sky_with_02.jpg"),
    };

    public string Description { get; set; }
    public string? URL { get; set; }
    public float Brightness { get; set; }
    public float Contrast { get; set; }
    public float Darken { get; set; }
    public float Lighten { get; set; }
    public float Blur { get; set; }

    public BackgroundImageData(string _description, string? _url = null, string? _color = null)
    {
        Description = _description;
        URL = _url ?? _color;
    }
}

