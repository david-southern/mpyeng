using Microsoft.AspNetCore.Components.Web;
using Microsoft.AspNetCore.Components.WebAssembly.Hosting;
using SSG.Client;
using MudBlazor.Services;
using SSG.Client.Services;

var builder = WebAssemblyHostBuilder.CreateDefault(args);
builder.RootComponents.Add<App>("#app");
builder.RootComponents.Add<HeadOutlet>("head::after");

builder.Services.AddSingleton<SSGEventService>();

builder.Services.Configure<AppConfiguration>(builder.Configuration.GetSection(AppConfiguration.ConfigSectionName));
builder.Services.AddScoped<ConfigurationService>();
builder.Services.AddScoped<SSGAPIClient>();


builder.Services.AddScoped(sp => new HttpClient { BaseAddress = new Uri(builder.HostEnvironment.BaseAddress) });
builder.Services.AddMudServices();

await builder.Build().RunAsync();