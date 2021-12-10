using rpi_ws281x;

using System;
using System.Collections.Generic;
using System.Linq;

using Helpers;

namespace PiController
{
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

        public const int WarpCorePixelCount = 976;
        public const double PowerChangeDurationSeconds = 2;

        private static readonly Lazy<WarpCore> lazy = new(() => new WarpCore());

        public static WarpCore Instance { get { return lazy.Value; } }

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
                new WarpCoreFog2D(),
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
                DisplayMode = WarpCoreDisplayMode.Animate;
                m_PowerLevel.SetValue(Utils.Clamp(value), PowerChangeDurationSeconds);
            }
        }

        private readonly TimeSpan DiagsInterval = TimeSpan.FromSeconds(1);
        private DateTime LastDiags = DateTime.MinValue;


        public void Clear()
        {
            CoreStrip.Clear();
        }

        public void Animate()
        {
            try
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

                CoreStrip.Set(CorePixels);
                CoreStrip.Update();
            }
            catch (Exception ex)
            {
                Logger.Error($"WarpCore.Animate: Caught excetion: {ex}");
            }
        }

        public void CoreAnimationFrame()
        {
            bool showDiags = false;

            if (DateTime.Now - LastDiags > DiagsInterval)
            {
                LastDiags = DateTime.Now;
                //Logger.Info($"WarpCore: Rendering {CorePixels.Count} pixels @ PowerLevel: {PowerLevel:N3} with Effects: {string.Join(", ", AnimationEffects.Select(ef => ef.Name))}");
                showDiags = true;
            }

            foreach (IAnimationEffect effect in AnimationEffects)
            {
                effect.Render(PowerLevel, CorePixels, showDiags);
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
}
