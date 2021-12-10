using Microsoft.Extensions.Hosting;

using System;
using System.Threading;
using System.Threading.Tasks;

using Helpers;

namespace PiController
{
    public class AnimationService : BackgroundService
    {
        public const double AnimationFramesPerSecond = 90;

        private readonly WarpCore Core = WarpCore.Instance;

        public AnimationService()
        {
        }

        protected override async Task ExecuteAsync(CancellationToken stoppingToken)
        {
            Logger.Info("AnimationService starting.");

            await RenderWorker(stoppingToken);
        }

        private static double DiagsIntervalSeconds = 10;
        private static DateTime LastDiags = DateTime.Now;
        private static int frameCount = 0;

        private static void CheckFrameRate(string desc = "")
        {
            frameCount++;
            double elapsedSeconds = (DateTime.Now - LastDiags).TotalSeconds;
            if (elapsedSeconds > DiagsIntervalSeconds)
            {
                string message = $"CheckFrameRate({desc}): elapsed: {elapsedSeconds:N3}, " +
                    $"frames: {frameCount}, req-rate: {frameCount / elapsedSeconds:N3} " +
                    $"- rendered: {rpi_ws281x.WS281x.framesRendered:N0}, skipped: {rpi_ws281x.WS281x.framesSkipped:N0}, " +
                    $"act-rate: {rpi_ws281x.WS281x.framesRendered / elapsedSeconds:N3}";
                LastDiags = DateTime.Now;
                frameCount = 0;
                rpi_ws281x.WS281x.framesRendered = 0;
                rpi_ws281x.WS281x.framesSkipped = 0;

                // Logger.Info(message);
            }
        }

        private Task RenderWorker(CancellationToken stoppingToken)
        {
            try
            {
                Logger.Info("RenderWorker is starting");

                while (!stoppingToken.IsCancellationRequested)
                {
                    Core.Animate();
                    CheckFrameRate("AnimationController");
                }

                Logger.Info("RenderWorker is exiting");
                Core.Dispose();
                Thread.Sleep(1000);
            }
            catch (Exception ex)
            {
                Logger.Error($"AnimationController.DoWork caught exception: {ex}");
            }

            return Task.CompletedTask;
        }

        public override async Task StopAsync(CancellationToken stoppingToken)
        {
            try
            {
                Logger.Info("AnimationService Service is stopping.");
                await base.StopAsync(stoppingToken);
            }
            catch (Exception ex)
            {
                Logger.Error($"AnimationController.StopAsync caught exception: {ex}");
            }
        }
    }
}
