using ColorMine.ColorSpaces;

using System;
using System.Collections.Generic;
using System.Drawing;

namespace PiController
{
    public class PixelColor : Hsl
    {
        public const double HUE_ROSE = 330;
        public const double HUE_MAGENTA = 300;
        public const double HUE_VIOLET = 270;
        public const double HUE_BLUE = 240;
        public const double HUE_AZURE = 210;
        public const double HUE_CYAN = 180;
        public const double HUE_TURQUOISE = 150;
        public const double HUE_GREEN = 120;
        public const double HUE_CHARTREUSE = 90;
        public const double HUE_YELLOW = 60;
        public const double HUE_ORANGE = 30;
        public const double HUE_RED = 0;

        public static readonly PixelColor Black = new(0.0, 0.0, 0.0);
        public static readonly PixelColor White = new(0.0, 0.0, 1.0);

        public static readonly PixelColor Rose = new(HUE_ROSE, 1.0, 0.5);
        public static readonly PixelColor Magenta = new(HUE_MAGENTA, 1.0, 0.5);
        public static readonly PixelColor Violet = new(HUE_VIOLET, 1.0, 0.5);
        public static readonly PixelColor Blue = new(HUE_BLUE, 1.0, 0.5);
        public static readonly PixelColor Azure = new(HUE_AZURE, 1.0, 0.5);
        public static readonly PixelColor Cyan = new(HUE_CYAN, 1.0, 0.5);
        public static readonly PixelColor Turquiose = new(HUE_TURQUOISE, 1.0, 0.5);
        public static readonly PixelColor Green = new(HUE_GREEN, 1.0, 0.5);
        public static readonly PixelColor Chartreuse = new(HUE_CHARTREUSE, 1.0, 0.5);
        public static readonly PixelColor Yellow = new(HUE_YELLOW, 1.0, 0.5);
        public static readonly PixelColor Orange = new(HUE_ORANGE, 1.0, 0.5);
        public static readonly PixelColor Red = new(HUE_RED, 1.0, 0.5);

        public PixelColor()
        {
        }

        public PixelColor(double h, double s, double l)
        {
            H = h;
            S = s;
            L = l;
        }

        public PixelColor(PixelColor other)
        {
            H = other.H;
            S = other.S;
            L = other.L;
        }

        public PixelColor(Color color)
        {
            Rgb rgb = new() { R = color.R, G = color.G, B = color.B };
            Hsl hsl = rgb.To<Hsl>();
            H = hsl.H;
            S = hsl.S;
            L = hsl.L;
        }

        public PixelColor(string htmlColor) : this(ColorTranslator.FromHtml(htmlColor))
        {
        }

        public Color LEDColor
        {
            get
            {
                IRgb rgb = ToRgb();
                return Color.FromArgb((int)rgb.R, (int)rgb.G, (int)rgb.B);
            }
        }

        public PixelColor Random(double hDelta = 0, double sDelta = 0, double lDelta = 0)
        {
            return new PixelColor(
                ColorUtils.RollHue(H + Rand.Linear(-hDelta, hDelta)),
                ColorUtils.Clamp(S + Rand.Linear(-sDelta, sDelta)),
                ColorUtils.Clamp(L + Rand.Linear(-lDelta, lDelta))
            );
        }

        public override string ToString()
        {
            return $"(H: {H:N0}, S: {S:N2}, L: {L:N2})";
        }
    }

    public static class Rand
    {
        private static readonly Random MyRand = new();

        public static double Linear(double? firstValue = null, double? secondValue = null)
        {
            double minValue, maxValue;

            if (firstValue == null) { minValue = 0; maxValue = 1; }
            else if (secondValue == null) { minValue = 0; maxValue = firstValue.Value; }
            else { minValue = firstValue.Value; maxValue = secondValue.Value; }
            if (maxValue < minValue) { double tmp = maxValue; maxValue = minValue; minValue = tmp; }
            return minValue + MyRand.NextDouble() * (maxValue - minValue);
        }

        public static int Linear(int? firstValue = null, int? secondValue = null)
        {
            int minValue, maxValue;

            if (firstValue == null) { minValue = 0; maxValue = 1; }
            else if (secondValue == null) { minValue = 0; maxValue = firstValue.Value; }
            else { minValue = firstValue.Value; maxValue = secondValue.Value; }
            if (maxValue < minValue) { int tmp = maxValue; maxValue = minValue; minValue = tmp; }
            return MyRand.Next(minValue, maxValue);
        }
    }

    public static class ColorUtils
    {
        public static double Clamp(double value, double minValue = 0, double maxValue = 1)
        {
            return Math.Min(Math.Max(value, minValue), maxValue);
        }

        public static double RollHue(double rawHue)
        {
            double mod = rawHue % 360d;

            return rawHue < 0 ? 360d - mod : mod;
        }

        public static double Lerp(double start, double end, double progress)
        {
            double retval = start + (end - start) * progress;
            return retval;
        }

        public static PixelColor Lerp(PixelColor start, PixelColor end, double progress)
        {
            progress = Math.Min(1, Math.Max(progress, 0));

            return new PixelColor
            {
                H = Lerp(start.H, end.H, progress),
                S = Lerp(start.S, end.S, progress),
                L = Lerp(start.L, end.L, progress)
            };
        }

        public static double ListLerp(List<double> lerpList, double progress)
        {
            double realIndex = (lerpList.Count - 1) * progress;
            int intIndex = (int)Math.Floor(realIndex);

            if (intIndex >= lerpList.Count - 1)
            {
                return lerpList[lerpList.Count - 1];
            }

            return ColorUtils.Lerp(lerpList[intIndex], lerpList[intIndex + 1], realIndex - intIndex);
        }
    }
}
