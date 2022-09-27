namespace SSG.Shared;

public static partial class Utils
{
    public static float Clamp(float value, float min, float max)
    {
        return value < min ? min : value > max ? max : value;
    }
}