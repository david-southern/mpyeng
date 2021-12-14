namespace WarpCoreController;

public class WarpCoreFog2D : IAnimationEffect
{
    public string Name => "WarpCore - Fog";
    public string Description => "Glowing fog that shifts from dark to bright in smoothly-changing patches";
    public int RenderOrder => 100;

    private readonly INoise Noise;
    private double NoiseX;
    private double NoiseY;
    private double NoiseZ;
    private double PixNoiseX;
    private double PixNoiseY;

    private double PowerLevel;
    private double PowerLevelControlValue()
    {
        return PowerLevel;
    }

    private double GetNoiseValue(double noiseX, double noiseY)
    {
        double noiseValue = Noise.NormalizedNoise(noiseX, noiseY, NoiseZ);
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

    public WarpCoreFog2D()
    {
        ScaleX = new(PowerLevelControlValue, 4, 5);
        ScaleY = new(PowerLevelControlValue, 4, 5);
        SpeedX = new(PowerLevelControlValue, 0, 0);
        SpeedY = new(PowerLevelControlValue, 15, 150);
        SpeedZ = new(PowerLevelControlValue, 25, 60);


        Hue = new(PowerLevelControlValue, HSVColor.HUE_BLUE, HSVColor.HUE_BLUE);
        SatStart = new(SatNoiseControlValue, 0.7, 1.0);
        SatEnd = new(SatNoiseControlValue, 0.7, 1.0);
        Sat = new(PowerLevelControlValue, SatStart, SatEnd);
        ValStart = new(ValNoiseControlValue, 0.2, 0.7);
        ValEnd = new(ValNoiseControlValue, 0.2, 0.7);
        Val = new(PowerLevelControlValue, ValStart, ValEnd);
        CoreColor = new(Hue, Sat, Val);

        // Create and configure FastNoise object
        double normalizeRange = WarpCore.WarpCoreSegmentLength * ScaleY.Value;

        FastNoiseLite FastNoise = new((int)DateTime.Now.Ticks, normalizeRange, normalizeRange);
        FastNoise.SetNoiseType(FastNoiseLite.NoiseType.OpenSimplex2);
        FastNoise.SetFrequency(0.040f);
        FastNoise.SetFractalType(FastNoiseLite.FractalType.FBm);
        FastNoise.SetFractalOctaves(3);
        FastNoise.SetFractalLacunarity(0.5f);
        FastNoise.SetFractalGain(0.5f);

        Noise = FastNoise;
    }

    double lastSimTime = 0;

    public void Render(double powerLevel, double simElapsedTime, List<HSVColor> Pixels, bool showDiags = false)
    {
        PowerLevel = powerLevel;

        double elapsedSeconds = simElapsedTime - lastSimTime;
        lastSimTime = simElapsedTime;

        NoiseX += SpeedX.Value * elapsedSeconds;
        NoiseY += SpeedY.Value * elapsedSeconds;
        NoiseZ += SpeedZ.Value * elapsedSeconds;

        int diagPix = Pixels.Count / 2;

        for (int pixIndex = 0; pixIndex < Pixels.Count; pixIndex++)
        {
            int xOffset = pixIndex / WarpCore.WarpCoreSegmentLength;
            int yOffset = pixIndex % WarpCore.WarpCoreSegmentLength;

            if (xOffset % 2 == 1)
            {
                yOffset = WarpCore.WarpCoreSegmentLength - yOffset;
            }

            PixNoiseX = NoiseX + (xOffset * ScaleX.Value);
            PixNoiseY = NoiseY + (yOffset * ScaleY.Value);

            Pixels[pixIndex] = CoreColor.Value;
        }
    }
}
