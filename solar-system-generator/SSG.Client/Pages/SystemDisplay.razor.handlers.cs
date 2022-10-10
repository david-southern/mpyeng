using System.Text;
using Humanizer;
using Microsoft.AspNetCore.Components;
using Microsoft.AspNetCore.Components.Forms;
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


    private async void DownloadScreenshotHandler(object? sender, EventArgs args)
    {
        Settings.DownloadImage = true;
        await UpdateSettingsAsync();
        Settings.DownloadImage = false;
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

    public float StarScale
    {
        get
        {
            return Settings.StarScale;
        }
        set
        {
            if (value == Settings.StarScale)
            {
                return;
            }

            Settings.StarScale = value;

            UpdateSettings();
        }
    }

    public float PlanetScale
    {
        get
        {
            return Settings.PlanetScale;
        }
        set
        {
            if (value == Settings.PlanetScale)
            {
                return;
            }

            Settings.PlanetScale = value;

            UpdateSettings();
        }
    }

    public string GridType
    {
        get
        {
            return Settings.GridType;
        }
        set
        {
            if (value == Settings.GridType)
            {
                return;
            }

            Settings.GridType = value;

            UpdateSettings();
        }
    }

    public BackgroundImageData BackgroundImage
    {
        get
        {
            return Settings.BackgroundImage;
        }
        set
        {
            if (value == Settings.BackgroundImage)
            {
                return;
            }

            Settings.BackgroundImage = value;

            UpdateSettings();
        }
    }

    /*
        public float BGBrightness
        {
            get
            {
                return Settings.BackgroundImage.Brightness;
            }
            set
            {
                if (value == Settings.BackgroundImage.Brightness)
                {
                    return;
                }

                Settings.BackgroundImage.Brightness = value;
            }
        }

        public float BGContrast
        {
            get
            {
                return Settings.BackgroundImage.Contrast;
            }
            set
            {
                if (value == Settings.BackgroundImage.Contrast)
                {
                    return;
                }

                Settings.BackgroundImage.Contrast = value;
            }
        }
    */
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
            _ = UpdateSystem();
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
            _ = UpdateSystem();
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
            _ = UpdateSystem();
            StateHasChanged();
        }
    }

    public string EditOrbitalVelocity
    {
        get
        {
            return $"{Constants.AngVelToDays((SelectedObject?.OrbitalVelocity ?? 0))} days";
        }

        set
        {
            if (SelectedObject == null) { return; }

            value = value.ToLower();
            if (value.Contains("days"))
            {
                value = value.Replace("days", "");
            }

            float floatValue = SelectedObject.OrbitalVelocity;

            try
            {
                floatValue = Constants.AngVelFromDays(Convert.ToSingle(value));
            }
            catch { }


            if (Utils.FloatEQ(SelectedObject.OrbitalVelocity, floatValue))
            {
                return;
            }

            SelectedObject.OrbitalVelocity = floatValue;
            _ = UpdateSystem();
            StateHasChanged();
        }
    }

    public string EditPhaseAngle
    {
        get
        {
            return $"{SelectedObject?.PhaseAngle ?? 0} deg";
        }

        set
        {
            if (SelectedObject == null) { return; }

            value = value.ToLower();
            if (value.Contains("deg"))
            {
                value = value.Replace("deg", "");
            }

            float floatValue = SelectedObject.PhaseAngle;

            try
            {
                floatValue = Convert.ToSingle(value);
            }
            catch { }


            if (Utils.FloatEQ(SelectedObject.PhaseAngle, floatValue))
            {
                return;
            }

            SelectedObject.PhaseAngle = floatValue;
            _ = UpdateSystem();
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
            _ = UpdateSystem();
            StateHasChanged();
        }
    }

    public string EditObjectRadius
    {
        get
        {
            if (SelectedObject == null)
            {
                return "";
            }

            float radius = SelectedObject.IsStar ? Constants.AsSolarRadii(SelectedObject.ObjectRadius)
                : Constants.AsEarthRadii(SelectedObject.ObjectRadius);
            string units = SelectedObject.IsStar ? "SR" : "ER";
            return $"{radius:N2} {units}";
        }

        set
        {
            if (SelectedObject == null) { return; }

            value = value.ToLower();
            bool valueIsStar = value.Contains("sr") || (!value.Contains("er") && SelectedObject.IsStar);

            value = value.Replace("er", "").Replace("sr", "");

            float floatValue = SelectedObject.ObjectRadius;

            try
            {
                floatValue = Convert.ToSingle(value);
                floatValue = valueIsStar ? Constants.OfSolarRadius(floatValue) : Constants.OfEarthRadius(floatValue);
            }
            catch { }


            if (Utils.FloatEQ(SelectedObject.ObjectRadius, floatValue))
            {
                return;
            }

            SelectedObject.ObjectRadius = floatValue;
            _ = UpdateSystem();
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
            _ = UpdateSystem();
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
            _ = UpdateSystem();
            StateHasChanged();
        }
    }

    public string EditRingInnerRadius
    {
        get
        {
            return SelectedObject == null || Utils.FloatEQ(SelectedObject.RingInnerRadius, 0) ? ""
                : $"{SelectedObject.RingInnerRadius:N4}";
        }

        set
        {
            if (SelectedObject == null) { return; }

            float floatValue = SelectedObject.RingInnerRadius;

            try
            {
                floatValue = (float)(Utils.SafeDouble(value) ?? 0);
            }
            catch { }

            if (Utils.FloatEQ(SelectedObject.RingInnerRadius, floatValue))
            {
                return;
            }

            SelectedObject.RingInnerRadius = floatValue;
            _ = UpdateSystem();
            StateHasChanged();
        }
    }

    public string EditRingWidth
    {
        get
        {
            return SelectedObject == null || Utils.FloatEQ(SelectedObject.RingWidth, 0) ? ""
                : $"{SelectedObject.RingWidth:N4}";
        }

        set
        {
            if (SelectedObject == null) { return; }

            float floatValue = SelectedObject.RingWidth;

            try
            {
                floatValue = (float)(Utils.SafeDouble(value) ?? 0);
            }
            catch { }

            if (Utils.FloatEQ(SelectedObject.RingWidth, floatValue))
            {
                return;
            }

            SelectedObject.RingWidth = floatValue;
            _ = UpdateSystem();
            StateHasChanged();
        }
    }

    public string EditRingDensity
    {
        get
        {
            return SelectedObject == null || Utils.FloatEQ(SelectedObject.RingDensity, 0) ? ""
                : $"{SelectedObject.RingDensity:N4}";
        }

        set
        {
            if (SelectedObject == null) { return; }

            float floatValue = SelectedObject.RingDensity;

            try
            {
                floatValue = (float)(Utils.SafeDouble(value) ?? 0);
            }
            catch { }

            if (Utils.FloatEQ(SelectedObject.RingDensity, floatValue))
            {
                return;
            }

            SelectedObject.RingDensity = floatValue;
            _ = UpdateSystem();
            StateHasChanged();
        }
    }

    public string EditRingColor
    {
        get
        {
            return SelectedObject?.RingColor ?? "";
        }

        set
        {
            if (SelectedObject == null) { return; }

            if (SelectedObject.RingColor == value)
            {
                return;
            }
            SelectedObject.RingColor = value;
            _ = UpdateSystem();
            StateHasChanged();
        }
    }

    private async Task NewSystem()
    {
        await Task.CompletedTask;
        CloseMenus();
        SolarSystem = CelestialObject.EmptySystem;
        SolarSystem.IsExpanded = true;
        SolarSystemTree.Clear();
        SolarSystemTree.Add(SolarSystem);
        SelectedObject = null;
        await UpdateSystem();
        StateHasChanged();
    }

    private async Task ShowLoadDialog()
    {
        await Task.CompletedTask;
        CloseMenus();
        LoadDialogVisible = true;
    }

    private async Task LoadSystem(InputFileChangeEventArgs e)
    {
        await Task.CompletedTask;
        LoadDialogVisible = false;

        CelestialObject? jsonResult = null;

        string systemJSON = await new StreamReader(e.File.OpenReadStream()).ReadToEndAsync();

        if (systemJSON.HasValue())
        {
            jsonResult = JsonConvert.DeserializeObject<CelestialObject>(systemJSON);
        }

        if (jsonResult == null)
        {
            await DialogService.ShowMessageBox("Load System Error", "The uploaded file was not a SolarSystem");
            return;
        }

        SolarSystem = jsonResult;
        Console.WriteLine($"Loaded solar system: {SolarSystem.Name}");
        SolarSystem.IsExpanded = true;
        SolarSystemTree.Clear();
        SolarSystemTree.Add(SolarSystem);
        SelectedObject = null;
        await UpdateSystem();
        StateHasChanged();
    }

    private async Task LoadPremade(CelestialObject obj)
    {
        await Task.CompletedTask;
        LoadDialogVisible = false;

        SolarSystem = obj.CloneJSON();
        Console.WriteLine($"Premade solar system: {SolarSystem.Name}");
        SolarSystem.IsExpanded = true;
        SolarSystemTree.Clear();
        SolarSystemTree.Add(SolarSystem);
        SelectedObject = null;
        await UpdateSystem();
        StateHasChanged();
    }

    private async void SaveSystem()
    {
        await Task.CompletedTask;
        CloseMenus();
        Console.WriteLine($"Saving solar system: {SolarSystem.Name}");

        string systemJSON = JsonConvert.SerializeObject(SolarSystem);

        byte[] byteArray = Encoding.UTF8.GetBytes(systemJSON);
        var fileStream = new MemoryStream(byteArray);
        var fileName = $"{Utils.SafeFilename(SolarSystem.Name)}.json";

        using var streamRef = new DotNetStreamReference(stream: fileStream);

        await JS.InvokeVoidAsync("SSG.Utils.downloadFileFromStream", fileName, streamRef);
    }

    private async Task AddChild(CelestialObject parent)
    {
        if (parent == null)
        {
            return;
        }
        int childCount = (parent.ChildObjects?.Count ?? 0) + 1;

        float effectiveParentRadius = parent.ObjectRadius * (parent.IsStar ? Settings.StarScale : Settings.PlanetScale);
        float effectiveChildRadius = (effectiveParentRadius / 10) / Settings.PlanetScale;

        CelestialObject newChild = new($"{parent.Name} {childCount.ToRoman()}", parent,
            semiMajorAxis: effectiveParentRadius * childCount * 10, semiMinorAxis: effectiveParentRadius * childCount * 10,
            orbitalVelocity: Constants.AngVelFromDays(parent.ObjectRadius * childCount * 10), orbitalInclination: 0,
            objectMass: Constants.OfEarthMass(1.0F), objectRadius: effectiveChildRadius,
            objectColor: "magenta");

        parent.IsExpanded = true;

        SolarSystemTree.Clear();
        SolarSystemTree.Add(SolarSystem);
        SelectedObject = null;

        await UpdateSystem();
        StateHasChanged();
    }

    private async Task RemoveElement(CelestialObject child)
    {
        if (child.ParentObject == null)
        {
            await NewSystem();
        }
        else
        {
            child.ParentObject?.RemoveChild(child);
            child.ParentObject = null;
        }

        SolarSystemTree.Clear();
        SolarSystemTree.Add(SolarSystem);
        SelectedObject = null;

        await UpdateSystem();
        StateHasChanged();
    }

    public void LookAt(CelestialObject context)
    {
        if(Settings.LookAt == context.Name) {
            Settings.LookAt = null;
        } else {
            Settings.LookAt = context.Name;
        }
        UpdateSettings();
    }

    public async Task ResetZoom()
    {
        Settings.Zoom = 1;
        await UpdateSystem();
    }

    public async Task ResetView()
    {
        Settings.ViewAngleXDegrees = SSGSettings.DEFAULT_VIEW_ANGLE_X;
        Settings.ResetOrbitControls = true;
        await UpdateSystem();
        Settings.ResetOrbitControls = false;
    }
}
