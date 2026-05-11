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

    public abstract class AnimationEffectConfig
    {
        public bool Enabled { get; set; } = true;
        public int? RenderOrder { get; set; }
    }

    public class ChaserConfig : AnimationEffectConfig
    {
        public double MinSpeedXLow { get; set; }
        public double MinSpeedXHigh { get; set; }
        public double SpeedXStartLow { get; set; }
        public double SpeedXStartLowHigh { get; set; }
        public double SpeedXEndLow { get; set; }
        public double SpeedXEndHigh { get; set; }

        public double MinSpeedYLow { get; set; }
        public double MinSpeedYHigh { get; set; }
        public double SpeedYStartLow { get; set; }
        public double SpeedYStartLowHigh { get; set; }
        public double SpeedYEndLow { get; set; }
        public double SpeedYEndHigh { get; set; }

        public double LifetimeStartLow { get; set; }
        public double LifetimeStartHigh { get; set; }
        public double LifetimeEndLow { get; set; }
        public double LifetimeEndHigh { get; set; }

        public double ChaserFreqLow { get; set; }
        public double ChaserFreqHigh { get; set; }

        public double Hue { get; set; }
        public double Sat { get; set; }
        public double Val { get; set; }
    }

    public class ProgressConfig : AnimationEffectConfig
    {
        public double? ProgressPerSecond { get; set; }
        public string? SecondsColor { get; set; }
        public string? MinutesColor { get; set; }
        public string? HoursColor { get; set; }
    }

    public class CoreConfiguration
    {
        public List<CorePalette> CorePalettes { get; set; } = null!;
        public double? PowerLevel { get; set; } = 0;
        public double? FrameRate { get; set; } = 0;
        public double? TimeScale { get; set; } = 0;
        public double? BrightnessScale { get; set; } = 0;
        public ChaserConfig? ChaserConfig { get; set; }
        public ProgressConfig? ProgressConfig { get; set; }
    }

    public class CoreConfigurationViewModel : CoreConfiguration
    {
    }

}