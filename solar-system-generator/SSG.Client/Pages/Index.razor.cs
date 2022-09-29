using Microsoft.AspNetCore.Components;
using Microsoft.JSInterop;
using MudBlazor;
using SSG.Client.Services;
using SSG.Helpers;

namespace SSG.Client.Pages;

public partial class Index : IDisposable
{
    [Inject] private SSGEventService EventService { get; set; } = null!;

    protected override async Task OnInitializedAsync()
    {
        try
        {
            EventService.FileMenuInvoked += FileMenuHandler;
            EventService.SettingsInvoked += SettingsHandler;

            SolarSystem = await ssProxy.GetSolarSystem() ?? MockSolarSystemData.TestSystem;
            Console.WriteLine($"Loaded solar system: {SolarSystem.Name}");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Exception loading solar system: {ex.Message}");
            SolarSystem = MockSolarSystemData.TestSystem;
        }
        SolarSystemTree.Add(SolarSystem);
        UpdateSystem();
    }

    protected override async Task OnAfterRenderAsync(bool firstRender)
    {
        if (firstRender)
        {
            string settingsJson = Settings.SafeJson() ?? "null";
            await JS.InvokeVoidAsync("SSG.Renderer.initialize", "ssgCanvas", settingsJson);
        }

        await base.OnAfterRenderAsync(firstRender);
    }

    private bool disposedValue;

    protected virtual void Dispose(bool disposing)
    {
        if (!disposedValue)
        {
            if (disposing)
            {
                EventService.FileMenuInvoked -= FileMenuHandler;
                EventService.SettingsInvoked -= SettingsHandler;
            }

            disposedValue = true;
        }
    }

    public void Dispose()
    {
        // Do not change this code. Put cleanup code in 'Dispose(bool disposing)' method
        Dispose(disposing: true);
        GC.SuppressFinalize(this);
    }

    private bool FileMenuOpen = false;


    private bool SettingsMenuOpen = false;

    private SSGSettings Settings = new();

    private CelestialObject SolarSystem = new("");
    private HashSet<CelestialObject> SolarSystemTree = new();

    private string ObjectIcon(CelestialObject context)
    {
        return context.ObjectMass > Constants.SolarMass / 10 ? Icons.Material.Filled.AutoAwesome :
        Icons.Material.Filled.BlurCircular;
    }

    private string EndText(CelestialObject context)
    {
        return Utils.FloatLT(context.OrbitalSemiMajorAxis, 1) ? "--" : $"{Constants.AsAU(context.OrbitalSemiMajorAxis):N3}AU";
    }

    private void UpdateSystem()
    {
        string solarSystemJson = SolarSystem.SafeJson() ?? "null";
        string settingsJson = Settings.SafeJson() ?? "null";
        _ = JS.InvokeVoidAsync("SSG.Renderer.render", solarSystemJson, settingsJson);
    }

    private void UpdateSettings()
    {
        string settingsJson = Settings.SafeJson() ?? "null";
        _ = JS.InvokeVoidAsync("SSG.Renderer.updateSettings", settingsJson);
    }
}
