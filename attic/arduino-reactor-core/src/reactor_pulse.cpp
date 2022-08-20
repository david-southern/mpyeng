#include "common.h"

bool SHOW_PULSE = true;

#define MAX_STROBE_PULSES 10

CruiseParam pulseHueParam(HUE_YELLOW, HUE_RED, EaseInCubic);
CruiseParam pulseSaturationParam(196, 196, 255, 255, EaseInCubic);
CruiseParam pulseValueParam(255);

CRGB PULSE_COLOR = CHSV(pulseHueParam.Value(), pulseSaturationParam.Value(), pulseValueParam.Value());

CruiseParam pulseSpeedParam(0.4);                    // Time in seconds for the pulse to traverse the core
CruiseParam pulseWidthParam(0.12, 0.04, EaseLinear); // Width of the pulse as a percentage of the core length
CruiseParam pulseFreqParam(4, 0.4, EaseOutCirc);     // Seconds between pulses

int pulseCount = 0;
float allPulsePos[MAX_STROBE_PULSES];
float allPulseSpeedPixPerSecond[MAX_STROBE_PULSES];
float allPulseWidth[MAX_STROBE_PULSES];

long unsigned int nextPulseCreation = 0;

void createNewPulse()
{
  if (pulseCount >= MAX_STROBE_PULSES)
  {
    Logger.Warning(F("Attempted to create a new strobe pulse, but there are already the max number (%d) of pulses"), MAX_STROBE_PULSES);
    return;
  }

  allPulsePos[pulseCount] = 0;
  allPulseSpeedPixPerSecond[pulseCount] = SEGMENT_SIZE / pulseSpeedParam.Value();
  allPulseWidth[pulseCount] = SEGMENT_SIZE * pulseWidthParam.Value();

  float nextPulseMillis = pulseFreqParam.Value() * 1000;
  nextPulseCreation = millis() + nextPulseMillis;

  Logger.Warning(F("PL: %f - Creating new pulse - total of %d pulses, next pulse delay: %d millis"),
                 CorePowerLevel, pulseCount, (int)nextPulseMillis);

  pulseCount++;
}

void deletePulse(int deletePulseIndex)
{
  // Copy the remaining pulses down
  if (deletePulseIndex >= 0 && pulseCount > 0)
  {
    for (int pulseIndex = deletePulseIndex; pulseIndex < pulseCount - 1; pulseIndex++)
    {
      allPulsePos[pulseIndex] = allPulsePos[pulseIndex + 1];
      allPulseSpeedPixPerSecond[pulseIndex] = allPulseSpeedPixPerSecond[pulseIndex + 1];
      allPulseWidth[pulseIndex] = allPulseWidth[pulseIndex + 1];
    }

    pulseCount--;
  }
}

void pulse_setup()
{
  if (!SHOW_PULSE)
  {
    return;
  }

  createNewPulse();
}

void pulse_update_params()
{
  if (!SHOW_PULSE)
  {
    return;
  }

  PULSE_COLOR = CHSV(pulseHueParam.Value(), pulseSaturationParam.Value(), pulseValueParam.Value());
}

void pulse_loop(CRGBSet &leds, uint32_t simTime, float secondsElapsed)
{
  if (!SHOW_PULSE)
  {
    return;
  }

  if (simTime > nextPulseCreation)
  {
    createNewPulse();
  }

  for (int pulseIndex = 0; pulseIndex < pulseCount; pulseIndex++)
  {
    // Quick macros to take care of the array indexing
#define pulsePos allPulsePos[pulseIndex]
#define pulseSpeedPixPerSecond allPulseSpeedPixPerSecond[pulseIndex]
#define pulseWidth allPulseWidth[pulseIndex]
#define pixelHue allPulseHue[pulseIndex]

    // if (showPulseDiags && pulseIndex == 0)
    // {
    //   Logger.Info(F("Updating Pulse: %d segments, pos: %f, speed: %f, width: %d, elapsed: %f"),
    //               REACTOR_SEGMENTS, CHASERS_PER_SEGMENT, pulsePos, pulseSpeedPixPerSecond, (int)pulseWidth, secondsElapsed);
    // }

    pulsePos += pulseSpeedPixPerSecond * secondsElapsed;

    if (pulsePos >= SEGMENT_SIZE)
    {
      deletePulse(pulseIndex);
      continue;
    }

    for (unsigned int segmentIndex = 0U; segmentIndex < REACTOR_SEGMENTS; segmentIndex++)
    {
      unsigned int segmentOffset = SEGMENT_SIZE * segmentIndex;

      for (unsigned int pulsePixelIndex = 0U; pulsePixelIndex < pulseWidth; pulsePixelIndex++)
      {
        unsigned int pixelIndex = pulsePos + pulsePixelIndex;

        if (pixelIndex >= SEGMENT_SIZE)
        {
          continue;
        }

        if (SEGMENTS_ALTERNATE_DIRECTION && segmentIndex % 2 == 1)
        {
          pixelIndex = segmentOffset + SEGMENT_SIZE - 1 - pixelIndex;
        }
        else
        {
          pixelIndex += segmentOffset;
        }

        if (pixelIndex >= NUM_LEDS)
        {
          Logger.Warning("Reactor:Strobe: pixelIndex overflow: index: %d for segment: %d, pulsePos: %d, pulsePixelIndex: %d",
                         pixelIndex, segmentIndex, (int)pulsePos, pulsePixelIndex);
        }
        else
        {
          leds[pixelIndex] = PULSE_COLOR;
        }
      }

      if (segmentOffset > 0)
      {
        leds[segmentOffset] = CRGB::Red;
      }
    }
  }
}