using rpi_ws281x;

using System.Drawing;

namespace PiController
{
    public class NeoPixelHardwareRPI : INeoPixelProtocol
    {
        public int LEDCount { get; }

        private readonly Settings RPI_Settings;
        private readonly WS281x RPI_Device;
        private readonly Controller RPI_Controller;
        private readonly Pin RPI_PIN = Pin.Gpio18;

        public NeoPixelHardwareRPI(Pin pin, int ledCount)
        {
            RPI_PIN = pin;
            RPI_Settings = Settings.CreateDefaultSettings();
            RPI_Settings.AddController(ledCount, RPI_PIN, stripType: StripType.WS2811_STRIP_GRB);
            RPI_Device = new(RPI_Settings);
            Controller? controller = RPI_Device.GetController();

            if (controller == null)
            {
                throw new InvalidOperationException($"Null controller returned from RPI_Device.GetController() for pin {RPI_PIN}");
            }

            RPI_Controller = controller;

            LEDCount = ledCount;

            Logger.Info($"NeoPixelHardwareRPI: Creating an RPI NeoPixel protocol on GPIO pin {RPI_PIN} for {ledCount} pixels.");

            ClearStrip();
            Update();
        }

        /// <summary>
        /// Sends the current LED data to the SPI bus
        /// </summary>
        public void Update()
        {
            RPI_Device.Render();
        }

        public void ClearStrip()
        {
            FillStrip(Color.Black);
        }

        public void FillStrip(Color fillColor)
        {
            RPI_Controller.SetAll(fillColor);
        }

        public void SetPixel(int pixel, Color color)
        {
            RPI_Controller.SetLED(pixel, color);
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
                Logger.Info($"NeoPixelHardwareRPI: Disposing the RPI bus NeoPixel protocol on GPIO pin {RPI_PIN}.");
                RPI_Device?.Dispose();
            }

            // Free unmanaged resources (unmanaged objects) here
            // Set large fields to null so they can be detected as unreferenced sooner
        }

    }
}
