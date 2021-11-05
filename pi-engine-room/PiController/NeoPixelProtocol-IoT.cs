using System;
using System.Drawing;
using System.Device.Spi;

using Iot.Device.Graphics;
using System.Text;
using Iot.Device.Ws28xx;
using System.Threading.Tasks;

namespace PiController
{
    public class NeoPixelHardwareIoT : INeoPixelProtocol
    {
        public int LEDCount { get; }

        private readonly SpiConnectionSettings SPISettings;
        private readonly SpiDevice SPIDevice;
        private readonly Ws2812b WS2812bStrip;

        public NeoPixelHardwareIoT(int spiBusId, int ledCount)
        {
            SPISettings = new(spiBusId, 0)
            {
                ClockFrequency = 2_400_000,
                Mode = SpiMode.Mode0,
                DataBitLength = 8
            };
            SPIDevice = SpiDevice.Create(SPISettings);
            LEDCount = ledCount;
            WS2812bStrip = new(SPIDevice, LEDCount);

            ClearStrip();

            Logger.Info($"NeoPixelHardwareIoT: Creating an SPI bus NeoPixel protocol on bus {SPISettings.BusId} for {ledCount} pixels.");
        }

        public void Dispose()
        {
            Dispose(true);
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
                Logger.Info($"NeoPixelHardwareIoT: Disposing the SPI bus NeoPixel protocol on bus {SPISettings.BusId}.");
                SPIDevice?.Dispose();
            }

            // Free unmanaged resources (unmanaged objects) here
            // Set large fields to null so they can be detected as unreferenced sooner
        }


        /// <summary>
        /// Sends the current LED data to the SPI bus
        /// </summary>
        public void Update()
        {
            WS2812bStrip.Update();
        }

        public void ClearStrip()
        {
            FillStrip(Color.Black);
        }

        public void FillStrip(Color fillColor)
        {
            for (int fillIndex = 0; fillIndex < LEDCount; fillIndex++)
            {
                SetPixel(fillIndex, fillColor);
            }
        }

        public void SetPixel(int pixel, Color color)
        {
            WS2812bStrip.Image.SetPixel(pixel, 0, color);
        }
    }
}