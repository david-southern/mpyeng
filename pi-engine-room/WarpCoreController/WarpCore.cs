using rpi_ws281x;

using SixLabors.ImageSharp;
using SixLabors.ImageSharp.PixelFormats;

using Color = System.Drawing.Color;

namespace WarpCoreController;

public enum WarpCoreDisplayMode
{
    None,
    ColorTest,
    PixelCount,
    Animate
}

/// <summary>
/// This singleton WarpCore class uses the Lazy Singleton pattern discussed here:
/// * https://garywoodfine.com/singleton-design-pattern-c-net-core/
/// </summary>
public class WarpCore : IDisposable
{
    public static readonly Pin RPI_GPIO_PIN = Pin.Gpio18;

    public const int WarpCoreSegmentCount = 8;
    public const int WarpCoreSegmentLength = 122;
    public const int WarpCorePixelCount = WarpCoreSegmentCount * WarpCoreSegmentLength;

    public const double PowerChangeDurationSeconds = 2;

    private static readonly Lazy<WarpCore> lazy = new(() => new WarpCore());

    public static WarpCore Instance { get { return lazy.Value; } }

    // Make the Core's animation effects run faster or slower - useful for debugging effects
    public double m_TimeScale = 1.0;
    public double TimeScale
    {
        get { return m_TimeScale; }
        set
        {
            if (!m_TimeScale.DoubleEQ(value))
            {
                Logger.Info($"Setting simulation TimeScale to {value:N3}");
            }
            m_TimeScale = value;
        }
    }

    // The LED's are way brighter than my monitor, so a blue that is very visible on the LED
    // array is nearly indistinguishable from the black background of the array.  Scale the
    // value of the bitmap colors to make them more visible
    public double m_BrightnessScale = 1.3;
    public double BrightnessScale
    {
        get { return m_BrightnessScale; }
        set
        {
            if (!m_BrightnessScale.DoubleEQ(value))
            {
                Logger.Info($"Setting simulation BrightnessScale to {value:N3}");
            }
            m_BrightnessScale = value;
        }
    }



    private WarpCore()
    {
        CorePixels = Enumerable.Range(0, WarpCorePixelCount)
            .Select(n => new HSVColor(HSVColor.Black)).ToList();

        CoreStripProtocol = new NeoPixelHardwareRPI(RPI_GPIO_PIN, WarpCorePixelCount);
        Logger.Info($"WarpCore: Finished creating CoreStripProtocol");
        CoreStrip = new PixelStrip(CoreStripProtocol);
        Logger.Info($"WarpCore: Finished creating CoreStrip");

        AnimationEffects = new List<IAnimationEffect>
            {
                new WarpCoreFog2D()
                ,new WarpCorePulse()
                ,new WarpCoreChaser()
                // new WarpCoreProgress()
            };

        AnimationEffects = AnimationEffects.OrderBy(eff => eff.RenderOrder).ToList();
    }

    private readonly List<HSVColor> CorePixels;
    private readonly INeoPixelProtocol CoreStripProtocol;
    private readonly PixelStrip CoreStrip;

    private WarpCoreDisplayMode DisplayMode = WarpCoreDisplayMode.Animate;

    public List<IAnimationEffect> AnimationEffects { get; private set; }

    private string? m_TargetColor;
    public string? TargetColor
    {
        get { return m_TargetColor; }
        set
        {
            m_TargetColor = value;
            DisplayMode = m_TargetColor == null ? WarpCoreDisplayMode.Animate : WarpCoreDisplayMode.ColorTest;
        }
    }

    private readonly InterpolatedValue m_PowerLevel = new();

    public double PowerLevel
    {
        get
        {
            return m_PowerLevel.CurrentValue;
        }

        set
        {
            value = Utils.Clamp(value);

            if (!m_PowerLevel.TargetValue.DoubleEQ(value))
            {
                Logger.Info($"Setting simulation Power Level to {value:N3}");
            }

            DisplayMode = WarpCoreDisplayMode.Animate;
            m_PowerLevel.SetValue(value, PowerChangeDurationSeconds);
        }
    }

    private readonly TimeSpan DiagsInterval = TimeSpan.FromSeconds(1);
    private DateTime LastDiags = DateTime.MinValue;

    /// <summary>
    /// Given an (X, Y) coordinate, return the pixel index of the corresponding LED.  The
    /// coordinate origin is the bottom-left corner of the LED array.
    /// </summary>
    public static int GetPixelIndex(int x, int y)
    {
        if (x < 0 || x >= WarpCoreSegmentCount)
        {
            throw new ArgumentOutOfRangeException(nameof(x), x, $"x must be > 0, < {WarpCoreSegmentCount}");
        }
        if (y < 0 || y >= WarpCoreSegmentLength)
        {
            throw new ArgumentOutOfRangeException(nameof(y), y, $"y must be > 0, < {WarpCoreSegmentLength}");
        }

        // Transform into the LED array's coordinate space.
        int arrayX = WarpCoreSegmentCount - x - 1;
        int arrayY = arrayX % 2 == 1 ? WarpCoreSegmentLength - y - 1 : y;

        return arrayX * WarpCoreSegmentLength + arrayY;
    }

    /// <summary>
    /// Given a pixel index of the LED array, return the (X, Y) coordinate.  The coordinate origin
    /// is the bottom-left corner of the LED array.
    /// </summary>
    public static (int, int) GetCoordinate(int pixelIndex)
    {
        int x = pixelIndex / WarpCoreSegmentLength;
        int y = pixelIndex % WarpCoreSegmentLength;

        if (x % 2 == 1)
        {
            y = WarpCoreSegmentLength - y - 1;
        }

        return (WarpCoreSegmentCount - x - 1, y);
    }

    public string GetCoreBitmapData()
    {
        using var image = new Image<Rgba32>(WarpCoreSegmentCount, WarpCoreSegmentLength);

        lock (CorePixels)
        {
            for (int pixIndex = 0; pixIndex < WarpCorePixelCount; pixIndex++)
            {
                (int x, int y) = GetCoordinate(pixIndex);

                HSVColor hsvColor = new(
                    CorePixels[pixIndex].H,
                    CorePixels[pixIndex].S,
                    CorePixels[pixIndex].V * BrightnessScale
                );
                Color pixColor = hsvColor.RGBColor;

                image[x, WarpCoreSegmentLength - y - 1]
                    = new Rgba32(pixColor.R, pixColor.G, pixColor.B);
            }
        }

        using var ms = new MemoryStream();
        image.SaveAsPng(ms);
        return "data:image/png;base64," + Convert.ToBase64String(ms.GetBuffer());
    }

    public void Clear()
    {
        CoreStrip.Clear();
    }

    public void Animate()
    {
        try
        {
            lock (CorePixels)
            {
                switch (DisplayMode)
                {
                    case WarpCoreDisplayMode.ColorTest:
                        HSVColor testColor = new(TargetColor ?? "#00FF00");
                        for (int pixIndex = 0; pixIndex < WarpCorePixelCount; pixIndex++)
                        {
                            CorePixels[pixIndex] = testColor;
                        }
                        break;

                    case WarpCoreDisplayMode.PixelCount:
                        for (int pixIndex = 0; pixIndex < WarpCorePixelCount; pixIndex++)
                        {
                            string pixColor = "#000000";

                            if (pixIndex > WarpCorePixelCount - 10) { pixColor = "#0000ff"; }
                            if (pixIndex % 10 == 0) { pixColor = pixColor = "#00ff00"; }
                            if (pixIndex % 50 == 0) { pixColor = pixColor = "#ff0000"; }

                            CorePixels[pixIndex] = new HSVColor(pixColor);
                        }
                        break;

                    case WarpCoreDisplayMode.Animate:
                        CoreAnimationFrame();
                        break;
                }
            }

            CoreStrip.Set(CorePixels);
            CoreStrip.Update();
        }
        catch (Exception ex)
        {
            Logger.Error($"WarpCore.Animate: Caught exception: {ex}");
        }
    }

    double SimElapsedTime = 0;

    DateTime LastSimTime = DateTime.Now;

    public void CoreAnimationFrame()
    {
        bool showDiags = false;

        SimElapsedTime += (DateTime.Now - LastSimTime).TotalSeconds * TimeScale;
        LastSimTime = DateTime.Now;


        if (DateTime.Now - LastDiags > DiagsInterval)
        {
            LastDiags = DateTime.Now;
            //Logger.Info($"WarpCore: Rendering {CorePixels.Count} pixels @ PowerLevel: {PowerLevel:N3} with Effects: {string.Join(", ", AnimationEffects.Select(ef => ef.Name))}");
            showDiags = true;
        }

        foreach (IAnimationEffect effect in AnimationEffects)
        {
            effect.Render(PowerLevel, SimElapsedTime, CorePixels, showDiags);
        }
    }

    // The IDispose pattern: The parameterless form of Dispose() is the deterministic dispose - this is the one
    // that other code calls explicitly to tell this object to dispose itself.  The Dispose(bool) form is what the
    // .Net Garbage Collector finalizer calls to dispose this object when it is collected by the GC.  Classes
    // derived from an IDisposable class that need to free up resources should not implement IDispose themselves,
    // but instead should override the Dispose(bool) method, as the initial dispose will be called by the ancestor.
    //
    // Full description here:
    // https://docs.microsoft.com/en-us/dotnet/standard/garbage-collection/implementing-dispose
    public void Dispose()
    {
        Dispose(true);

        // If we have disposed the object, there is no reason for the Garbage Collector to try to dispose it, so we
        // call GC.SuppressFinalize to prevent the GC from trying to dispose us again.  (The GC will still free up
        // this class' managed memory)
        GC.SuppressFinalize(this);
    }

    private bool IsDisposed = false;
    protected virtual void Dispose(bool disposing)
    {
        if (IsDisposed)
        {
            return;
        }
        IsDisposed = true;

        if (disposing)
        {
            // Dispose managed state (managed objects) here
            CoreStrip.Dispose();
        }

        // Free unmanaged resources (unmanaged objects) here
        // Set large fields to null so they can be detected as unreferenced sooner
    }
}
