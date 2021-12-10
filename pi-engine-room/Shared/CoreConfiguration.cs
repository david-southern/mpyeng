namespace pi_engine_room.Shared
{
    public class CorePalette
    {
        public string CoreColor { get; set; } = null!;
        public double PowerLevel { get; set; }

        public CorePalette()
        {
        }
    }

    public class CoreConfiguration
    {
        public List<CorePalette> CorePalettes { get; set; } = null!;
        public double PowerLevel { get; set; } = 0;
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
        }
    }

}