using Helpers;

using System;
using System.Collections.Generic;

namespace PiController
{
    public class WarpCoreProgress : IAnimationEffect
    {
        public string Name => "WarpCore - Progress";
        public string Description => "Red pixel progress indicator";
        public int RenderOrder => 200;

        public double ProgressPerSecond { get; set; } = 1;

        public WarpCoreProgress()
        {
        }

        private readonly DateTime ProgressStart = DateTime.Now;

        public void Render(double powerLevel, double simElapsedTime, List<HSVColor> Pixels, bool showDiags = false)
        {
            double elapsedSeconds = (DateTime.Now - ProgressStart).TotalSeconds;
            int progressSeconds = ((int)(elapsedSeconds * ProgressPerSecond));
            int progressHours = progressSeconds / 3600;
            int progressMinutes = (progressSeconds / 60) % 60;
            progressSeconds %= 60;

            Pixels[progressSeconds] = HSVColor.Green;
            Pixels[progressMinutes] = HSVColor.Yellow;
            Pixels[progressHours] = HSVColor.Red;
        }
    }
}
