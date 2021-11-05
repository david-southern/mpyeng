using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;

using PiController;

using rpi_ws281x;

using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;

namespace pi_engine_room
{
    public class Program
    {
        public static void Main(string[] args)
        {
            CreateHostBuilder(args).Build().Run();
        }

        public static IHostBuilder CreateHostBuilder(string[] args) =>
            Host.CreateDefaultBuilder(args)
                .ConfigureWebHostDefaults(webBuilder =>
                {
                    webBuilder.UseStartup<Startup>();
                })
                .ConfigureServices(services =>
                {
                    services.AddHostedService<AnimationService>();
                });

        private static void FrameRateTestFog()
        {
            // RasPi FrameRateTest code as of Nov 4, 2021: 16 frames/second
            // ESP32 FrameRateTest code as of Nov 4, 2021: 24 frames/second

            WarpCore.Instance.Clear();

            CancellationTokenSource cts = new();
            CancellationToken token = cts.Token;
            Console.CancelKeyPress += (s, e) =>
            {
                Console.WriteLine($"Frame Rate Test Cancelled");
                e.Cancel = true;
                cts.Cancel();
            };

            Console.WriteLine($"Frame Rate Test");

            while (!token.IsCancellationRequested)
            {
                WarpCore.Instance.Animate();
                CheckFrameRate();
            }

            WarpCore.Instance.Dispose();

            Thread.Sleep(500);

            Console.WriteLine($"Frame Rate Test Ended");
        }

        private static void FrameRateTestWarpColor()
        {
            // RasPi FrameRateTest code as of Nov 4, 2021: 16 frames/second

            WarpCore.Instance.Clear();

            CancellationTokenSource cts = new();
            CancellationToken token = cts.Token;
            Console.CancelKeyPress += (s, e) =>
            {
                Console.WriteLine($"Frame Rate Test Cancelled");
                e.Cancel = true;
                cts.Cancel();
            };

            Console.WriteLine($"Frame Rate Test");

            List<string> testColors = new List<string>() { "#ff0000", "#00ff00", "#0000ff" };
            int testColorIndex = 0;

            while (!token.IsCancellationRequested)
            {
                WarpCore.Instance.TargetColor = testColors[testColorIndex++];
                if (testColorIndex >= testColors.Count)
                {
                    testColorIndex = 0;
                }
                WarpCore.Instance.Animate();
            }

            WarpCore.Instance.Dispose();

            Thread.Sleep(500);

            Console.WriteLine($"Frame Rate Test Ended");
        }

        private static double DiagsIntervalSeconds = 1;
        private static DateTime LastDiags = DateTime.Now;
        private static int frameCount = 0;

        private static void CheckFrameRate(string desc = "")
        {
            frameCount++;
            double elapsedSeconds = (DateTime.Now - LastDiags).TotalSeconds;
            if (elapsedSeconds > DiagsIntervalSeconds)
            {
                Console.WriteLine($"{DateTime.Now:yyyy-MM-dd HH:mm:ss.fff} CheckFrameRate({desc}): frame count: {frameCount}, elapsed seconds: {elapsedSeconds:N3}, frame rate: {frameCount / elapsedSeconds:N3}");
                LastDiags = DateTime.Now;
                frameCount = 0;
            }
        }

        private static void FrameRateTestDirect()
        {
            CancellationTokenSource cts = new();
            CancellationToken token = cts.Token;
            Console.CancelKeyPress += (s, e) =>
            {
                Console.WriteLine($"Frame Rate Test Cancelled");
                e.Cancel = true;
                cts.Cancel();
            };

            Console.WriteLine($"Frame Rate Test");

            int ledCount = 976;

            WarpCoreFog effect = new();

            var settings = Settings.CreateDefaultSettings();
            var channel = settings.AddController(ledCount, Pin.Gpio18, StripType.WS2811_STRIP_GRB);
            using (var device = new WS281x(settings))
            {
                var controller = device.GetController();

                List<PixelColor> Pixels = Enumerable.Range(0, ledCount).Select(n => PixelColor.Red).ToList();

                while (!token.IsCancellationRequested)
                {
                    effect.Render(Pixels);

                    for (int pixelIndex = 0; pixelIndex < ledCount; pixelIndex++) {
                        controller.SetLED(pixelIndex, Pixels[pixelIndex].LEDColor);
                    }
                    
                    // controller.SetAll(Pixels[42].LEDColor);
                    device.Render();

                    CheckFrameRate("WarpCoreFog-Direct");
                }

                device.Reset();

            }

            Thread.Sleep(500);

            Console.WriteLine($"Frame Rate Test Ended");
        }

        // RasPi FrameRateTest code as of Nov 4, 2021: 

        private static void FrameRateTestKens()
        {
            CancellationTokenSource cts = new();
            CancellationToken token = cts.Token;
            Console.CancelKeyPress += (s, e) =>
            {
                Console.WriteLine($"Frame Rate Test Cancelled");
                e.Cancel = true;
                cts.Cancel();
            };

            Console.WriteLine($"Frame Rate Test");

            int ledCount = 976;

            List<Color> testColors = new List<Color>() { Color.Red, Color.Green, Color.Blue };
            int testColorIndex = 0;

            var settings = Settings.CreateDefaultSettings();
            var channel = settings.AddController(ledCount, Pin.Gpio18, StripType.WS2811_STRIP_GRB);
            using (var device = new WS281x(settings))
            {
                var controller = device.GetController();

                while (!token.IsCancellationRequested)
                {
                    controller.SetAll(testColors[testColorIndex++]);
                    device.Render();

                    if (testColorIndex >= testColors.Count)
                    {
                        testColorIndex = 0;
                    }

                    CheckFrameRate("SetAll");
                }

                device.Reset();

            }

            Thread.Sleep(500);

            Console.WriteLine($"Frame Rate Test Ended");
        }

    }
}
