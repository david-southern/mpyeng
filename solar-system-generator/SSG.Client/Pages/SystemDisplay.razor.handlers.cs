using Microsoft.AspNetCore.Components;
using Microsoft.JSInterop;
using MudBlazor;
using SSG.Client.Services;
using SSG.Helpers;

namespace SSG.Client.Pages;

public partial class SystemDisplay : IDisposable
{
    private void CloseMenus()
    {
        FileMenuOpen = false;
        SettingsMenuOpen = false;
    }

    private void ToggleFileMenu()
    {
        FileMenuOpen = !FileMenuOpen;
        SettingsMenuOpen = false;
        StateHasChanged();
    }

    private void FileMenuHandler(object? sender, EventArgs args)
    {
        ToggleFileMenu();
    }

    private void ToggleSettingsMenu()
    {
        SettingsMenuOpen = !SettingsMenuOpen;
        FileMenuOpen = false;
        StateHasChanged();
    }

    private void SettingsHandler(object? sender, EventArgs args)
    {
        ToggleSettingsMenu();
    }

    private CelestialObject? m_SelectedObject;
    public CelestialObject? SelectedObject
    {
        get
        {
            return m_SelectedObject;
        }

        set
        {
            m_SelectedObject = value;
        }
    }


    public float Zoom
    {
        get
        {
            return Settings.Zoom;
        }
        set
        {
            if (value == Settings.Zoom)
            {
                return;
            }

            Settings.Zoom = value;
            UpdateSettings();
        }
    }

    public bool Animate
    {
        get
        {
            return Settings.Animate;
        }
        set
        {
            if (value == Settings.Animate)
            {
                return;
            }

            Settings.Animate = value;
            UpdateSettings();
        }
    }

    public float AnimationSpeed
    {
        get
        {
            return Settings.AnimationSpeed;
        }
        set
        {
            if (value == Settings.AnimationSpeed)
            {
                return;
            }

            Settings.AnimationSpeed = value;

            UpdateSettings();
        }
    }

    public float ViewAngle
    {
        get
        {
            return -Settings.ViewAngleXDegrees;
        }
        set
        {
            if (value == -Settings.ViewAngleXDegrees)
            {
                return;
            }

            Settings.ViewAngleXDegrees = -value;
            UpdateSettings();
        }
    }

    public string EditName
    {
        get
        {
            return SelectedObject?.Name ?? "";
        }

        set
        {
            if (SelectedObject == null || SelectedObject.Name == value)
            {
                return;
            }
            SelectedObject.Name = value;
            StateHasChanged();
        }
    }

    public bool EditIsStar
    {
        get
        {
            return SelectedObject?.IsStar ?? false;
        }

        set
        {
            if (SelectedObject == null || SelectedObject.IsStar == value)
            {
                return;
            }
            SelectedObject.IsStar = value;
            UpdateSystem();
            StateHasChanged();
        }
    }

    public string EditOrbitalSemiMajorAxis
    {
        get
        {
            return $"{Constants.AsAU(SelectedObject?.OrbitalSemiMajorAxis ?? 0)} AU";
        }

        set
        {
            if (SelectedObject == null) { return; }

            value = value.ToLower();
            if (value.Contains("au"))
            {
                value = value.Replace("au", "");
            }

            float floatValue = SelectedObject.OrbitalSemiMajorAxis;

            try
            {
                floatValue = Convert.ToSingle(value);
                floatValue = Constants.OfAU(floatValue);
            }
            catch { }


            if (Utils.FloatEQ(SelectedObject.OrbitalSemiMajorAxis, floatValue))
            {
                return;
            }

            SelectedObject.OrbitalSemiMajorAxis = floatValue;
            UpdateSystem();
            StateHasChanged();
        }
    }

    public string EditOrbitalSemiMinorAxis
    {
        get
        {
            return $"{Constants.AsAU(SelectedObject?.OrbitalSemiMinorAxis ?? 0)} AU";
        }

        set
        {
            if (SelectedObject == null) { return; }

            value = value.ToLower();
            if (value.Contains("au"))
            {
                value = value.Replace("au", "");
            }

            float floatValue = SelectedObject.OrbitalSemiMinorAxis;

            try
            {
                floatValue = Convert.ToSingle(value);
                floatValue = Constants.OfAU(floatValue);
            }
            catch { }


            if (Utils.FloatEQ(SelectedObject.OrbitalSemiMinorAxis, floatValue))
            {
                return;
            }

            SelectedObject.OrbitalSemiMinorAxis = floatValue;
            UpdateSystem();
            StateHasChanged();
        }
    }

    public string EditOrbitalInclination
    {
        get
        {
            return $"{SelectedObject?.OrbitalInclination ?? 0} deg";
        }

        set
        {
            if (SelectedObject == null) { return; }

            value = value.ToLower();
            if (value.Contains("deg"))
            {
                value = value.Replace("deg", "");
            }

            float floatValue = SelectedObject.OrbitalInclination;

            try
            {
                floatValue = Convert.ToSingle(value);
            }
            catch { }


            if (Utils.FloatEQ(SelectedObject.OrbitalInclination, floatValue))
            {
                return;
            }

            SelectedObject.OrbitalInclination = floatValue;
            UpdateSystem();
            StateHasChanged();
        }
    }

    public string EditObjectRadius
    {
        get
        {
            return $"{Constants.AsEarthRadii(SelectedObject?.ObjectRadius ?? 0)} ER";
        }

        set
        {
            if (SelectedObject == null) { return; }

            value = value.ToLower();
            if (value.Contains("er"))
            {
                value = value.Replace("er", "");
            }

            float floatValue = SelectedObject.ObjectRadius;

            try
            {
                floatValue = Convert.ToSingle(value);
                floatValue = Constants.OfEarthRadius(floatValue);
            }
            catch { }


            if (Utils.FloatEQ(SelectedObject.ObjectRadius, floatValue))
            {
                return;
            }

            SelectedObject.ObjectRadius = floatValue;
            UpdateSystem();
            StateHasChanged();
        }
    }

    public string EditObjectColor
    {
        get
        {
            return SelectedObject?.ObjectColor ?? "";
        }

        set
        {
            if (SelectedObject == null) { return; }

            if (SelectedObject.ObjectColor == value)
            {
                return;
            }
            SelectedObject.ObjectColor = value;
            UpdateSystem();
            StateHasChanged();
        }
    }

    public string EditOrbitalColor
    {
        get
        {
            return SelectedObject?.OrbitalColor ?? "";
        }

        set
        {
            if (SelectedObject == null) { return; }

            if (SelectedObject.OrbitalColor == value)
            {
                return;
            }
            SelectedObject.OrbitalColor = value;
            UpdateSystem();
            StateHasChanged();
        }
    }

    private async Task NewSystem()
    {
        await Task.CompletedTask;
        CloseMenus();
        SolarSystem = CelestialObject.EmptySystem;
        SolarSystemTree.Clear();
        SolarSystemTree.Add(SolarSystem);
        SelectedObject = null;
        UpdateSystem();
    }

    private async Task ShowLoadDialog()
    {
        CloseMenus();
        await GetSystemList();
        Console.WriteLine($"Loaded Solar System List: {string.Join(", ", SolarSystemList.Select(co => co.Name))}");
        LoadDialogVisible = true;
    }

    private async Task LoadSystem()
    {
        LoadDialogVisible = false;
        if (!(LoadDialogSelection is CelestialObject selectedSystem))
        {
            await DialogService.ShowMessageBox("Load Error", "No System Selected");
            return;
        }

        Console.WriteLine($"Selected solar system: {selectedSystem.Name}");

        SolarSystem = (await api.LoadSolarSystem(selectedSystem.Name)) ?? CelestialObject.EmptySystem;
        Console.WriteLine($"Loaded solar system: {SolarSystem.Name}");
        SolarSystemTree.Clear();
        SolarSystemTree.Add(SolarSystem);
        SelectedObject = null;
        UpdateSystem();
    }

    private async void SaveSystem()
    {
        CloseMenus();
        Console.WriteLine($"Saving solar system: {SolarSystem.Name}");
        bool result = await api.SaveSolarSystem(SolarSystem);

        string saveMessage = result ? $"System {SolarSystem.Name} saved" : $"An error occurred while trying to save {SolarSystem.Name}";
        _ = DialogService.ShowMessageBox("Save System", saveMessage);
    }
}
