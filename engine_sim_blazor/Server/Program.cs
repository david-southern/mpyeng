using GraphQL.Client.Abstractions;
using GraphQL.Client.Http;
using GraphQL.Client.Serializer.Newtonsoft;

using Serilog;

Log.Logger = new LoggerConfiguration()
    .WriteTo.Console(
        outputTemplate: "{Timestamp:yyyy-MM-dd HH:mm:ss.fff} [{Level:u3}]  {SourceContext}: {Message:lj}{NewLine}{Exception}"
    )
    .WriteTo.File(
        path: "C:/Logs/engine-sim.log",
        outputTemplate: "{Timestamp:yyyy-MM-dd HH:mm:ss.fff} [{Level:u3}]  {SourceContext}: {Message:lj}{NewLine}{Exception}",
        shared: true,
        buffered: false)
    .CreateBootstrapLogger();

Log.Information("EngineSim pre-initialization beginning");

try
{
    var builder = WebApplication.CreateBuilder(args);

    builder.Host.UseSerilog((ctx, lc) => lc.ReadFrom.Configuration(ctx.Configuration));

    builder.Host.UseSerilog((ctx, lc) => lc.ReadFrom.Configuration(ctx.Configuration));

    // Add services to the container.
    builder.Services.AddSingleton<BackgroundTaskManager>();
    builder.Services.AddHostedService(provider => provider.GetService<BackgroundTaskManager>());

    builder.Services.AddScoped<IGraphQLClient>(s => new GraphQLHttpClient(
        builder.Configuration["GraphQLURI"], new NewtonsoftJsonSerializer()));
    builder.Services.AddScoped<GraphQLConsumer>();

    builder.Services.AddRazorPages();

    var app = builder.Build();

    //By default, the ASP.NET Core framework logs multiple information-level events per request.
    //Serilog's request logging streamlines this, into a single message per request, including path,
    //method, timings, status code, and exception.
    app.UseSerilogRequestLogging();

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
    app.MapFallbackToFile("index.html");

    app.MapAPIEndpoints();
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