namespace Shared
{
    public class CorePalette
    {
        public string CoreColor { get; set; } = null!;
        public double PowerLevel { get; set; }

        public CorePalette()
        {
        }
    }

    public class ChaserConfig
    {

        public double MinSpeedXLow;
        public double MinSpeedXHigh;
        public double SpeedXStartLow;
        public double SpeedXStartLowHigh;
        public double SpeedXEndLow;
        public double SpeedXEndHigh;

        public double MinSpeedYLow;
        public double MinSpeedYHigh;
        public double SpeedYStartLow;
        public double SpeedYStartLowHigh;
        public double SpeedYEndLow;
        public double SpeedYEndHigh;

        public double LifetimeStartLow;
        public double LifetimeStartHigh;
        public double LifetimeEndLow;
        public double LifetimeEndHigh;
        public double ChaserFreqLow;
        public double ChaserFreqHigh;
        public double Hue;
        public double Sat;
        public double Val;

    }

    public class CoreConfiguration
    {
        public List<CorePalette> CorePalettes { get; set; } = null!;
        public double PowerLevel { get; set; } = 0;
        public double FrameRate { get; set; } = 0;
        public double TimeScale { get; set; } = 0;
        public double BrightnessScale { get; set; } = 0;
    }

    public class CoreConfigurationViewModel : CoreConfiguration
    {
        public CoreConfigurationViewModel()
        {
        }

        public CoreConfigurationViewModel(CoreConfiguration other)
        {
            CorePalettes = other.CorePalettes;
            PowerLevel = other.PowerLevel;
            FrameRate = other.FrameRate;
            TimeScale = other.TimeScale;
            BrightnessScale = other.BrightnessScale;
        }
    }

}