namespace SSG.Helpers;

public class SSGSettings
{
    public const float DEFAULT_VIEW_ANGLE_X = -80;
    public const string GRID_TYPE_RECTANGULAR = "Rectangular";
    public const string GRID_TYPE_POLAR = "Polar";
    public const string GRID_TYPE_NONE = "None";

    public string AmbientLightColor = "#404040";
    public float AmbientLightIntensity = 1;

    public bool IncludeDirectionalLight = false;
    public string DirectionalLightColor = "#000000";
    public float DirectionalLightIntensity = 0;
    public string DirectionalLightPosition = "[0, 0, 0]";

    // We want a perspective view so that we get a sense of 'nearer/farther', but we also want our planets to be apparent
    // spheres.  If the camera is too close, then we get fisheye distortion of the scene.  Instead put the camera way far
    // away, and use a very narrow FOV to get the right look.
    public float FieldOfViewDegrees = 10;

    // Use these controls to tilt the view anywhere from a "top view" (all zero) to an "edge on view" (X=90).  Messing
    // with Y or Z will make things weird.  Probably better to use the Orbit Controls.
    public float ViewAngleXDegrees = DEFAULT_VIEW_ANGLE_X;
    public float ViewAngleYDegrees = 0;
    public float ViewAngleZDegrees = 0;

    public string GridType = GRID_TYPE_POLAR;

    // If rendered, the grid will be sized to the maximum extents of the system, scaled by GridSizeFactor
    public float GridSizeFactor = 1.1f;

    // For a rectangular grid, this is the number of divisions along both the X and Y axes.  For a polar grid, this is
    // the number of parallel rings
    public float GridMajorDivisions = 4;

    // For a rectangular grid, this is the color of the center lines.  For a polar grid, this is the first of two
    // alternating colors used to render the rings and sector lines.
    public string GridMajorColor = "#004000";

    // For a polar grid, this is the number of radial sectors
    public float GridMinorDivisions = 36;
    // For a rectangular grid, this is the color of the non-center lines.  For a polar grid, this is the second of two
    // alternating colors used to render the rings and sector lines.
    public string GridMinorColor = "#003000";

    // If true, the planets will rotate along their orbits.
    public bool Animate = true;

    // Animation Speed, ranging from zero to one.
    public float AnimationSpeed = 0;
    public float MaxAnimationSpeed = 10e8f;

    // Animation Time Scale - a linear interpolation of AnimationSpeed over the range [0, 10e7]
    // public float AnimationTimeScale => (float)(Math.Clamp(AnimationSpeed, 0, 1) * 10e7);

    // Animation Time Scale - a quadratic ease-in interpolation of AnimationSpeed over the range [0, 10e8]
    public float AnimationTimeScale
    {
        get
        {
            float clampedSpeed = Math.Clamp(AnimationSpeed, -1, 1);

            // Use a quadratic easing function, but allow the sign of the clampedSpeed through
            return clampedSpeed * Math.Abs(clampedSpeed) * MaxAnimationSpeed;
        }
    }

    // A human-readable representation of the AnimationTimeScale
    public string AnimationTimeScaleHuman => Utils.FloatEQ(AnimationTimeScale, 0) ? "paused" : $"{Utils.HumanTime(AnimationTimeScale)} per second";

    // The amount to scale planets over their 'actual' size so that they are visible on an orbital scale.
    public float PlanetScale = 1500;

    // The amount to scale planets over their 'actual' size so that they are visible on an orbital scale.
    public float StarScale = 50;

    public float Zoom = 1;

    public bool ResetOrbitControls = false;
    public bool DownloadImage = false;

    public BackgroundImageData BackgroundImage { get; set; } = BackgroundImageData.BackgroundImages[0];
};

