using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

using Helpers;

namespace PiController
{
    public class WarpCoreFog2D : IAnimationEffect
    {
        const int StripLength = 122;

        public string Name => "WarpCore - Fog";
        public string Description => "Glowing fog that shifts from dark to bright in smoothly-changing patches";
        public int RenderOrder => 100;

        private readonly Stopwatch RenderStart;

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

        public WarpCoreFog2D()
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
            double normalizeRange = StripLength * ScaleY.Value;

            FastNoiseLite FastNoise = new((int)DateTime.Now.Ticks, normalizeRange, normalizeRange);
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
        private int MinMaxReset = 10;
        private int MinMaxResetCount = 0;

        public void Render(double powerLevel, List<HSVColor> Pixels, bool showDiags = false)
        {
            PowerLevel = powerLevel;

            double elapsedSeconds = RenderStart.Elapsed.TotalSeconds;
            RenderStart.Restart();

            NoiseX += SpeedX.Value * elapsedSeconds;
            NoiseY += SpeedY.Value * elapsedSeconds;
            NoiseZ += SpeedZ.Value * elapsedSeconds;

            for (int pixIndex = 0; pixIndex < Pixels.Count; pixIndex++)
            {
                int diagPix = Pixels.Count / 2;

                int xOffset = pixIndex / StripLength;
                int yOffset = pixIndex % StripLength;

                if (xOffset % 2 == 1)
                {
                    yOffset = StripLength - yOffset;
                }

                PixNoiseX = NoiseX + (xOffset * ScaleX.Value);
                PixNoiseY = NoiseY + (yOffset * ScaleY.Value);

                Pixels[pixIndex] = CoreColor.Value;

                if (showDiags && pixIndex == diagPix)
                {
                    Logger.Info($"WarpCoreFog: Rendering {Pixels.Count} Pixels: " +
                        $"Scale: ({ScaleX.Value},{ScaleY.Value}), " +
                        $"Speed: ({SpeedX.Value},{SpeedY.Value},{SpeedZ.Value}), " +
                        $"Noise Min/Max: {NoiseMin:N3}/{NoiseMax:N3}, " +
                        $"Pix{diagPix} Color: {Pixels[pixIndex]}");

                    if (MinMaxResetCount++ >= MinMaxReset)
                    {
                        Logger.Info($"WarpCoreFog: Reset Min/Max");
                        NoiseMax = -1f;
                        NoiseMin = 1f;
                        MinMaxResetCount = 0;
                    }
                }
            }
        }
    }
}
