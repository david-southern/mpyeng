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

        private Task RenderTask;
        private readonly CancellationTokenSource RenderCancelTokenSource;

        private bool HardwareDeviceInitialized;
        private bool AllowRendering;

        /// <summary>
        /// Initialize the wrapper
        /// </summary>
        /// <param name="settings">Settings used for initialization</param>
        public WS281x(Settings settings)
        {
            Settings = settings;
            RenderCancelTokenSource = new CancellationTokenSource();
            // Only dispose the native hardware interface if it was successfully initialized, otherwise it crashes
            HardwareDeviceInitialized = false;
            AllowRendering = false;

            // Don't wait for initialization to finish, we only need to wait if we want to re-initialize again
            _ = InitializeHardware();
        }

        private async Task InitializeHardware()
        {
            if (RenderTask != null)
            {
                await CancelRendering();
            }

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

            // Only dispose the native hardware interface if it was successfully initialized, otherwise it crashes
            HardwareDeviceInitialized = true;
            AllowRendering = true;

            CancellationToken cancelToken = RenderCancelTokenSource.Token;
            RenderTask = Task.Run(() => RenderWorker(cancelToken), cancelToken);
        }

        private double DiagsIntervalSeconds = 1;
        private DateTime LastDiags = DateTime.Now;
        private int frameCount = 0;

        private void RenderWorker(CancellationToken cancelToken)
        {
            try
            {
                while (!cancelToken.IsCancellationRequested)
                {
                    if (AllowRendering)
                    {
                        if (PendingRenderData0 != null)
                        {
                            RenderData0 = PendingRenderData0;
                            PendingRenderData0 = null;
                        }
                        if (PendingRenderData1 != null)
                        {
                            RenderData1 = PendingRenderData1;
                            PendingRenderData1 = null;
                        }

                        PushPixels();
                        frameCount++;
                    }

                    // TODO: Change this to wait on a signal
                    Thread.Sleep(10);

                    double elapsedSeconds = (DateTime.Now - LastDiags).TotalSeconds;
                    if (elapsedSeconds > DiagsIntervalSeconds)
                    {
                        LastDiags = DateTime.Now;
                        Console.WriteLine($"{DateTime.Now:yyyy-MM-dd HH:mm:ss.fff} WS281x.RenderWorker: frame rate: {frameCount / elapsedSeconds:N3}");
                        frameCount = 0;
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"{DateTime.Now:yyyy-MM-dd HH:mm:ss.fff} WS281x.RenderWorker: ERROR: Exception caught: {ex}");
            }

            Console.WriteLine($"{DateTime.Now:yyyy-MM-dd HH:mm:ss.fff} WS281x.RenderWorker: RenderWorker was cancelled");
        }

        private async Task CancelRendering()
        {
            Console.WriteLine($"{DateTime.Now:yyyy-MM-dd HH:mm:ss.fff} WS281x.RenderWorker: Releasing WS281x hardware");

            // Tell the render thread to cancel
            RenderCancelTokenSource.Cancel();

            // Wait for the render thread to finish
            await RenderTask;

            // Clear the render task so that if we are re-initializing it will be recreated correctly.
            RenderTask = null;
        }

        private void PushPixels()
        {
            if (RenderData0 != null)
            {
                Marshal.Copy(RenderData0, 0, _ws2811.channel_0.leds, RenderData0.Length);
                RenderData0 = null;
            }

            if (RenderData1 != null)
            {
                Marshal.Copy(RenderData1, 0, _ws2811.channel_1.leds, RenderData1.Length);
                RenderData1 = null;
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

        /// <summary>
        /// Renders the content of the channels
        /// </summary>
        /// <param name="force">Force LEDs to updated - default only updates if when a change is done</param>
        public void Render(bool force = false)
        {
            if (_controllers.ContainsKey(0) && (force || _controllers[0].IsDirty))
            {
                // TODO: Verify if assignment of this array reference is atomic in .Net - if not the RenderWorker might
                // try to access PendingRenderData0 while it is being assigned.
                PendingRenderData0 = _controllers[0].GetColors(true);
            }

            if (_controllers.ContainsKey(1) && (force || _controllers[1].IsDirty))
            {
                // TODO: Verify if assignment of this array reference is atomic in .Net - if not the RenderWorker might
                // try to access PendingRenderData0 while it is being assigned.
                PendingRenderData1 = _controllers[1].GetColors(true);
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

        private async Task ReleaseHardware()
        {
            try
            {
                Console.WriteLine($"WS281x: Releasing Hardware");
                AllowRendering = false;

                await CancelRendering();

                // Clear the strip before releasing the hardware.  .Net arrays are initialized with the base type's
                // default value (zero in this case) which is what we want here.
                RenderData0 = new int[GetLedCount(0)];
                RenderData1 = new int[GetLedCount(1)];
                PushPixels();

                PInvoke.ws2811_fini(ref _ws2811);

                if (_ws2811Handle.IsAllocated)
                {
                    _ws2811Handle.Free();
                }

                Console.WriteLine($"WS281x: Finished releasing Hardware");
                HardwareDeviceInitialized = false;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"{DateTime.Now:yyyy-MM-dd HH:mm:ss.fff} WS281x.ReleaseHardware: ERROR: Exception caught: {ex}");
            }
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
                if (HardwareDeviceInitialized)
                {
                    // No need to to wait for the release to complete
                    _ = ReleaseHardware();
                }
            }
        }
    }
}
