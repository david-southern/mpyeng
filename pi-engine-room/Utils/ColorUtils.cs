using System;
using System.Collections.Generic;
using System.Drawing;

namespace PiController
{
    public class HSVColor
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

        public static readonly HSVColor Black = new(0.0, 0.0, 0.0);
        public static readonly HSVColor White = new(0.0, 0.0, 1.0);

        public static readonly HSVColor Rose = new(HUE_ROSE, 1.0, 1.0);
        public static readonly HSVColor Magenta = new(HUE_MAGENTA, 1.0, 1.0);
        public static readonly HSVColor Violet = new(HUE_VIOLET, 1.0, 1.0);
        public static readonly HSVColor Blue = new(HUE_BLUE, 1.0, 1.0);
        public static readonly HSVColor Azure = new(HUE_AZURE, 1.0, 1.0);
        public static readonly HSVColor Cyan = new(HUE_CYAN, 1.0, 1.0);
        public static readonly HSVColor Turquiose = new(HUE_TURQUOISE, 1.0, 1.0);
        public static readonly HSVColor Green = new(HUE_GREEN, 1.0, 1.0);
        public static readonly HSVColor Chartreuse = new(HUE_CHARTREUSE, 1.0, 1.0);
        public static readonly HSVColor Yellow = new(HUE_YELLOW, 1.0, 1.0);
        public static readonly HSVColor Orange = new(HUE_ORANGE, 1.0, 1.0);
        public static readonly HSVColor Red = new(HUE_RED, 1.0, 1.0);

        public double H { get; }
        public double S { get; }
        public double V { get; }

        private Color CachedRGBColor { get; set; } = Color.Empty;

        public HSVColor()
        {
        }

        public HSVColor(double h, double s, double v)
        {
            H = Utils.Clamp(h);
            S = Utils.Clamp(s);
            V = Utils.Clamp(v);
        }

        public HSVColor(HSVColor other)
        {
            H = other.H;
            S = other.S;
            V = other.V;
        }

        public HSVColor(Color rgbColor)
        {
            double r = rgbColor.R / 255f;
            double g = rgbColor.G / 255f;
            double b = rgbColor.B / 255f;

            double min, max, delta;

            min = Math.Min(r, Math.Min(g, b));
            max = Math.Max(r, Math.Max(g, b));
            delta = max - min;

            V = max;

            if (max != 0) { S = delta / max; }
            else
            {
                S = 0;
                H = 0;
                return;
            }

            if (r == max) { H = (g - b) / delta; }          // Between yellow & magenta 
            else if (g == max) { H = 2 + (b - r) / delta; } // Between cyan & yellow
            else { H = 4 + (r - g) / delta; }               // Between magenta & cyan

            H *= 60;                                        // Convert to degrees

            if (H < 0) { H += 360; }
        }

        public HSVColor(string htmlColor) : this(ColorTranslator.FromHtml(htmlColor))
        {
        }

        public Color RGBColor
        {
            get
            {
                if (CachedRGBColor != Color.Empty) { return CachedRGBColor; }

                if (S == 0)
                {
                    // Zero saturation means that we have a shade of gray
                    int grayLevel = (int)(V * 255);
                    CachedRGBColor = Color.FromArgb(grayLevel, grayLevel, grayLevel);
                    return CachedRGBColor;
                }

                double h = H / 60;          // sector 0 to 5

                double sector = (int)h;
                double frac = h - sector;   // fractional part of h

                double p = V * (1 - S);
                double q = V * (1 - S * frac);
                double t = V * (1 - S * (1 - frac));

                double R = 0, G = 0, B = 0;

                switch (sector)
                {
                case 0: R = V; G = t; B = p; break;
                case 1: R = q; G = V; B = p; break;
                case 2: R = p; G = V; B = t; break;
                case 3: R = p; G = q; B = V; break;
                case 4: R = t; G = p; B = V; break;
                case 5: R = V; G = p; B = q; break;
                }

                CachedRGBColor = Color.FromArgb((int)(R * 255), (int)(G * 255), (int)(B * 255));
                return CachedRGBColor;
            }
        }

        public HSVColor Random(double hDelta = 0, double sDelta = 0, double vDelta = 0)
        {
            return new HSVColor(
                Utils.RollHue(H + Rand.Linear(-hDelta, hDelta)),
                Utils.Clamp(S + Rand.Linear(-sDelta, sDelta)),
                Utils.Clamp(V + Rand.Linear(-vDelta, vDelta))
            );
        }

        public override string ToString()
        {
            return $"(H: {H:N0}, S: {S:N2}, V: {V:N2})";
        }
    }

    public static partial class Utils
    {
        public static double RollHue(double rawHue)
        {
            double mod = rawHue % 360d;

            return rawHue < 0 ? 360d - mod : mod;
        }

        public static HSVColor Lerp(HSVColor start, HSVColor end, double progress)
        {
            progress = Clamp(progress);
            return new HSVColor(Lerp(start.H, end.H, progress), Lerp(start.S, end.S, progress), Lerp(start.V, end.V, progress));
        }
    }
}
