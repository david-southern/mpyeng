using Helpers;

using System;

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

        public bool IsLerping => LerpDurationSeconds > 0;

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

                double retval = Utils.Lerp(LerpFrom, LerpTo, lerpProgress);

                return retval;
            }
        }
    }
}
