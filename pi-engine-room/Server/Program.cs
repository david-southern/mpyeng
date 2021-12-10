using Serilog;

Log.Logger = new LoggerConfiguration()
    .WriteTo.Console(outputTemplate: "{Timestamp:yyyy-MM-dd HH:mm:ss.fff} [{Level:u3}]  {SourceContext}: {Message:lj}{NewLine}{Exception}")
    .CreateBootstrapLogger();

Log.Information("Model API pre-initialization beginning");

try
{
    var builder = WebApplication.CreateBuilder(args);

    builder.Host.UseSerilog((ctx, lc) => lc.ReadFrom.Configuration(ctx.Configuration));

    builder.Services.AddSingleton<CoreConfiguration>(builder.Configuration.GetSection("CoreConfiguration").Get<CoreConfiguration>());

    // Learn more about configuring Swagger/OpenAPI at https://aka.ms/aspnetcore/swashbuckle
    builder.Services.AddEndpointsApiExplorer();
    builder.Services.AddSwaggerGen();

    builder.Services.AddRazorPages();

    var app = builder.Build();

    //By default, the ASP.NET Core framework logs multiple information-level events per request. Serilog's request
    //logging streamlines this, into a single message per request, including path, method, timings, status code, and
    //exception.
    app.UseSerilogRequestLogging();

    // Microsoft suggests only allowing the DeveloperExceptionPage when running in a development environment, as it could
    // potentially exposed sensitive information.  However, this API is not intended to be an externally-facing service, it
    // should only be called by the externally-facing website developers. I'm going to leave this on so that we provide
    // useful exception information.
    app.UseDeveloperExceptionPage();
    app.UseSwagger();
    app.UseSwaggerUI();

    app.Logger.LogInformation("Pi Engine Room Controller Starting");

    // Configure the HTTP request pipeline.
    if (app.Environment.IsDevelopment())
    {
        app.UseWebAssemblyDebugging();
    }
    else
    {
        app.UseExceptionHandler("/Error");
    }

    app.UseBlazorFrameworkFiles();
    app.UseStaticFiles();

    app.UseRouting();


    app.MapGet("/api-docs", () => Results.Redirect("/swagger"));

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
        app.Logger.LogInformation($"/config: Updating CoreConfig: {newConfig.SafeJson()}");
        transientConfig.PowerLevel = newConfig.PowerLevel;
        return transientConfig;
    });

    app.MapRazorPages();
    app.MapFallbackToFile("index.html");


    app.Run();
}
catch (Exception ex)
{
    Log.Fatal(ex, "Pi Engine Room Controller unhandled exception");
}
finally
{
    Log.Information($"Pi Engine Room Controller shutdown complete");
    Log.CloseAndFlush();
}