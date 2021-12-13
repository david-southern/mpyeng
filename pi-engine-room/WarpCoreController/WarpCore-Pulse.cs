using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

using Helpers;

namespace PiController
{
    public class WarpCorePulse : IAnimationEffect
    {
        private const int MAX_STROBE_PULSES = 10;

        public string Name => "WarpCore - Pulse";
        public string Description => "A pulse that strobes from the bottom of the core to the top, increasing in frequency as the power level increases";
        public int RenderOrder => 900;

        private double PowerLevel;
        private double PowerLevelControlValue()
        {
            return PowerLevel;
        }

        /// <summary>
        /// The time (in seconds) it takes for the pulse to travel from the bottom of the core to the top
        /// </summary>
        private readonly DependentDouble PulseSpeed;
        private readonly DependentDouble SecondsPerPulse;
        /// <summary>
        /// Width of the pulse as the number of "y-axis" rows of LEDs
        /// </summary>
        private readonly DependentDouble PulseWidth;

        private readonly DependentDouble Hue;
        private readonly DependentDouble Sat;
        private readonly DependentDouble Val;
        private readonly HSVColorByDependent PulseColor;

        private List<double> PulsePositions = new();

        private double NextPulseCreation = 0;

        void CreateNewPulse(int pulseWidth)
        {
            if (PulsePositions.Count >= MAX_STROBE_PULSES)
            {
                return;
            }

            PulsePositions.Add(-pulseWidth);
            NextPulseCreation = lastSimTime + SecondsPerPulse.Value;
        }

        public WarpCorePulse()
        {
            PulseSpeed = new(PowerLevelControlValue, 0.4, 0.4);
            SecondsPerPulse = new(PowerLevelControlValue, 1, 0.15);
            PulseWidth = new(PowerLevelControlValue, 12, 3);
            Hue = new(PowerLevelControlValue, HSVColor.HUE_YELLOW, HSVColor.HUE_RED, EasingFunction.CircularEaseIn);
            Sat = new(PowerLevelControlValue, 0.77, 1.0);
            Val = new(PowerLevelControlValue, 1.0, 1.0);
            PulseColor = new(Hue, Sat, Val);
        }

        double lastSimTime = 0;

        public void Render(double powerLevel, double simElapsedTime, List<HSVColor> Pixels, bool showDiags = false)
        {
            PowerLevel = powerLevel;

            double elapsedSeconds = simElapsedTime - lastSimTime;
            lastSimTime = simElapsedTime;

            int pulseWidth = (int)Math.Max(Math.Floor(PulseWidth.Value), 1);

            if (simElapsedTime > NextPulseCreation)
            {
                CreateNewPulse(pulseWidth);
            }

            double pulseDistance = WarpCore.WarpCoreSegmentLength / PulseSpeed.Value * elapsedSeconds;

            HashSet<int> DeletePulses = new();

            for (int pulseIndex = 0; pulseIndex < PulsePositions.Count; pulseIndex++)
            {
                // if (showPulseDiags && pulseIndex == 0)
                // {
                //   Logger.Info(F("Updating Pulse: %d segments, pos: %f, speed: %f, width: %d, elapsed: %f"),
                //               REACTOR_SEGMENTS, CHASERS_PER_SEGMENT, pulsePos, pulseSpeedPixPerSecond, (int)pulseWidth, secondsElapsed);
                // }



                PulsePositions[pulseIndex] += pulseDistance;

                if (PulsePositions[pulseIndex] >= WarpCore.WarpCoreSegmentLength)
                {
                    DeletePulses.Add(pulseIndex);
                    continue;
                }

                for (int segmentIndex = 0; segmentIndex < WarpCore.WarpCoreSegmentCount; segmentIndex++)
                {
                    int segmentOffset = WarpCore.WarpCoreSegmentLength * segmentIndex;

                    for (int pulsePixelIndex = 0; pulsePixelIndex < pulseWidth; pulsePixelIndex++)
                    {
                        int pixelIndex = (int)(PulsePositions[pulseIndex] + pulsePixelIndex);

                        if (pixelIndex < 0 || pixelIndex >= WarpCore.WarpCoreSegmentLength)
                        {
                            continue;
                        }

                        // The segments are wired in alternating top-to-bottom directions.  Adjust the pixel index to
                        // take this into account
                        if (segmentIndex % 2 == 1)
                        {
                            pixelIndex = segmentOffset + WarpCore.WarpCoreSegmentLength - 1 - pixelIndex;
                        }
                        else
                        {
                            pixelIndex += segmentOffset;
                        }

                        if (pixelIndex >= WarpCore.WarpCorePixelCount)
                        {
                            Logger.Warn("Reactor:Strobe: pixelIndex overflow: index: {pixelIndex} for segment: {segmentIndex}, pulsePos: {allPulsePos[pulseIndex]}, pulsePixelIndex: {pulsePixelIndex}");
                            DeletePulses.Add(pulseIndex);
                            continue;
                        }
                        Pixels[pixelIndex] = PulseColor.Value;
                    }
                }
            }

            foreach (int delIndex in DeletePulses)
            {
                PulsePositions.RemoveAt(delIndex);
            }

            if (showDiags)
            {
                const int diagPix = 42;

                Logger.Info($"WarpCorePulse({simElapsedTime:N2}): Pulse count: {PulsePositions.Count}, " +
                    $"Pulse Freq: {SecondsPerPulse.Value:N2}, " +
                    $"Next Pulse: {NextPulseCreation:N2}, " +
                    $"Pulse Speed: {PulseSpeed.Value:N2}, " +
                    $"Pulse[0] Pos: {(PulsePositions.Count > 0 ? (int)PulsePositions[0] : -1)}, " +
                    $"Pix{diagPix} Color: {Pixels[diagPix]}");
            }
        }
    }
}
