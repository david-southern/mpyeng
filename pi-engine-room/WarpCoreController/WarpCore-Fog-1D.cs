using System.Diagnostics;

namespace WarpCoreController;

public class WarpCoreFog1D : IAnimationEffect
{
    public string Name => "WarpCore - Fog";
    public string Description => "Glowing fog that shifts from dark to bright in smoothly-changing patches";
    public int RenderOrder => 100;

    private readonly Stopwatch RenderStart;

    private readonly INoise Noise;
    private double NoiseY;
    private double PixNoiseX;
    private double PixNoiseY;

    private double PowerLevel;
    private double PowerLevelControlValue()
    {
        return PowerLevel;
    }

    private double GetNoiseValue(double noiseX, double noiseY)
    {
        double noiseValue = Noise.NormalizedNoise(noiseX, noiseY, 0);
        NoiseMax = Math.Max(NoiseMax, noiseValue);
        NoiseMin = Math.Min(NoiseMin, noiseValue);
        return noiseValue;
    }

    private double SatNoiseControlValue()
    {
        return GetNoiseValue(-PixNoiseX, -PixNoiseY);
    }

    private double ValNoiseControlValue()
    {
        // We need to use different noise values for Sat vs. Val so that they don't track each other. We can use
        // the same noise origin and scale, and just flip them about the coordinate origin to get different noise
        // values.
        return GetNoiseValue(-PixNoiseX, -PixNoiseY);
    }

    private readonly DependentDouble ScaleX;
    private readonly DependentDouble ScaleY;
    private readonly DependentDouble SpeedX;
    private readonly DependentDouble SpeedY;
    private readonly DependentDouble SpeedZ;
    private readonly DependentDouble Hue;
    private readonly DependentDouble SatStart;
    private readonly DependentDouble SatEnd;
    private readonly DependentRange Sat;
    private readonly DependentDouble ValStart;
    private readonly DependentDouble ValEnd;
    private readonly DependentRange Val;
    private readonly HSVColorByDependent CoreColor;

    public WarpCoreFog1D()
    {
        ScaleX = new(PowerLevelControlValue, 4, 5);
        ScaleY = new(PowerLevelControlValue, 4, 5);
        SpeedX = new(PowerLevelControlValue, 0, 0);
        SpeedY = new(PowerLevelControlValue, 15, 150);
        SpeedZ = new(PowerLevelControlValue, 25, 60);
        Hue = new(PowerLevelControlValue, HSVColor.HUE_BLUE, HSVColor.HUE_CYAN);
        SatStart = new(SatNoiseControlValue, 70, 100);
        SatEnd = new(SatNoiseControlValue, 0, 40);
        Sat = new(PowerLevelControlValue, SatStart, SatEnd);
        ValStart = new(ValNoiseControlValue, 20, 70);
        ValEnd = new(ValNoiseControlValue, 60, 100);
        Val = new(PowerLevelControlValue, ValStart, ValEnd);
        CoreColor = new(Hue, Sat, Val);

        // Create and configure FastNoise object
        FastNoiseLite FastNoise = new((int)DateTime.Now.Ticks);
        FastNoise.SetNoiseType(FastNoiseLite.NoiseType.OpenSimplex2);
        FastNoise.SetFrequency(0.040f);
        FastNoise.SetFractalType(FastNoiseLite.FractalType.FBm);
        FastNoise.SetFractalOctaves(3);
        FastNoise.SetFractalLacunarity(0.5f);
        FastNoise.SetFractalGain(0.5f);

        Noise = FastNoise;
        RenderStart = Stopwatch.StartNew();
    }

    private double NoiseMax = -1f;
    private double NoiseMin = 1f;

    public void Render(double powerLevel, double simElapsedTime, List<HSVColor> Pixels, bool showDiags = false)
    {
        PowerLevel = powerLevel;
        double elapsedSeconds = RenderStart.Elapsed.TotalSeconds;
        RenderStart.Restart();

        NoiseY += SpeedY.Value * elapsedSeconds;

        for (int pixIndex = 0; pixIndex < Pixels.Count; pixIndex++)
        {
            PixNoiseX = pixIndex * ScaleX.Value;
            PixNoiseY = NoiseY * ScaleY.Value;

            Pixels[pixIndex] = CoreColor.Value;
        }
    }
}
