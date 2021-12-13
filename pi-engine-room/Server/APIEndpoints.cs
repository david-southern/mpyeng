
using PiController;

using Serilog;

namespace Server;

public class APIEndpoints
{
    public static ConfigureAPIEndpoints(WebApplication app)
    {
        app.MapGet("/api-docs", () => Results.Redirect("/swagger"));

        WarpCore core = WarpCore.Instance;

        app.MapGet("/animation-frame", () =>
        {

            return core.GetCoreBitmapData();
        });

        WarpCore Core = WarpCore.Instance;

        CoreConfigurationViewModel transientConfig;

        using (var serviceScope = app.Services.CreateScope())
        {
            var services = serviceScope.ServiceProvider;
            transientConfig = new(services.GetRequiredService<CoreConfiguration>());
        }

        app.MapGet("/config", () =>
        {
            app.Logger.LogInformation($"/config: CoreConfig: {transientConfig.SafeJson()}");
            return transientConfig;
        });

        app.MapPost("/config", (CoreConfigurationViewModel newConfig) =>
        {
            app.Logger.LogInformation($"/config: Updating PowerLevel: {newConfig.PowerLevel}");
            transientConfig.PowerLevel = newConfig.PowerLevel;
            Core.PowerLevel = newConfig.PowerLevel;
            return transientConfig;
        });
    }

}
