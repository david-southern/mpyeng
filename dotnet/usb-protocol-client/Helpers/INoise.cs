namespace Helpers;

public interface INoise
{
    public double GetNoise(double x, double y, double z);
    public double NormalizedNoise(double x, double y, double z);
}
