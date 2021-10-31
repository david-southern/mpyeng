using Native;

using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Threading;
using System.Threading.Tasks;

namespace rpi_ws281x
{
    /// <summary>
    /// Wrapper class to controll WS281x LEDs
    /// </summary>
    public class WS281x : IDisposable
    {
        private readonly Settings Settings;
        private ws2811_t _ws2811;
        private GCHandle _ws2811Handle;
        private Dictionary<int, Controller> _controllers;

        private static readonly SemaphoreSlim RenderManagmentLock = new(1);

        private int[] RenderData0;
        private int[] PendingRenderData0;
        private int[] RenderData1;
        private int[] PendingRenderData1;

        private bool _isDisposingAllowed;

        /// <summary>
        /// Initialize the wrapper
        /// </summary>
        /// <param name="settings">Settings used for initialization</param>
        public WS281x(Settings settings)
        {
            Settings = settings;

            InitializeHardware();

            //Disposing is only allowed if the init was successful.
            //Otherwise the native cleanup function throws an error.
            _isDisposingAllowed = true;
        }

        private void InitializeHardware()
        {
            Console.WriteLine($"{DateTime.Now:yyyy-MM-dd HH:mm:ss.fff} WS281x.InitializeHardware: Initializing WS281x hardware");

            _ws2811 = new ws2811_t
            {
                dmanum = Settings.DMAChannel,
                freq = Settings.Frequency,
                channel_0 = InitChannel(0, Settings.Controllers),
                channel_1 = InitChannel(1, Settings.Controllers)
            };

            //Pin the object in memory. Otherwise GC will probably move the object to another memory location.
            //This would cause errors because the native library has a pointer on the memory location of the object.
            _ws2811Handle = GCHandle.Alloc(_ws2811, GCHandleType.Pinned);

            var initResult = PInvoke.ws2811_init(ref _ws2811);
            if (initResult != ws2811_return_t.WS2811_SUCCESS)
            {
                throw WS281xException.Create(initResult, "initializing");
            }

            // save a copy of the controllers - used to update LEDs
            _controllers = new Dictionary<int, Controller>(Settings.Controllers);

            // if specified, apply gamma correction
            if (Settings.GammaCorrection != null)
            {
                if (Settings.Controllers.ContainsKey(0))
                    Marshal.Copy(Settings.GammaCorrection.ToArray(), 0, _ws2811.channel_0.gamma, Settings.GammaCorrection.Count);
                if (Settings.Controllers.ContainsKey(1))
                    Marshal.Copy(Settings.GammaCorrection.ToArray(), 0, _ws2811.channel_1.gamma, Settings.GammaCorrection.Count);
            }

            Task.Run(RenderWorker);
        }

        private async Task RenderWorker()
        {
            try
            {
                while (true)
                {
                    bool didRender = false;

                    await RenderManagmentLock.WaitAsync();
                    try
                    {
                        if (PendingRenderData0 != null || PendingRenderData1 != null)
                        {
                            RenderData0 = PendingRenderData0;
                            RenderData1 = PendingRenderData1;
                            PendingRenderData0 = null;
                            PendingRenderData1 = null;
                            PushPixels();
                            didRender = true;
                        }
                    }
                    finally
                    {
                        RenderManagmentLock.Release();
                    }

                    if (!didRender)
                    {
                        // If we didn't have anything to render then sleep for a bit - later wait on a signal
                        Thread.Sleep(10);
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"{DateTime.Now:yyyy-MM-dd HH:mm:ss.fff} WS281x.RenderWorker: ERROR: Exception caught: {ex}");

                Console.WriteLine($"{DateTime.Now:yyyy-MM-dd HH:mm:ss.fff} WS281x.RenderWorker: ERROR: Releasing WS281x hardware");
                ReleaseHardware();
                // If we got an error, then wait a few seconds to let everything clear out and re-initialize the hardware
                Thread.Sleep(5000);
                InitializeHardware();
            }
        }

        private void PushPixels()
        {
            if (RenderData0 != null)
            {
                Marshal.Copy(RenderData0, 0, _ws2811.channel_0.leds, RenderData0.Length);
            }

            if (RenderData1 != null)
            {
                Marshal.Copy(RenderData1, 0, _ws2811.channel_1.leds, RenderData1.Length);
            }
            ws2811_return_t result = PInvoke.ws2811_render(ref _ws2811);
            if (result != ws2811_return_t.WS2811_SUCCESS)
            {
                throw WS281xException.Create(result, "rendering");
            }

            result = PInvoke.ws2811_wait(ref _ws2811);
            if (result != ws2811_return_t.WS2811_SUCCESS)
            {
                throw WS281xException.Create(result, "render waiting");
            }
        }

        private async Task RequestRender(int[] pixelData0, int[] pixelData1)
        {
            await RenderManagmentLock.WaitAsync();
            try
            {
                PendingRenderData0 = pixelData0;
                PendingRenderData1 = pixelData1;
            }
            finally
            {
                RenderManagmentLock.Release();
            }
        }

        /// <summary>
        /// Renders the content of the channels
        /// </summary>
        /// <param name="force">Force LEDs to updated - default only updates if when a change is done</param>
        public async Task Render(bool force = false)
        {
            int[] pixData0 = null;
            int[] pixData1 = null;

            if (_controllers.ContainsKey(0) && (force || _controllers[0].IsDirty))
            {
                pixData0 = _controllers[0].GetColors(true);
            }
            if (_controllers.ContainsKey(1) && (force || _controllers[1].IsDirty))
            {
                pixData1 = _controllers[1].GetColors(true);
            }

            if (pixData0 != null || pixData1 != null)
            {
                await RequestRender(pixData0, pixData1);
            }
        }

        /// <summary>
        /// Get the brightness of a controller
        /// </summary>
        /// <param name="controllerId">The ID of the controller (0 or 1)</param>
        /// <returns></returns>
        public int GetBrightness(int controllerId = 0)
        {
            if (!_controllers.ContainsKey(controllerId)) return 0;
            var controller = _controllers[controllerId];
            return controller.Brightness;
        }

        /// <summary>
        /// Update the strip's brightness
        /// </summary>
        /// <param name="brightness">New brightness (0-255)</param>
        /// /// <param name="controllerId">The ID of the controller (0 or 1)</param>
        public void SetBrightness(int brightness, int controllerId = 0)
        {
            if (!_controllers.ContainsKey(controllerId)) return;
            var controller = _controllers[controllerId];

            controller.Brightness = (byte)brightness;
            if (controller.ControllerType == ControllerType.PWM1)
            {
                _ws2811.channel_1.brightness = (byte)brightness;
            }
            else
            {
                _ws2811.channel_0.brightness = (byte)brightness;
            }

            controller.IsDirty = true;
        }

        public int GetLedCount(int controllerId)
        {
            if (!_controllers.ContainsKey(controllerId)) return 0;
            var controller = _controllers[controllerId];
            return controller.LEDCount;
        }

        /// <summary>
        /// Update the number of LEDs in the strip
        /// </summary>
        /// <param name="ledCount">New number of leds</param>
        /// <param name="controllerId">The ID of the controller (0 or 1)</param>
        public void SetLedCount(int ledCount, int controllerId = 0)
        {
            if (!_controllers.ContainsKey(controllerId)) return;
            var controller = _controllers[controllerId];
            controller.LEDCount = ledCount;
            if (controller.ControllerType == ControllerType.PWM1)
            {
                _ws2811.channel_1.count = ledCount;
            }
            else
            {
                _ws2811.channel_0.count = ledCount;
            }
        }

        public Controller GetController(ControllerType controllerType = ControllerType.PWM0)
        {
            int channelNumber = (controllerType == ControllerType.PWM1) ? 1 : 0;
            if (_controllers.ContainsKey(channelNumber) &&
                _controllers[channelNumber].ControllerType == controllerType)
            {
                return _controllers[channelNumber];
            }
            return null;
        }

        /// <summary>
        /// Initialize the channel propierties
        /// </summary>
        /// <param name="channelIndex">Index of the channel tu initialize</param>
        /// <param name="controllers">Controller Settings</param>
        private ws2811_channel_t InitChannel(int channelIndex, Dictionary<int, Controller> controllers)
        {
            ws2811_channel_t channel = new();

            if (controllers.ContainsKey(channelIndex))
            {
                channel.count = controllers[channelIndex].LEDCount;
                channel.gpionum = controllers[channelIndex].GPIOPin;
                channel.brightness = controllers[channelIndex].Brightness;
                channel.invert = Convert.ToInt32(controllers[channelIndex].Invert);

                if (controllers[channelIndex].StripType != StripType.Unknown)
                {
                    //Strip type is set by the native assembly if not explicitly set.
                    //This type defines the ordering of the colors e. g. RGB or GRB, ...
                    channel.strip_type = (int)controllers[channelIndex].StripType;
                }
            }
            return channel;
        }

        private void ReleaseHardware()
        {
            try
            {
                PInvoke.ws2811_fini(ref _ws2811);

                if (_ws2811Handle.IsAllocated)
                {
                    _ws2811Handle.Free();
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"{DateTime.Now:yyyy-MM-dd HH:mm:ss.fff} WS281x.ReleaseHardware: ERROR: Exception caught: {ex}");
            }
        }

        #region IDisposable Support
        private bool disposedValue = false; // To detect redundant calls

        protected virtual void Dispose(bool disposing)
        {
            if (!disposedValue)
            {
                if (disposing)
                {
                    // TODO: dispose managed state (managed objects).
                }

                // TODO: free unmanaged resources (unmanaged objects) and override a finalizer below.
                // TODO: set large fields to null.

                if (_isDisposingAllowed)
                {
                    ReleaseHardware();
                    _isDisposingAllowed = false;
                }

                disposedValue = true;
            }
        }

        // TODO: override a finalizer only if Dispose(bool disposing) above has code to free unmanaged resources.
        ~WS281x()
        {
            // Do not change this code. Put cleanup code in Dispose(bool disposing) above.
            Dispose(false);
        }

        // This code added to correctly implement the disposable pattern.
        public void Dispose()
        {
            // Do not change this code. Put cleanup code in Dispose(bool disposing) above.
            Dispose(true);
            // TODO: uncomment the following line if the finalizer is overridden above.
            // GC.SuppressFinalize(this);
        }
        #endregion
    }
}
