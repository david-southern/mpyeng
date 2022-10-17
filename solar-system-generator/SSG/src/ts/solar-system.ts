import { CelestialObject } from "./celestial-object";
import { Constants } from "./ssg.utils"


export const EmptySystem = new CelestialObject({
    Name: "Cygnus X-1",
    ObjectRadius: Constants.SolarRadius,
    ObjectColor: "#ddddff",
    IsStar: true
});

export const SpeedTest = new CelestialObject({
    Name: "SpeedTest",
    IsStar: true,
    ObjectRadius: Constants.OfSolarRadius(0.5),
    PhaseAngle: 0,
    ObjectColor: "#770000"
});

const S1 = new CelestialObject({
    Name: "One Day",
    ParentObject: SpeedTest,
    OrbitalSemiMajorAxis: Constants.OfAU(8), OrbitalSemiMinorAxis: Constants.OfAU(8),
    OrbitalVelocity: Constants.AngVelFromDays(365), OrbitalInclination: 0,
    ObjectRadius: Constants.OfEarthRadius(3.3),
    ObjectColor: "white", OrbitColor: "#dddddd",
    PhaseAngle: 0
});


export const Wack = new CelestialObject({
    Name: "Wackmobile",
    OrbitalSemiMajorAxis: 0, OrbitalSemiMinorAxis: 0,
    OrbitalVelocity: 0, OrbitalInclination: 0,
    ObjectRadius: Constants.OfSolarRadius(2.5),
    ObjectColor: "#d8fff",
    PhaseAngle: 0,
    IsStar: true
});

const P1 = new CelestialObject({
    Name: "Vanilla Circle",
    ParentObject: Wack,
    OrbitalSemiMajorAxis: Constants.OfAU(8), OrbitalSemiMinorAxis: Constants.OfAU(8),
    OrbitalVelocity: Constants.AngVelFromDays(65.24), OrbitalInclination: 0,
    ObjectRadius: Constants.OfEarthRadius(3.3),
    ObjectColor: "cyan", OrbitColor: "#dddddd",
    PhaseAngle: 0
});

const P2 = new CelestialObject({
    Name: "Vanilla Ellipse",
    ParentObject: Wack,
    OrbitalSemiMajorAxis: Constants.OfAU(8), OrbitalSemiMinorAxis: Constants.OfAU(5),
    OrbitalVelocity: Constants.AngVelFromDays(165.24), OrbitalInclination: 0,
    ObjectRadius: Constants.OfEarthRadius(3.3),
    ObjectColor: "magenta", OrbitColor: "#777777",
    PhaseAngle: 180
});

const P3 = new CelestialObject({
    Name: "Phased",
    ParentObject: Wack,
    OrbitalSemiMajorAxis: Constants.OfAU(15), OrbitalSemiMinorAxis: Constants.OfAU(11),
    OrbitalVelocity: Constants.AngVelFromDays(65.24), OrbitalInclination: 0,
    ObjectRadius: Constants.OfEarthRadius(7.3),
    ObjectColor: "yellow", OrbitColor: "yellow",
    PhaseAngle: 30
});

const P4 = new CelestialObject({
    Name: "Phased-Inclined",
    ParentObject: Wack,
    OrbitalSemiMajorAxis: Constants.OfAU(19), OrbitalSemiMinorAxis: Constants.OfAU(13),
    OrbitalVelocity: Constants.AngVelFromDays(265.24), OrbitalInclination: 20,
    ObjectRadius: Constants.OfEarthRadius(3.3),
    ObjectColor: "red", OrbitColor: "#ff7777",
    PhaseAngle: 90
});


// Planetary Fact Sheet:
// https://nssdc.gsfc.nasa.gov/planetary/factsheet/

export const Sol = new CelestialObject({
    Name: "Sol",
    OrbitalSemiMajorAxis: 0, OrbitalSemiMinorAxis: 0,
    OrbitalVelocity: 0, OrbitalInclination: 0,
    ObjectRadius: Constants.SolarRadius,
    ObjectColor: "white",
    IsStar: true
});

const Mercury = new CelestialObject({
    Name: "Mercury",
    ParentObject: Sol,
    OrbitalSemiMajorAxis: Constants.OfAU(0.387), OrbitalSemiMinorAxis: Constants.OfAU(0.379),
    OrbitalVelocity: Constants.AngVelFromDays(88), OrbitalInclination: 7.0,
    ObjectRadius: Constants.OfEarthRadius(0.38),
    ObjectColor: "gray"
});

const Venus = new CelestialObject({
    Name: "Venus",
    ParentObject: Sol,
    OrbitalSemiMajorAxis: Constants.OfAU(0.723), OrbitalSemiMinorAxis: Constants.OfAU(0.723),
    OrbitalVelocity: Constants.AngVelFromDays(224.7), OrbitalInclination: 3.4,
    ObjectRadius: Constants.OfEarthRadius(0.95),
    ObjectColor: "GreenYellow"
});


const Earth = new CelestialObject({
    Name: "Earth",
    ParentObject: Sol,
    OrbitalSemiMajorAxis: Constants.OfAU(1.0), OrbitalSemiMinorAxis: Constants.OfAU(0.999),
    OrbitalVelocity: Constants.AngVelFromDays(365.24), OrbitalInclination: 0,
    ObjectRadius: Constants.OfEarthRadius(1.0),
    ObjectColor: "blue"
});

const Luna = new CelestialObject({
    Name: "Luna",
    ParentObject: Earth,
    OrbitalSemiMajorAxis: 384_000_000, OrbitalSemiMinorAxis: 384_000_000,
    OrbitalVelocity: Constants.AngVelFromDays(27.3), OrbitalInclination: -23.0,
    ObjectRadius: 3_476_000,
    ObjectColor: "WhiteSmoke"
});

const Mars = new CelestialObject({
    Name: "Mars",
    ParentObject: Sol,
    OrbitalSemiMajorAxis: Constants.OfAU(1.524), OrbitalSemiMinorAxis: Constants.OfAU(1.517),
    OrbitalVelocity: Constants.AngVelFromDays(687), OrbitalInclination: 1.9,
    ObjectRadius: Constants.OfEarthRadius(0.53),
    ObjectColor: "red"
});

const beltColor = '#ffffff'; // '#ffffff'
const beltStart = 5; // 7.7;
const beltWidth = 9.3; // 6.3;
const beltCount = 27;
const beltWidthPer = beltWidth / beltCount;
const beltMaxDensity = 0.3;

for (let belt = 0; belt < beltCount; belt++) {
    const beltProgress = belt / beltCount;
    const beltDensity = Math.pow(Math.sin(beltProgress * Math.PI), 3) * beltMaxDensity;

    const AsteroidsIn = new CelestialObject({
        Name: `Asteroid Belt ${belt}`,
        ParentObject: Sol,
        OrbitalSemiMajorAxis: 0, OrbitalSemiMinorAxis: 0, OrbitalVelocity: 0, OrbitalInclination: 0, ObjectRadius: 0,
        RingInnerRadius: beltStart + beltWidthPer * belt,
        RingWidth: beltWidthPer,
        RingDensity: beltDensity,
        RingColor: beltColor
    });
}

const Jupiter = new CelestialObject({
    Name: "Jupiter",
    ParentObject: Sol,
    OrbitalSemiMajorAxis: Constants.OfAU(5.2), OrbitalSemiMinorAxis: Constants.OfAU(5.198),
    OrbitalVelocity: Constants.AngVelFromDays(4331), OrbitalInclination: 1.3,
    ObjectRadius: Constants.OfEarthRadius(10.9),
    ObjectColor: "OrangeRed",
    InitialOrbitalAngle: 330
});

const Saturn = new CelestialObject({
    Name: "Saturn",
    ParentObject: Sol,
    OrbitalSemiMajorAxis: Constants.OfAU(9.572), OrbitalSemiMinorAxis: Constants.OfAU(9.559),
    OrbitalVelocity: Constants.AngVelFromDays(10747), OrbitalInclination: 2.5,
    ObjectRadius: Constants.OfEarthRadius(9.13),
    ObjectColor: "Goldenrod",
    InitialOrbitalAngle: 0
});

// Ring layout ref: https://www.britannica.com/place/Saturn-planet/The-ring-system
const SaturnRingsC = new CelestialObject({
    Name: "C-Ring",
    ParentObject: Saturn,
    OrbitalSemiMajorAxis: 0, OrbitalSemiMinorAxis: 0, OrbitalVelocity: 0, OrbitalInclination: -13.0, ObjectRadius: 0,
    RingInnerRadius: 1.23,
    RingWidth: 0.28,
    RingDensity: 0.1,
    RingColor: "#ffffff"
});

const SaturnRingsB = new CelestialObject({
    Name: "B-Ring",
    ParentObject: Saturn,
    OrbitalSemiMajorAxis: 0, OrbitalSemiMinorAxis: 0, OrbitalVelocity: 0, OrbitalInclination: -13.0, ObjectRadius: 0,
    RingInnerRadius: 1.52,
    RingWidth: 0.43,
    RingDensity: 0.35,
    RingColor: "#ffffff"
});

const SaturnRingsA = new CelestialObject({
    Name: "A-Ring",
    ParentObject: Saturn,
    OrbitalSemiMajorAxis: 0, OrbitalSemiMinorAxis: 0, OrbitalVelocity: 0, OrbitalInclination: -13.0, ObjectRadius: 0,
    RingInnerRadius: 2.02,
    RingWidth: 0.25,
    RingDensity: 0.25,
    RingColor: "#ffffff"
});

const Uranus = new CelestialObject({
    Name: "Uranus",
    ParentObject: Sol,
    OrbitalSemiMajorAxis: Constants.OfAU(19.164), OrbitalSemiMinorAxis: Constants.OfAU(19.143),
    OrbitalVelocity: Constants.AngVelFromDays(30589), OrbitalInclination: 0.8,
    ObjectRadius: Constants.OfEarthRadius(3.98),
    ObjectColor: "Turquoise"
});

const Neptune = new CelestialObject({
    Name: "Neptune",
    ParentObject: Sol,
    OrbitalSemiMajorAxis: Constants.OfAU(30.180), OrbitalSemiMinorAxis: Constants.OfAU(30.179),
    OrbitalVelocity: Constants.AngVelFromDays(59800), OrbitalInclination: 1.8,
    ObjectRadius: Constants.OfEarthRadius(3.86),
    ObjectColor: "BlueViolet"
});

const Pluto = new CelestialObject({
    Name: "Pluto",
    ParentObject: Sol,
    OrbitalSemiMajorAxis: Constants.OfAU(39.481), OrbitalSemiMinorAxis: Constants.OfAU(38.288),
    OrbitalVelocity: Constants.AngVelFromDays(90560), OrbitalInclination: 17.0,
    ObjectRadius: Constants.OfEarthRadius(0.18),
    ObjectColor: "DarkGray"
});


export const CetiAlpha = new CelestialObject({
    Name: "Ceti Alpha",
    OrbitalSemiMajorAxis: 0, OrbitalSemiMinorAxis: 0,
    OrbitalVelocity: 0, OrbitalInclination: 0,
    ObjectRadius: Constants.SolarRadius,
    ObjectColor: "#ffc8c8c",
    IsStar: true
});

const CA1 = new CelestialObject({
    Name: "CA I",
    ParentObject: CetiAlpha,
    OrbitalSemiMajorAxis: Constants.OfAU(0.43), OrbitalSemiMinorAxis: Constants.OfAU(0.5),
    OrbitalVelocity: Constants.AngVelFromDays(113.7), OrbitalInclination: 3.4,
    ObjectRadius: Constants.OfEarthRadius(0.38),
    ObjectColor: "gray",
    PhaseAngle: -27
});

const CA2 = new CelestialObject({
    Name: "CA II",
    ParentObject: CetiAlpha,
    OrbitalSemiMajorAxis: Constants.OfAU(0.523), OrbitalSemiMinorAxis: Constants.OfAU(0.523),
    OrbitalVelocity: Constants.AngVelFromDays(173.7), OrbitalInclination: -17,
    ObjectRadius: Constants.OfEarthRadius(0.38),
    ObjectColor: "gray",
    PhaseAngle: 37,
});

const CA3 = new CelestialObject({
    Name: "CA III",
    ParentObject: CetiAlpha,
    OrbitalSemiMajorAxis: Constants.OfAU(0.613), OrbitalSemiMinorAxis: Constants.OfAU(0.535),
    OrbitalVelocity: Constants.AngVelFromDays(203.7), OrbitalInclination: 0.4,
    ObjectRadius: Constants.OfEarthRadius(0.38),
    ObjectColor: "gray"
});

const CA4 = new CelestialObject({
    Name: "CA IV",
    ParentObject: CetiAlpha,
    OrbitalSemiMajorAxis: Constants.OfAU(0.723), OrbitalSemiMinorAxis: Constants.OfAU(0.723),
    OrbitalVelocity: Constants.AngVelFromDays(224.7), OrbitalInclination: 3.4,
    ObjectRadius: Constants.OfEarthRadius(0.95),
    ObjectColor: "#202070"
});

const CA5 = new CelestialObject({
    Name: "CA V",
    ParentObject: CetiAlpha,
    OrbitalSemiMajorAxis: Constants.OfAU(1.0), OrbitalSemiMinorAxis: Constants.OfAU(0.999),
    OrbitalVelocity: Constants.AngVelFromDays(365.24), OrbitalInclination: 0,
    ObjectRadius: Constants.OfEarthRadius(1.0),
    ObjectColor: "blue"
});

const CA6 = new CelestialObject({
    Name: "CA VI",
    ParentObject: CetiAlpha,
    OrbitalSemiMajorAxis: Constants.OfAU(5.0), OrbitalSemiMinorAxis: Constants.OfAU(3),
    OrbitalVelocity: Constants.AngVelFromDays(589.24), OrbitalInclination: -7,
    ObjectRadius: Constants.OfEarthRadius(10.0),
    ObjectColor: "#DEB887"
});