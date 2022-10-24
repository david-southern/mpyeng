export class Constants {
    public static COLOR_NONE = 'none';
    public static DEFAULT_ORBITAL_COLOR = 'white';

    public static OneAU = 1.496e11;
    public static SolarRadius = 6.96e8;
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

    // I modeled all the planetary data in actual units, but those numbers are huge, and hard to track while debugging.
    // Scale everything down to 'smallish' numbers internally.
    public static CoordsScale = Constants.OneAU;

    public static RootGroup = 'RootGroup';
    public static PerigeeSubscriber = 'PerigeeSubscriber';
    public static OrbitSubscriber = 'OrbitSubscriber';
    public static BodySubscriber = 'BodySubscriber';
    public static OrbiterSubscriber = 'OrbiterSubscriber';
    public static OrbitGroup = 'OrbitGroup';
    public static OrbitMesh = 'OrbitMesh';
    public static OrbitCurve = 'OrbitCurve';
    public static BodyGroup = 'BodyGroup';
    public static Orbiter = 'Orbiter';
    public static OrbiterInitialPositionSubscriber = 'OrbiterInitialPositionSubscriber';
    public static OrbiterVelocitySubscriber = 'OrbiterVelocitySubscriber';
    public static RingSubscriber = 'RingSubscriber';
    public static RingGroup = 'RingGroup';
    public static InclinationSubscriber = 'InclinationSubscriber';
    public static PhaseAngleSubscriber = 'PhaseAngleSubscriber';
}
