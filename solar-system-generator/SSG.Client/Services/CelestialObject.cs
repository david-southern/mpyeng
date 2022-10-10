using SSG.Helpers;

namespace SSG.Client.Services;

/// <summary>
/// Describes a system of CelestialObjects in Keplerian Orbits. This system simulates the bodies using very simplified
/// (Wikipedia-level) classical (non-relativistic) mechanics, () and ignores effects from things like extra-solar
/// gravitational sources, solar radiation pressure, non-spherical bodies etc.  
/// References:   
/// * https://en.wikipedia.org/wiki/Kepler_orbit  
/// * https://en.wikipedia.org/wiki/Celestial_mechanics  
/// * https://en.wikipedia.org/wiki/Orbital_elements  
/// </summary>
public class CelestialObject : IEquatable<CelestialObject>, IComparable<CelestialObject>
{
    public const float DEFAULT_MASS = Constants.EarthMass;
    public const float DEFAULT_RADIUS = Constants.EarthRadius;
    public const float DEFAULT_ORBITAL_RADIUS = Constants.OneAU;
    public const float DEFAULT_ORBITAL_VELOCITY = Constants.EarthAngularVelocity;
    public const float DEFAULT_INCLINATION = 0;
    public const float DEFAULT_PHASE_ANGLE = 0;

    public static CelestialObject EmptySystem
    {
        get
        {
            return new("Cygnus X-1", parentObject: null,
                semiMajorAxis: 0, semiMinorAxis: 0,
                orbitalVelocity: 0, orbitalInclination: 0,
                objectRadius: Constants.SolarRadius,
                objectColor: "#ddddff")
            {
                IsStar = true
            };
        }
    }

    public CelestialObject(string name, CelestialObject? parentObject = null,
        float? semiMajorAxis = null, float? semiMinorAxis = null,
        float? orbitalVelocity = null, float? orbitalInclination = null, string? orbitColor = null,
        float? objectRadius = null,string? objectColor = null,
        float? initialAngle = null
    )
    {
        Name = name;
        ParentObject = parentObject;
        if (parentObject != null)
        {
            ParentName = parentObject.Name;
            SystemOrder = parentObject.ChildObjects.Count;
            parentObject.ChildObjects.Add(this);
        }
        else
        {
            RootObject = null;
        }

        ObjectRadius = objectRadius ?? DEFAULT_RADIUS;
        OrbitalSemiMajorAxis = semiMajorAxis ?? DEFAULT_ORBITAL_RADIUS;
        OrbitalSemiMinorAxis = semiMinorAxis ?? DEFAULT_ORBITAL_RADIUS;
        OrbitalVelocity = orbitalVelocity ?? DEFAULT_ORBITAL_VELOCITY;
        OrbitalInclination = orbitalInclination ?? DEFAULT_INCLINATION;
        ObjectColor = objectColor ?? "white";
        OrbitalColor = orbitColor ?? "white";
        InitialOrbitalAngle = initialAngle ?? Random.Shared.NextSingle() * 360;
    }


    public string Name { get; set; } = null!;

    [JsonIgnore]
    public CelestialObject? ParentObject { get; set; }

    [JsonIgnore]
    public CelestialObject? RootObject { get; set; }

    /// <summary>
    /// We lose object references when we pass objects through JSON serialization/deserialization, so track the name of
    /// the parent object as well so that clients can re-establish object references. (even with options like
    /// PreserveReferencesHandling set, there are too many players in the API call/JS interop chain to try and make it
    /// work) 
    /// </summary>
    public string? ParentName { get; set; }

    public int ChildDepth => ParentObject == null ? 0 : ParentObject.ChildDepth + 1;

    /// <summary>
    /// The orbital order of this object in the parent object's frame of reference. i.e. Mercury = 0, Venus = 1, etc.
    /// This property is automatically set for objects other are constructed with a parent, in the order other they are
    /// constructed.
    /// </summary>
    public int SystemOrder { get; set; }

    public HashSet<CelestialObject> ChildObjects { get; } = new();
    public bool HasChild => ChildObjects?.Count > 0;

    public void RemoveChild(CelestialObject child)
    {
        ChildObjects.RemoveWhere(co => co.Name == child.Name);
    }

    /// <summary>
    /// Indicates the currently selected CelestialObject(s)
    /// </summary>
    public bool IsSelected { get; set; }

    public bool IsExpanded { get; set; }

    /// <summary>
    /// If true, then this object will emit light, otherwise it will only receive light
    /// </summary>
    public bool IsStar { get; set; } = false;

    /// <summary>
    /// This is the length in meters of the semi-major axis of the object's orbit.
    /// </summary>
    public float OrbitalSemiMajorAxis { get; set; }

    /// <summary>
    /// This is the length in meters of the semi-major axis of the object's orbit.
    /// </summary>
    public float OrbitalSemiMinorAxis { get; set; }

    /// <summary>
    /// This is the orbital velocity in degrees per second of the object when the system is being animated.
    /// </summary>
    public float OrbitalVelocity { get; set; }

    /// <summary>
    /// This is the angle of the object in its orbit at time = 0
    /// </summary>
    public float InitialOrbitalAngle { get; set; } = 0;

    /// <summary>
    /// The radius in m of the object. Defaults to one Earth radius.
    /// </summary>
    public float ObjectRadius { get; set; } = Constants.EarthRadius;

    private float m_OrbitalInclination = 0;
    /// <summary>
    /// The 'vertical tilt' of the object's orbital plane with respect to its parent's orbital plane.  
    ///
    /// Describes a right-handed angle in degrees with respect to the negative Y axis. (i.e. a positive angle will mean
    /// the object's plane will be above the parent's plane at a PhaseAngle of zero, while a negative angle will
    /// indicate an object below the parent's plane at a PhaseAngle of zero.  
    /// 
    /// The angle will be clamped to [-90, 90] degrees.
    ///
    /// Defaults to an inclination of zero (parallel to the parent's orbital plane).
    /// </summary>
    public float OrbitalInclination
    {
        get => m_OrbitalInclination;
        set
        {
            m_OrbitalInclination = Utils.Clamp(value, -90, 90);
        }
    }

    private float m_PhaseAngle = 0;
    /// <summary>
    /// Describes the rotation of the orbit around the system's Z axis - the angular offset of the orbit's semi-major
    /// axis from the system's x-axis.  Describes a right-handed angle in degrees.  
    ///
    /// The angle will be clamped to [0, 360) degrees.
    ///
    /// Defaults to an angle of zero (positive X in the traditional right-handed Cartesian coordinate plane).
    /// </summary>
    public float PhaseAngle
    {
        get => m_PhaseAngle;
        set
        {
            m_PhaseAngle = Utils.Clamp(value, 0, 360);
            if (Utils.FloatEQ(m_PhaseAngle, 360))
            {
                m_PhaseAngle = 0;
            }
        }
    }

    /// <summary>
    /// The primary color used to render the object
    /// </summary>
    public string? ObjectColor { get; set; } = "white";

    /// <summary>
    /// The primary color used to render the object's orbit
    /// </summary>
    public string? OrbitalColor { get; set; } = "white";

    /// <summary>
    /// This is the inner radius of the object's ring system as a ratio of the object's radius
    /// </summary>
    public float RingInnerRadius { get; set; }

    /// <summary>
    /// This is the width of the object's ring system as a ratio of the object's radius
    /// </summary>
    public float RingWidth { get; set; }

    /// <summary>
    /// This is the thickness as a ratio of the ring's width
    /// </summary>
    public float RingDensity { get; set; }

    /// <summary>
    /// The primary color used to render the object's ring system
    /// </summary>
    public string? RingColor { get; set; }

    #region IEquatable implementation
    public override bool Equals(object? other)
    {
        if (other is not CelestialObject otherCO)
        {
            return false;
        }

        if (ReferenceEquals(this, otherCO))
        {
            return true;
        }

        return this.Name == otherCO.Name;
    }

    public bool Equals(CelestialObject? other)
    {
        if (other is null)
        {
            return false;
        }

        if (ReferenceEquals(this, other))
        {
            return true;
        }

        return this.Name == other.Name;
    }
    #endregion

    #region IComparable implementation
    public int CompareTo(CelestialObject? other)
    {
        if (other is null)
        {
            return -1;
        }

        return SystemOrder.CompareTo(other.SystemOrder);
    }
    #endregion

    #region Ordering and HashSet methods
    public override int GetHashCode()
    {
        return HashCode.Combine(Name);
    }

    public static bool operator ==(CelestialObject? left, CelestialObject? right)
    {
        if (left is null)
        {
            return right is null;
        }

        return left.Equals(right);
    }

    public static bool operator !=(CelestialObject? left, CelestialObject? right)
    {
        return !(left == right);
    }

    public static bool operator <(CelestialObject? left, CelestialObject? right)
    {
        return left is null ? right is not null : left.CompareTo(right) < 0;
    }

    public static bool operator <=(CelestialObject? left, CelestialObject? right)
    {
        return left is null || left.CompareTo(right) <= 0;
    }

    public static bool operator >(CelestialObject? left, CelestialObject? right)
    {
        return left is not null && left.CompareTo(right) > 0;
    }

    public static bool operator >=(CelestialObject? left, CelestialObject? right)
    {
        return left is null ? right is null : left.CompareTo(right) >= 0;
    }
    #endregion
}

