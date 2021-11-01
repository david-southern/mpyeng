#include "common.h"

bool SHOW_CHASERS = true;

#define MAX_CHASERS_PER_SEGMENT 20

float chaserPosition[REACTOR_SEGMENTS * MAX_CHASERS_PER_SEGMENT];
float chaserSpeedPixPerSec[REACTOR_SEGMENTS * MAX_CHASERS_PER_SEGMENT];

CruiseParam chasersPerSegmentParam(1, 10, EaseLinear);
// Negative speeds create downwards floating chasers
// CruiseParam chaserSpeedSecondsPerSegment(-10, -5, -2, -0.5, EaseLinear);
CruiseParam chaserSpeedParam(-10, -5, -5, -2, EaseLinear); // // Time in seconds for the pulse to traverse the core

CruiseParam chaserHueParam(HUE_ORANGE, HUE_RED, EaseInCubic);
CruiseParam chaserSaturationParam(255, 200, EaseInCubic);
CruiseParam chaserValueParam(255);

CRGB CHASER_COLOR = CHSV(chaserHueParam.Value(), chaserSaturationParam.Value(), chaserValueParam.Value());

int chasersPerSegment = 0;

void chaser_setup()
{
  if(!SHOW_CHASERS) {
    return;
  }

  chaser_update_params();
}

void chaser_update_params()
{
  if(!SHOW_CHASERS) {
    return;
  }

  int prevChasersPerSegment = chasersPerSegment;

  chasersPerSegment = chasersPerSegmentParam.Value();

  if (chasersPerSegment > prevChasersPerSegment)
  {
    for (unsigned int segmentIndex = 0; segmentIndex < REACTOR_SEGMENTS; segmentIndex++)
    {
      for (unsigned int chaserIndex = prevChasersPerSegment; chaserIndex < chasersPerSegment; chaserIndex++)
      {
        int flatIndex = segmentIndex * MAX_CHASERS_PER_SEGMENT + chaserIndex;

        int segmentPos = MoarRandom.randomInt(SEGMENT_SIZE);

        chaserPosition[flatIndex] = segmentPos;
        chaserSpeedPixPerSec[flatIndex] = SEGMENT_SIZE / chaserSpeedParam.RandomValue();
      }
    }
  }

  CHASER_COLOR = CHSV(chaserHueParam.Value(), chaserSaturationParam.Value(), chaserValueParam.Value());

  // Update the chaser speeds
  for (unsigned int segmentIndex = 0; segmentIndex < REACTOR_SEGMENTS; segmentIndex++)
  {
    for (unsigned int chaserIndex = 0; chaserIndex < chasersPerSegment; chaserIndex++)
    {
      int flatIndex = segmentIndex * MAX_CHASERS_PER_SEGMENT + chaserIndex;
      chaserSpeedPixPerSec[flatIndex] = SEGMENT_SIZE / chaserSpeedParam.RandomValue();
    }
  }
}

void chaser_loop(CRGBSet &leds, uint32_t simTime, float secondsElapsed)
{
  if(!SHOW_CHASERS) {
    return;
  }

  for (unsigned int segmentIndex = 0U; segmentIndex < REACTOR_SEGMENTS; segmentIndex++)
  {
    unsigned int segmentOffset = SEGMENT_SIZE * segmentIndex;

    for (unsigned int chaserIndex = 0U; chaserIndex < chasersPerSegment; chaserIndex++)
    {
      unsigned int flatIndex = segmentIndex * MAX_CHASERS_PER_SEGMENT + chaserIndex;

      chaserPosition[flatIndex] += chaserSpeedPixPerSec[flatIndex] * secondsElapsed;

      if (chaserPosition[flatIndex] >= SEGMENT_SIZE || chaserPosition[flatIndex] < 0)
      {
        while (chaserPosition[flatIndex] >= SEGMENT_SIZE)
        {
          chaserPosition[flatIndex] -= SEGMENT_SIZE;
        }
        while (chaserPosition[flatIndex] < 0)
        {
          chaserPosition[flatIndex] += SEGMENT_SIZE;
        }

        chaserSpeedPixPerSec[flatIndex] = SEGMENT_SIZE / chaserSpeedParam.RandomValue();
      }

      int pixelPosition = chaserPosition[flatIndex] + segmentOffset;

      if (SEGMENTS_ALTERNATE_DIRECTION && segmentIndex % 2 == 1)
      {
        pixelPosition = segmentOffset + SEGMENT_SIZE - 1 - chaserPosition[flatIndex];
      }

      if (pixelPosition >= NUM_LEDS)
      {
        Logger.Warning("Reactor:Chaser: pixelPosition overflow: index: %d for segment: %d", pixelPosition, segmentIndex);
        continue;
      }

      leds[pixelPosition] = CHASER_COLOR;
    }
  }
}
