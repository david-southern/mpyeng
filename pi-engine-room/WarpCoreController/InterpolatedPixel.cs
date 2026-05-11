using System.Drawing;

namespace WarpCoreController;

public class InterpolatedPixel
{
    private HSVColor LerpFrom;
    private HSVColor LerpTo;
    private DateTime LerpStart;
    private double LerpDurationSeconds = 0;

    public InterpolatedPixel()
    {
        LerpFrom = LerpTo = HSVColor.Black;
    }

    public InterpolatedPixel(HSVColor color)
    {
        LerpFrom = LerpTo = color;
    }

    public void SetColor(Color targetColor, double setDuration)
    {
        LerpFrom = CurrentColor;
        LerpTo = new HSVColor(targetColor);
        LerpStart = DateTime.Now;
        LerpDurationSeconds = setDuration;
    }

    public void SetColor(string targetColor, double setDuration)
    {
        LerpFrom = CurrentColor;
        LerpTo = new HSVColor(targetColor);
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

    public HSVColor TargetColor => LerpTo;
    public HSVColor CurrentColor
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

            HSVColor retval = Utils.Lerp(LerpFrom, LerpTo, lerpProgress);

            return retval;
        }
    }
}
