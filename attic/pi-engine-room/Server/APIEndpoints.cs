namespace Server;

public class APIEndpoints
{
    public static void ConfigureAPIEndpoints(WebApplication app)
    {
        app.MapGet("/api-docs", () => Results.Redirect("/swagger"));

        app.MapGet("/animation-frame", (WarpCore core) =>
        {

            return core.GetCoreBitmapData();
        });

        app.MapGet("/config", (WarpCore core) =>
        {
            return new CoreConfigurationViewModel
            {
                PowerLevel = core.PowerLevel,
                TimeScale = core.TimeScale,
                BrightnessScale = core.BrightnessScale
            };
        });

        app.MapPost("/config", (WarpCore core, CoreConfigurationViewModel newConfig) =>
        {
            core.PowerLevel = newConfig?.PowerLevel ?? core.PowerLevel;
            core.TimeScale = newConfig?.TimeScale ?? core.TimeScale;
            core.BrightnessScale = newConfig?.BrightnessScale ?? core.BrightnessScale;

            return new CoreConfigurationViewModel
            {
                PowerLevel = core.PowerLevel,
                TimeScale = core.TimeScale,
                BrightnessScale = core.BrightnessScale
            };
        });
    }

}
