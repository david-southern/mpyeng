using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using System.Threading.Tasks;

namespace PiController
{
    public class PixelStrip : IDisposable
    {
        public int PixelCount { get; }
        public double PixelBrightness { get; set; }
        public INeoPixelProtocol Protocol { get; }

        public List<PixelColor> PixelColors { get; }

        public PixelStrip(INeoPixelProtocol protocol, double pixelBrightness = 1.0)
        {
            Protocol = protocol;
            PixelCount = protocol.LEDCount;
            PixelBrightness = pixelBrightness;
            PixelColors = new List<PixelColor>(PixelCount);
        }

        public void Update()
        {
            Protocol.Update();
        }

        public void Clear()
        {
            Protocol.ClearStrip();
            Protocol.Update();
        }

        public void Fill(PixelColor color)
        {
            Protocol.FillStrip(color.LEDColor);
        }

        public void Set(List<PixelColor> colorData)
        {
            if (colorData?.Count < 1)
            {
                Logger.Error($"NeoPixelStrip: Set strip called with empty colorData");
                return;
            }

            for (int pixelIndex = 0; pixelIndex < colorData.Count; pixelIndex++)
            {
                try
                {
                    Protocol.SetPixel(pixelIndex, colorData[pixelIndex].LEDColor);
                }
                catch (Exception ex)
                {
                    Logger.Error($"Exception setting pixel {pixelIndex} to color: {colorData[pixelIndex]}: {ex}");
                }
            }
        }

        public void Set(List<InterpolatedPixel> colorData)
        {
            for (int pixelIndex = 0; pixelIndex < colorData.Count; pixelIndex++)
            {
                Protocol.SetPixel(pixelIndex, colorData[pixelIndex].CurrentColor.LEDColor);
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
                Clear();
                // Dispose managed state (managed objects) here
                Protocol.Dispose();
            }

            // Free unmanaged resources (unmanaged objects) here
            // Set large fields to null so they can be detected as unreferenced sooner
        }
    }
}
