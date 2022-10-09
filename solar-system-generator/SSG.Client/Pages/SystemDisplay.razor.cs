using Microsoft.AspNetCore.Components;
using Microsoft.JSInterop;
using MudBlazor;
using SSG.Client.Services;
using SSG.Helpers;

namespace SSG.Client.Pages;

public partial class SystemDisplay : IDisposable
{
    [Inject] private SSGEventService EventService { get; set; } = null!;

    private bool FileMenuOpen = false;
    private bool SettingsMenuOpen = false;
    private bool LoadDialogVisible = false;
    private DialogOptions LoadDialogOptions = new()
    {
        FullWidth = true,
        CloseButton = true,
        CloseOnEscapeKey = true,
    };
    private object? LoadDialogSelection;

    private SSGSettings Settings = new();

    private CelestialObject[] SolarSystemList = Array.Empty<CelestialObject>();

    private CelestialObject SolarSystem = new("");
    private HashSet<CelestialObject> SolarSystemTree = new();

    protected override async Task OnInitializedAsync()
    {
        await Task.CompletedTask;
        try
        {
            EventService.FileMenuInvoked += FileMenuHandler;
            EventService.SettingsInvoked += SettingsHandler;
            EventService.DownloadScreenshotInvoked += DownloadScreenshotHandler;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Exception loading solar system: {ex.Message}");
        }
    }

    protected override async Task OnAfterRenderAsync(bool firstRender)
    {
        await Task.CompletedTask;
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

    private string ObjectIcon(CelestialObject context)
    {
        return context.IsStar ? Icons.Material.Filled.AutoAwesome : Icons.Material.Filled.BlurCircular;
    }

    private string EndText(CelestialObject context)
    {
        return Utils.FloatLT(context.OrbitalSemiMajorAxis, 1) ? "--" : $"{Constants.AsAU(context.OrbitalSemiMajorAxis):N3}AU";
    }

    private async Task UpdateSystem()
    {
        string solarSystemJson = SolarSystem.SafeJson() ?? "null";
        string settingsJson = Settings.SafeJson() ?? "null";
        await JS.InvokeVoidAsync("SSG.Renderer.render", solarSystemJson, settingsJson);
    }

    private void UpdateSettings()
    {
        string settingsJson = Settings.SafeJson() ?? "null";
        _ = JS.InvokeVoidAsync("SSG.Renderer.updateSettings", settingsJson);
    }

    private async Task UpdateSettingsAsync()
    {
        string settingsJson = Settings.SafeJson() ?? "null";
        await JS.InvokeVoidAsync("SSG.Renderer.updateSettings", settingsJson);
    }
}
