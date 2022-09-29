namespace SSG.Helpers;

public class SSGSettings
{
    const string GRID_TYPE_RECTANGULAR = "Rectangular";
    const string GRID_TYPE_POLAR = "Polar";
    const string GRID_TYPE_NONE = "None";

    public string AmbientLightColor = "#404040";

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
    public float ViewAngleXDegrees = -80;
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
    public float GridMinorDivisions = 18;
    // For a rectangular grid, this is the color of the non-center lines.  For a polar grid, this is the second of two
    // alternating colors used to render the rings and sector lines.
    public string GridMinorColor = "#003000";

    // If true, the planets will rotate along their orbits.
    public bool Animate = true;

    // By default, the animation runs in real time.  This setting runs the animation faster so that it is visible.  The
    // setting is exponential, so a setting of 0 is real time (one Earth orbit per real-time year) while a setting of
    // about 7 will have Earth completing a full orbit once per second.
    public float AnimationSpeed = 0;

    // The amount to scale planets over their 'actual' size so that they are visible on an orbital scale.
    public float PlanetScale = 2000;

    // The amount to scale planets over their 'actual' size so that they are visible on an orbital scale.
    public float StarScale = 50;

    public float Zoom = 1;
};

