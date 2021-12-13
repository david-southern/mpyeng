namespace Shared
{
    public class CorePalette
    {
        public string CoreColor { get; set; } = null!;
        public double PowerLevel { get; set; }

        public CorePalette()
        {
        }
    }z

    public class CoreConfiguration
    {
        public List<CorePalette> CorePalettes { get; set; } = null!;
        public double PowerLevel { get; set; } = 0;
        public double SimTimeScale { get; set; } = 0;
        public double BrightnessScale { get; set; } = 0;
    }

    public class CoreConfigurationViewModel : CoreConfiguration
    {
        public CoreConfigurationViewModel()
        {
        }

        public CoreConfigurationViewModel(CoreConfiguration other)
        {
            this.CorePalettes = other.CorePalettes;
            this.PowerLevel = other.PowerLevel;
            this.SimTimeScale = other.SimTimeScale;
            this.BrightnessScale = other.BrightnessScale;
        }
    }

}