using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

using Helpers;

namespace PiController
{
    public class WarpCorePulse : IAnimationEffect
    {
        private const int MAX_STROBE_PULSES = 1;

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
        /// Width of the pulse as a percentage of the core length
        /// </summary>
        private readonly DependentDouble PulseWidth;

        private readonly DependentDouble Hue;
        private readonly DependentDouble Sat;
        private readonly DependentDouble Val;
        private readonly HSVColorByDependent PulseColor;

        private List<double> PulsePositions = new();

        private double NextPulseCreation = 0;

        void CreateNewPulse()
        {
            if (PulsePositions.Count >= MAX_STROBE_PULSES)
            {
                return;
            }

            PulsePositions.Add(0);
            NextPulseCreation = lastSimTime + SecondsPerPulse.Value;
        }

        public WarpCorePulse()
        {
            PulseSpeed = new(PowerLevelControlValue, 0.4, 0.4);
            SecondsPerPulse = new(PowerLevelControlValue, 4, 0.4, EasingFunction.CircularEaseOut);
            PulseWidth = new(PowerLevelControlValue, 0.12, 0.04);
            Hue = new(PowerLevelControlValue, HSVColor.HUE_YELLOW, HSVColor.HUE_RED);
            Sat = new(PowerLevelControlValue, 0.77, 1.0);
            Val = new(PowerLevelControlValue, 1.0, 1.0);
            PulseColor = new(Hue, Sat, Val);
        }

        int renders = 0;
        double maxTime = 0;
        double totalTime = 0;

        double lastSimTime = 0;

        public void Render(double powerLevel, double simElapsedTime, List<HSVColor> Pixels, bool showDiags = false)
        {
            renders++;
            Stopwatch diagTimer = Stopwatch.StartNew();

            PowerLevel = powerLevel;

            double elapsedSeconds = simElapsedTime - lastSimTime;
            lastSimTime = simElapsedTime;

            if (simElapsedTime > NextPulseCreation)
            {
                CreateNewPulse();
            }

            int pulseWidth = (int)Math.Min(Math.Floor(PulseWidth.Value * WarpCore.WarpCoreSegmentLength), 1);

            double pulseDelta =  WarpCore.WarpCoreSegmentLength / PulseSpeed.Value;
            double pulseDistance = pulseDelta * elapsedSeconds;

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

                        if (pixelIndex >= WarpCore.WarpCoreSegmentLength)
                        {
                            DeletePulses.Add(pulseIndex);
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

            maxTime = Math.Max(diagTimer.Elapsed.TotalSeconds, maxTime);
            totalTime += diagTimer.Elapsed.TotalSeconds;

            if (showDiags)
            {
                const int diagPix = 42;

                Logger.Info($"WarpCorePulse: Renders: {renders}, MaxTime: {maxTime:N3}, AvgTime: {totalTime / renders:N3}, Pulse count: {PulsePositions.Count}, " +
                    $"Pulse Speed: {PulseSpeed.ValueAtStart}, pulseDelta: {pulseDelta}, pulseDistance: {pulseDistance}, " +
                    $"Pulse[0] Pos: {(PulsePositions.Count > 0 ? (int)PulsePositions[0] : -1)}, " +
                    $"Pix{diagPix} Color: {Pixels[diagPix]}");
                renders = 0;
                maxTime = 0;
                totalTime = 0;
            }
            /*

            for (int pixIndex = 0; pixIndex < Pixels.Count; pixIndex++)
            {
                int diagPix = Pixels.Count / 2;

                int xOffset = pixIndex / StripLength;
                int yOffset = pixIndex % StripLength;

                if (xOffset % 2 == 1)
                {
                    yOffset = StripLength - yOffset;
                }

                PixNoiseX = NoiseX + (xOffset * ScaleX.Value);
                PixNoiseY = NoiseY + (yOffset * ScaleY.Value);

                Pixels[pixIndex] = CoreColor.Value;

                if (showDiags && pixIndex == diagPix)
                {
                    Logger.Info($"WarpCoreFog: Rendering {Pixels.Count} Pixels: " +
                        $"Scale: ({ScaleX.Value},{ScaleY.Value}), " +
                        $"Speed: ({SpeedX.Value},{SpeedY.Value},{SpeedZ.Value}), " +
                        $"Pix{diagPix} Color: {Pixels[pixIndex]}, " +
                        $"Sat({Sat.ControlValue:N3}): {Sat.Value:N3}, SatStart({SatStart.ControlValue:N3}): {SatStart.Value:N3}"
                    );
                }
            }
            */
        }
    }
}
