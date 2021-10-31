using Microsoft.Extensions.Hosting;

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace PiController
{
    public class AnimationService : IHostedService, IDisposable
    {
        public const double AnimationFramesPerSecond = 30;

        private Timer _timer;
        private readonly WarpCore Core = WarpCore.Instance;

        public AnimationService()
        {
        }

        public Task StartAsync(CancellationToken stoppingToken)
        {
            Logger.Info("AnimationService starting.");
            _timer = new Timer(DoWork, null, TimeSpan.Zero, TimeSpan.FromSeconds(1.0 / AnimationFramesPerSecond));
            return Task.CompletedTask;
        }

        //private ArduinoProxy aProxy = new ArduinoProxy(1, 0x42);
        //private byte pingValue = 7;

        //private readonly TimeSpan DiagsInterval = TimeSpan.FromSeconds(1);
        //private DateTime LastDiags = DateTime.MinValue;

        private void DoWork(object state)
        {
            try
            {
                // We don't need to wait for the Animate() call to finish
                _ = Core.Animate();

                //if (DateTime.Now - LastDiags > DiagsInterval)
                //{
                //    LastDiags = DateTime.Now;
                //    aProxy.SendPing(pingValue++);
                //    if(pingValue > 126)
                //    {
                //        pingValue = 7;
                //    }
                //}
            }
            catch (Exception ex)
            {
                Logger.Error($"AnimationController caught exception: {ex}");
            }
        }

        public async Task StopAsync(CancellationToken stoppingToken)
        {
            Logger.Info("AnimationService Service is stopping.");

            _timer?.Change(Timeout.Infinite, 0);
            await Core.Clear();

            Core.Dispose();
        }

        public void Dispose()
        {
            _timer?.Dispose();
        }
    }
}
