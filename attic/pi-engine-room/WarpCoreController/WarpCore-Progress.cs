namespace WarpCoreController;

public class WarpCoreProgress : IAnimationEffect
{
    public string Name => "WarpCore - Progress";
    public string Description => "Red pixel progress indicator";

    public bool Enabled { get; set; } = false;
    public int RenderOrder { get; init; } = 999;

    public double ProgressPerSecond { get; set; } = 1;
    public HSVColor SecondsColor { get; set; } = HSVColor.Green;
    public HSVColor MinutesColor { get; set; } = HSVColor.Yellow;
    public HSVColor HoursColor { get; set; } = HSVColor.Red;

    private readonly CoreConfiguration Config;

    public WarpCoreProgress(CoreConfiguration config)
    {
        Config = config;

        RenderOrder = config.ProgressConfig?.RenderOrder ?? RenderOrder;
        ProgressPerSecond = config.ProgressConfig?.ProgressPerSecond ?? ProgressPerSecond;
        SecondsColor = config.ProgressConfig?.SecondsColor == null ? SecondsColor : new HSVColor(config.ProgressConfig.SecondsColor);
        MinutesColor = config.ProgressConfig?.MinutesColor == null ? MinutesColor : new HSVColor(config.ProgressConfig.MinutesColor);
        HoursColor = config.ProgressConfig?.HoursColor == null ? HoursColor : new HSVColor(config.ProgressConfig.HoursColor);

        if(Enabled)
        {
            Logger.Info($"Adding Animation Effect {nameof(WarpCoreProgress)} with config: " +
                $"RenderOrder: {RenderOrder}, ProgressPerSec: {ProgressPerSecond:N2}, " +
                $"SecColor: {SecondsColor}, MinColor: {MinutesColor}, HourColor: {HoursColor}");
        }
    }

    private readonly DateTime ProgressStart = DateTime.Now;

    public void Render(double powerLevel, double simElapsedTime, List<HSVColor> Pixels, bool showDiags = false)
    {
        double elapsedSeconds = (DateTime.Now - ProgressStart).TotalSeconds;
        int progressSeconds = ((int)(elapsedSeconds * ProgressPerSecond));
        int progressHours = progressSeconds / 3600;
        int progressMinutes = (progressSeconds / 60) % 60;
        progressSeconds %= 60;

        Pixels[progressSeconds] = SecondsColor;
        Pixels[progressMinutes] = MinutesColor;
        Pixels[progressHours] = HoursColor;
    }
}
