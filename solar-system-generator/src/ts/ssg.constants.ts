export class Constants {
    public static OneAU = 1.496e11;
    public static SolarRadius = 6.960e8;
    public static EarthRadius = 6.378e6;

    public static SecondsPerDay = 3600 * 24;
    public static SecondsPerYear = Constants.SecondsPerDay * 365.24;

    public static EarthAngularVelocity = 360 / Constants.SecondsPerYear;

    public static OfSolarRadius = (percentage: number) => Constants.SolarRadius * percentage;
    public static OfEarthRadius = (percentage: number) => Constants.EarthRadius * percentage;
    public static OfEarthAngVel = (percentage: number) => Constants.EarthAngularVelocity * percentage;
    public static OfAU = (percentage: number) => Constants.OneAU * percentage;

    public static AsAU = (meters: number) => meters / Constants.OneAU;
    public static AsEarthRadii = (meters: number) => meters / Constants.EarthRadius;
    public static AsEarthAngVel = (degPerSec: number) => degPerSec / Constants.EarthAngularVelocity;
    public static AsSolarRadii = (meters: number) => meters / Constants.SolarRadius;

    public static AngVelFromDays = (totalDays: number) => 360 / (totalDays * Constants.SecondsPerDay);
    public static AngVelToDays = (angVel: number) => 360 / (angVel * Constants.SecondsPerDay);
}
