namespace Server;

public class APIEndpoints
{
    public static void ConfigureAPIEndpoints(WebApplication app)
    {
        app.MapGet("/api-docs", () => Results.Redirect("/swagger"));

        WarpCore core = WarpCore.Instance;

        app.MapGet("/animation-frame", () =>
        {

            return core.GetCoreBitmapData();
        });

        WarpCore Core = WarpCore.Instance;

        CoreConfiguration initialConfig;
        CoreConfigurationViewModel currentConfig;

        using (var serviceScope = app.Services.CreateScope())
        {
            var services = serviceScope.ServiceProvider;
            initialConfig = services.GetRequiredService<CoreConfiguration>();
            currentConfig = new CoreConfigurationViewModel(initialConfig);
            Core.PowerLevel = currentConfig.PowerLevel;
            Core.TimeScale = currentConfig.TimeScale;
            Core.BrightnessScale = currentConfig.BrightnessScale;
        }

        app.MapGet("/config", () =>
        {
            return currentConfig;
        });

        app.MapPost("/config", (CoreConfigurationViewModel newConfig) =>
        {
            currentConfig = newConfig;
            Core.PowerLevel = currentConfig.PowerLevel;
            Core.TimeScale = currentConfig.TimeScale;
            Core.BrightnessScale = currentConfig.BrightnessScale;
            return currentConfig;
        });
    }

}
