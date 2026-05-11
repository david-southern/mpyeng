using System.Runtime.InteropServices;

using rpi_ws281x;

namespace Native
{
    [StructLayout(LayoutKind.Sequential)]
#pragma warning disable IDE1006 // Naming Styles - don't complain that the type doesn't start with an uppercase letter
    internal struct ws2811_t
#pragma warning restore IDE1006 // Naming Styles
    {
        public long render_wait_time;
        public IntPtr device;
        public IntPtr rpi_hw;
        public uint freq;
        public int dmanum;
        public ws2811_channel_t channel_0;
        public ws2811_channel_t channel_1;
    }

    internal class WS2811Wrapper
    {
        // If we're not on the RasPi, don't try to address the hardware, this will let us test on Windows
        private bool HardwareRender { get; init; } = Utils.OperatingSystem.IsLinux();

        // This has to remain a field rather than a property, as it has to be passed by reference to PInvoke
        private ws2811_t _ws2811;
        private GCHandle WS2811Handle { get; init; }
        private Dictionary<int, Controller> Controllers { get; init; }

        public WS2811Wrapper(Settings settings)
        {
            // save a copy of the controllers - used to update LEDs
            Controllers = new Dictionary<int, Controller>(settings.Controllers);

            _ws2811 = new ws2811_t
            {
                dmanum = settings.DMAChannel,
                freq = settings.Frequency,
                channel_0 = InitChannel(0, settings.Controllers),
                channel_1 = InitChannel(1, settings.Controllers)
            };

            //Pin the object in memory. Otherwise GC will probably move the object to another memory location.
            //This would cause errors because the native library has a pointer on the memory location of the object.
            WS2811Handle = GCHandle.Alloc(_ws2811, GCHandleType.Pinned);

            var initResult = PInvoke.ws2811_init(ref _ws2811);
            if (initResult != ws2811_return_t.WS2811_SUCCESS)
            {
                throw WS281xException.Create(initResult, "initializing");
            }

            // if specified, apply gamma correction
            if (settings.GammaCorrection != null)
            {
                if (settings.Controllers.ContainsKey(0))
                {
                    Marshal.Copy(settings.GammaCorrection.ToArray(), 0, _ws2811.channel_0.gamma, settings.GammaCorrection.Count);
                }

                if (settings.Controllers.ContainsKey(1))
                {
                    Marshal.Copy(settings.GammaCorrection.ToArray(), 0, _ws2811.channel_1.gamma, settings.GammaCorrection.Count);
                }
            }
        }

        /// <summary>
        /// Initialize the channel properties
        /// </summary>
        /// <param name="channelIndex">Index of the channel to initialize</param>
        /// <param name="controllers">Controller Settings</param>
        private static ws2811_channel_t InitChannel(int channelIndex, Dictionary<int, Controller> controllers)
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

        public void Render(bool force = false)
        {
            if (!HardwareRender)
            {
                return;
            }

            int maxLength = 0;

            if (Controllers.ContainsKey(0) && (force || Controllers[0].IsDirty))
            {
                var ledColor = Controllers[0].GetColors(true);
                maxLength = Math.Max(ledColor.Length, maxLength);
                Marshal.Copy(ledColor, 0, _ws2811.channel_0.leds, ledColor.Length);
            }
            if (Controllers.ContainsKey(1) && (force || Controllers[1].IsDirty))
            {
                var ledColor = Controllers[1].GetColors(true);
                maxLength = Math.Max(ledColor.Length, maxLength);
                Marshal.Copy(ledColor, 0, _ws2811.channel_1.leds, ledColor.Length);
            }

            if (maxLength > 0)
            {
                var result = PInvoke.ws2811_render(ref _ws2811);
                if (result != ws2811_return_t.WS2811_SUCCESS)
                {
                    WS281xException ex = WS281xException.Create(result, "rendering");
                    Console.ForegroundColor = ConsoleColor.Red;
                    Console.WriteLine($"WS281x Render Exception: {ex.ErrorCode} - {ex.Message}");
                    Console.ForegroundColor = ConsoleColor.White;
                    throw ex;
                }
                //result = PInvoke.ws2811_wait(ref _ws2811);
                //if (result != ws2811_return_t.WS2811_SUCCESS)
                //{
                //    WS281xException ex = WS281xException.Create(result, "waiting");
                //    Console.ForegroundColor = ConsoleColor.Red;
                //    Console.WriteLine($"WS281x Exception: {ex.ErrorCode} - {ex.Message}");
                //    Console.ForegroundColor = ConsoleColor.White;
                //    throw ex;
                //}
            }
        }

        public void Dispose()
        {
            if (HardwareRender)
            {
                PInvoke.ws2811_fini(ref _ws2811);
                WS2811Handle.Free();
            }
        }
    }
}
