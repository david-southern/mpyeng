using System;
using System.Drawing;
using System.Device.Spi;

using Iot.Device.Graphics;
using System.Text;
using Iot.Device.Ws28xx;
using System.Threading.Tasks;

namespace PiController
{
    public interface INeoPixelProtocol : IDisposable
    {
        public int LEDCount { get; }

        /// <summary>
        /// Sends the current LED data to the underlying protocol implementation.
        /// </summary>
        public Task Update();

        /// <summary>
        /// Fill the entire strip with Black pixels.  Does not Update() the strip.
        /// </summary>
        public void ClearStrip();

        /// <summary>
        /// Fill the entire strip with <paramref name="fillColor"/> pixels.  Does not Update() the strip.
        /// </summary>
        public void FillStrip(Color fillColor);

        /// <summary>
        /// Set zero-indexed <paramref name="pixel"/> LED to <paramref name="color"/>.  Does not Update() the strip.
        /// </summary>
        public void SetPixel(int pixel, Color color);
    }
}
