using ColorMine.ColorSpaces;

using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using System.Threading.Tasks;

namespace PiController
{
    public class InterpolatedPixel
    {
        private PixelColor LerpFrom;
        private PixelColor LerpTo;
        private DateTime LerpStart;
        private double LerpDurationSeconds = 0;

        public InterpolatedPixel()
        {
            LerpFrom = LerpTo = PixelColor.Black;
        }

        public InterpolatedPixel(PixelColor color)
        {
            LerpFrom = LerpTo = color;
        }

        public void SetColor(Color targetColor, double setDuration)
        {
            LerpFrom = CurrentColor;
            LerpTo = new PixelColor(targetColor);
            LerpStart = DateTime.Now;
            LerpDurationSeconds = setDuration;
        }

        public void SetColor(string targetColor, double setDuration)
        {
            LerpFrom = CurrentColor;
            LerpTo = new PixelColor(targetColor);
            LerpStart = DateTime.Now;
            LerpDurationSeconds = setDuration;
        }

        private double LerpProgress
        {
            get
            {
                if (LerpDurationSeconds < double.Epsilon) { return 0; }

                double lerpValue = Math.Min(1.0, (DateTime.Now - LerpStart).TotalSeconds / LerpDurationSeconds);
                return lerpValue;
            }
        }

        public PixelColor TargetColor => LerpTo;
        public PixelColor CurrentColor
        {
            get
            {
                double lerpProgress = LerpProgress;

                if (lerpProgress < double.Epsilon)
                {
                    return LerpTo;
                }

                if (lerpProgress >= 1.0)
                {
                    LerpFrom = LerpTo;
                    LerpDurationSeconds = 0;
                    lerpProgress = 1.0;
                }

                PixelColor retval = ColorUtils.Lerp(LerpFrom, LerpTo, lerpProgress);

                return retval;
            }
        }
    }
}
