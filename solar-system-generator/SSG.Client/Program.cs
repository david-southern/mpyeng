using Microsoft.AspNetCore.Components.Web;
using Microsoft.AspNetCore.Components.WebAssembly.Hosting;
using SSG.Client;
using MudBlazor.Services;
using SSG.Client.Services;
using Blazored.LocalStorage;

var builder = WebAssemblyHostBuilder.CreateDefault(args);
builder.RootComponents.Add<App>("#app");
builder.RootComponents.Add<HeadOutlet>("head::after");

builder.Services.AddBlazoredLocalStorage();

builder.Services.AddScoped(sp => new HttpClient { BaseAddress = new Uri(builder.HostEnvironment.BaseAddress) });

builder.Services.Configure<AppConfiguration>(builder.Configuration.GetSection(AppConfiguration.ConfigSectionName));
builder.Services.AddScoped<ConfigurationService>();

builder.Services.AddScoped<SSGAPIClient>();
builder.Services.AddSingleton<SSGEventService>();

builder.Services.AddMudServices();

await builder.Build().RunAsync();