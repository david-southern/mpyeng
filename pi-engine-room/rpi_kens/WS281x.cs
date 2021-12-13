using Native;

namespace rpi_ws281x
{
    /// <summary>
    /// Wrapper class to control WS281x LEDs
    /// </summary>
    public class WS281x : IDisposable
    {
        // If we're not on the RasPi, don't try to address the HArdware, this will let us test on Windows
        private bool HardwareRender { get; init; } = Utils.OperatingSystem.IsLinux();

        private WS2811Wrapper? NativeWS2811 { get; init; }

        private Dictionary<int, Controller> Controllers { get; init; }

        private bool _isDisposingAllowed;

        /// <summary>
        /// Initialize the wrapper
        /// </summary>
        /// <param name="settings">Settings used for initialization</param>
        public WS281x(Settings settings)
        {
            if (HardwareRender)
            {
                // Don't even allocate the WS2811Wrapper if we can't write it, the PInvoke.init method sets up internal
                // structures that are needed for this code to run correctly, so keep the reference null so as to fail
                // fast if we call it when we shouldn't.
                NativeWS2811 = new WS2811Wrapper(settings);
            }

            // save a copy of the controllers - used to update LEDs
            Controllers = new Dictionary<int, Controller>(settings.Controllers);

            //Disposing is only allowed if the init was successful.
            //Otherwise the native cleanup function throws an error.
            _isDisposingAllowed = true;
        }

        private static readonly TimeSpan ReportSkippedFramesFrequency = new(0, 1, 0);
        private static DateTime NextSkippedFramesReport = DateTime.MinValue;
        private static DateTime LastSkippedFramesReport = DateTime.MinValue;

        public static int FramesRendered { get; private set; }
        public static int FramesSkipped { get; private set; }

        public static void ResetFrameCount()
        {
            FramesSkipped = 0;
            FramesRendered = 0;
            LastSkippedFramesReport = DateTime.Now;
            NextSkippedFramesReport = LastSkippedFramesReport + ReportSkippedFramesFrequency;
        }

        private bool isRendering = false;

        /// <summary>
        /// Renders the content of the channels
        /// </summary>
        /// <param name="force">Force LEDs to updated - default only updates if when a change is done</param>
        public void Render(bool force = false)
        {
            if (DateTime.Now > NextSkippedFramesReport)
            {
                if (FramesSkipped > 0 && LastSkippedFramesReport > DateTime.MinValue)
                {
                    Logger.Info($"WS281x.Render(): There were {FramesSkipped} skipped frames " +
                        $"(out of {FramesSkipped + FramesRendered} total Render() calls) " +
                        $"during the last {(DateTime.Now - LastSkippedFramesReport).TotalSeconds:N3} seconds.  " +
                        $"Perhaps you should optimize your rendering loop?");
                }

                ResetFrameCount();
            }

            if (isRendering)
            {
                FramesSkipped++;
                return;
            }

            FramesRendered++;

            isRendering = true;
            NativeWS2811?.Render(force);
            isRendering = false;
        }

        /// <summary>
        /// Set all LEDs (on all controllers) to the same color.
        /// </summary>
        /// <param name="color">color to display</param>
        public void SetAll(Color color)
        {
            foreach (var controller in Controllers.Values)
            {
                controller.SetAll(color);
                controller.IsDirty = false;
            }
            Render(true);
        }

        /// <summary>
        /// Clear all LEDs
        /// </summary>
        public void Reset()
        {
            foreach (var controller in Controllers.Values)
            {
                controller.Reset();
                controller.IsDirty = false;
            }
            Render(true);
        }

        public Controller GetController(ControllerType controllerType = ControllerType.PWM0)
        {
            int channelNumber = (controllerType == ControllerType.PWM1) ? 1 : 0;
            if (Controllers.ContainsKey(channelNumber) &&
                Controllers[channelNumber].ControllerType == controllerType)
            {
                return Controllers[channelNumber];
            }
            throw new InvalidOperationException($"No controller found for controllerType {controllerType}");
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
                    NativeWS2811?.Dispose();
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
