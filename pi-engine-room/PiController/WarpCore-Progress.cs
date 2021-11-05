using ColorMine.ColorSpaces;

using rpi_ws281x;

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.Linq;
using System.Threading.Tasks;

namespace PiController
{
    public class WarpCoreProgress : IAnimationEffect
    {
        public string Name => "WarpCore - Progress";
        public string Description => "Red pixel progress indicator";
        public List<AnimationParameter> Parameters => new();
        public int RenderOrder => 200;

        public readonly AnimationParameter ProgressPerSecond = new("Progress Per Second", "How many pixels should the progress meter advance every second", 1);

        public WarpCoreProgress()
        {
            Parameters.Add(ProgressPerSecond);
        }

        private readonly DateTime ProgressStart = DateTime.Now;

        public void Render(List<PixelColor> Pixels, bool showDiags = false)
        {
            double elapsedSeconds = (DateTime.Now - ProgressStart).TotalSeconds;
            int progressSeconds = ((int)(elapsedSeconds * ProgressPerSecond.Value));
            int progressHours = progressSeconds / 3600;
            int progressMinutes = (progressSeconds / 60) % 60;
            progressSeconds %= 60;

            Pixels[progressSeconds] = PixelColor.Green;
            Pixels[progressMinutes] = PixelColor.Yellow;
            Pixels[progressHours] = PixelColor.Red;
        }
    }
}
