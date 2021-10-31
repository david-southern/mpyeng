using ColorMine.ColorSpaces;

using rpi_ws281x;

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.Linq;
using System.Threading.Tasks;

namespace PiController
{
    public class WarpCoreFog : IAnimationEffect
    {
        public static WarpCoreFog Instance => new();

        public string Name => "WarpCore - Fog";
        public string Description => "Glowing fog that shifts from dark to bright in smoothly-changing patches";
        public List<AnimationParameter> Parameters => new();
        public int RenderOrder => 100;

        private readonly FastNoiseLite Noise;
        private double NoiseY;
        private double NoiseDY = 1;
        private double NoiseZ;

        public readonly AnimationParameter NoiseScale = new("Noise Scale", "How 'tightly' should the noise function be sampled for each pixel. Smaller numbers will result in slower color change from one pixel the the next, and thus larger patches of colors with more gradual color change from one patch to the next.  Larger values will result in smaller patches and more abrupt color change from one patch to the next.", 2);

        public readonly AnimationParameter NoiseSpeed = new("Noise Speed", "How quickly should the noise scan line move along the perpendicular axis of the noise.  Lower values will result in the fog color patches changing more slowly, while higher values will change the patches more quickly.", 0.5);

        public readonly AnimationParameter HueMin = new("Fog Hue Min", "The base hue of the fog when the Engine Core is at its minimum power level", PixelColor.HUE_BLUE);
        public readonly AnimationParameter HueMax = new("Fog Hue Max", "The base hue of the fog when the Engine Core is at its maximum power level", PixelColor.HUE_CYAN);

        public readonly AnimationParameter LumMin = new("Fog Brightness Min", "The average brightness of the fog when the Engine Core is at its minimum power level", 0.5);
        public readonly AnimationParameter LumRangeMin = new("Fog Brightness Delta Min", "The delta brightness of the fog when the Engine Core is at its minimum power level", 0.49);
        public readonly AnimationParameter LumMax = new("Fog Brightness Max", "The average brightness of the fog when the Engine Core is at its Maximum power level", 0.7);
        public readonly AnimationParameter LumRangeMax = new("Fog Brightness Delta Max", "The delta brightness of the fog when the Engine Core is at its maximum power level", 0.3);

        private WarpCoreFog()
        {
            Parameters.Add(NoiseScale);
            Parameters.Add(NoiseSpeed);
            Parameters.Add(HueMin);
            Parameters.Add(HueMax);
            Parameters.Add(LumMin);
            Parameters.Add(LumRangeMin);
            Parameters.Add(LumMax);
            Parameters.Add(LumRangeMax);

            NoiseZ = Rand.Linear(-100.0, 100.0);

            // Create and configure FastNoise object
            Noise = new((int)DateTime.Now.Ticks);
            Noise.SetNoiseType(FastNoiseLite.NoiseType.OpenSimplex2);
            Noise.SetFrequency(0.040f);
            Noise.SetFractalType(FastNoiseLite.FractalType.FBm);
            Noise.SetFractalOctaves(3);
            Noise.SetFractalLacunarity(0.5f);
            Noise.SetFractalGain(0.5f);
        }

        private double NoiseMax = -1f;
        private double NoiseMin = 1f;
        private int MinMaxReset = 10;
        private int MinMaxResetCount = 0;

        public void Render(List<PixelColor> Pixels, bool showDiags = false)
        {
            WarpCore Core = WarpCore.Instance;

            double hue = ColorUtils.Lerp(HueMin.Value, HueMax.Value, Core.PowerLevel);
            double lumMean = ColorUtils.Lerp(LumMin.Value, LumMax.Value, Core.PowerLevel);
            double lumRange = ColorUtils.Lerp(LumRangeMin.Value, LumRangeMax.Value, Core.PowerLevel);

            double lumMin = ColorUtils.Clamp(lumMean - lumRange * 2);
            double lumMax = ColorUtils.Clamp(lumMean + lumRange * 2);

            for (int pixIndex = 0; pixIndex < Pixels.Count; pixIndex++)
            {
                double pixNoise = Noise.NormalizedNoise(pixIndex * NoiseScale.Value, NoiseY * NoiseScale.Value, NoiseZ);

                NoiseMax = Math.Max(NoiseMax, pixNoise);
                NoiseMin = Math.Min(NoiseMin, pixNoise);

                double noiseLum = ColorUtils.Lerp(lumMin, lumMax, pixNoise);
                Pixels[pixIndex] = new PixelColor(hue, 1.0, noiseLum);

                if (showDiags && pixIndex == 5)
                {
                    Logger.Info($"WarpCoreFog: Rendering {Pixels.Count} Pixels: " +
                        $"Scale: {NoiseScale.Value}, Speed: {NoiseSpeed.Value}, pixNoise: {pixNoise:N3}({NoiseMin:N3}-{NoiseMax:N3}), " +
                        $"Hue: {hue:N0}({HueMin.Value:N0}-{HueMax.Value:N0}), " +
                        $"Lum: {noiseLum:N3}({lumMin:N3}-{lumMax:N3}) - " +
                        $"Pix5 Color: {Pixels[pixIndex]}");

                    if(MinMaxResetCount++ >= MinMaxReset)
                    {
                        Logger.Info($"WarpCoreFog: Reset Min/Max");
                        NoiseMax = -1f;
                        NoiseMin = 1f;
                        MinMaxResetCount = 0;
                    }
                }
            }

            NoiseY += NoiseDY * NoiseSpeed.Value;

            if (NoiseY < 0 || NoiseY > Pixels.Count)
            {
                NoiseDY = -NoiseDY;
            }
        }
    }
}
