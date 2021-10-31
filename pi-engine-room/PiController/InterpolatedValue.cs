using ColorMine.ColorSpaces;

using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using System.Threading.Tasks;

namespace PiController
{
    public class InterpolatedValue
    {
        private double LerpFrom;
        private double LerpTo;
        private DateTime LerpStart;
        private double LerpDurationSeconds = 0;

        public InterpolatedValue()
        {
            LerpFrom = LerpTo = 0;
        }

        public InterpolatedValue(double value)
        {
            LerpFrom = LerpTo = value;
        }

        public void SetValue(double targetValue, double setDuration)
        {
            LerpFrom = CurrentValue;
            LerpTo = targetValue;
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

        public double TargetValue => LerpTo;
        public double CurrentValue
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

                double retval = ColorUtils.Lerp(LerpFrom, LerpTo, lerpProgress);

                return retval;
            }
        }
    }
}
