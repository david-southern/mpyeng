using Microsoft.AspNetCore.ResponseCompression;

using Serilog;

Log.Logger = new LoggerConfiguration()
    .WriteTo.Console(outputTemplate: "{Timestamp:yyyy-MM-dd HH:mm:ss.fff} [{Level:u3}]  {SourceContext}: {Message:lj}{NewLine}{Exception}")
    .WriteTo.File(path: "pi-engine-room.log", outputTemplate: "{Timestamp:yyyy-MM-dd HH:mm:ss.fff} [{Level:u3}]  {SourceContext}: {Message:lj}{NewLine}{Exception}", shared: true, buffered: false)
    .CreateBootstrapLogger();

Log.Information("EngineSim pre-initialization beginning");

try
{
    var builder = WebApplication.CreateBuilder(args);

    builder.Host.UseSerilog((ctx, lc) => lc.ReadFrom.Configuration(ctx.Configuration));

    // Add services to the container.

    builder.Services.AddSingleton<CommsManager>();
    builder.Services.AddHostedService(provider => provider.GetService<CommsManager>());


    builder.Services.AddControllersWithViews();
    builder.Services.AddRazorPages();

    var app = builder.Build();

    //By default, the ASP.NET Core framework logs multiple information-level events per request.
    //Serilog's request logging streamlines this, into a single message per request, including path,
    //method, timings, status code, and exception.
    app.UseSerilogRequestLogging();

    // Microsoft suggests only allowing the DeveloperExceptionPage when running in a development
    // environment, as it could potentially exposed sensitive information.  This API is not intended
    // to be an externally-facing service, it should only be called by the externally-facing website
    // developers. I'm going to leave this on so that we provide useful exception information.
    app.UseDeveloperExceptionPage();

    app.Logger.LogInformation("EngineSim Starting");

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


    app.MapRazorPages();
    app.MapControllers();
    app.MapFallbackToFile("index.html");

    app.Run();
}
catch (Exception ex)
{
    Log.Fatal(ex, "EngineSim Controller unhandled exception");
}
finally
{
    Log.Information($"EngineSim shutdown complete");
    Log.CloseAndFlush();
}