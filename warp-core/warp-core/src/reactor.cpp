#include "common.h"

// Adjust these constants to configure the parameters of the core lighting

// How many vertical segments is the LED strip broken into
const unsigned int REACTOR_SEGMENTS = 4;

// If true, we will animate pure white LED's that will progress along each section at random speeds.
const bool SHOW_CHASERS = false;

// If true, the "background fog" palette will shift from a dark blue to a nearly blue-white as the cruise level increases.
const bool SHIFT_PALETTE = false;

// If true, the "background fog" twinkle speed will shift increase as the cruise level increases.
const bool SHIFT_TWINKLE_SPEED = true;

// If true, the entire LED strip brightness will increase as the cruise level increases
const bool SHIFT_BRIGHTNESS = false;

// If true, we will render a vertical strobing 'pulse; of white light that will increase in speed and intensity as the
// cruise level increases
const bool STROBE_PULSE = true;

const unsigned int CHASERS_PER_SEGMENT = 3;
// At maximum power, how long should one chaser take to traverse a full segment
const float MAX_CHASER_SPEED_SECONDS_PER_SEGMENT = 0.5;

// At maximum power, how long should one strobe pulse take to traverse a full segment
const float MAX_PULSE_SPEED_SECONDS_PER_SEGMENT = 0.5;
// At maximum power, how what percentage of the segment should one strobe pulse occupy
const float MAX_PULSE_WIDTH = 0.1;

// Set this flag to true if the segments are arranged in up/down/up/down/etc orientation (to make soldering connections
// shorter) or false if all the segments are arranged in the same direction.
const bool SEGMENTS_ALTERNATE_DIRECTION = true;

// These constants are calculated from the simultion settings above, you should probably not set them directly
const unsigned int SEGMENT_SIZE = NUM_LEDS / REACTOR_SEGMENTS;
const float MAX_CHASER_SPEED_PIXELS_PER_SECOND = SEGMENT_SIZE / MAX_CHASER_SPEED_SECONDS_PER_SEGMENT;
const float MAX_PULSE_SPEED_PIXELS_PER_SECOND = SEGMENT_SIZE / MAX_PULSE_SPEED_SECONDS_PER_SEGMENT;

// The level of power being drawn from the reactor code, expressed as a floating point value on the range [0, 1]
float cruiseLevel = 0;

class CruiseParam
{
private:
  float paramTerp(float lowLevel, float highLevel, easing_functions easingFunc)
  {
    auto easingFunction = getEasingFunction(easingFunc);
    double progress = easingFunction(cruiseLevel);
    return lerp(lowLevel, highLevel, progress);
  }

public:
  CruiseParam(float lowStart, float lowEnd, float highStart, float highEnd, easing_functions easingFunc)
  {
    LowLevelRangeStart = lowStart;
    LowLevelRangeEnd = lowEnd;

    HighLevelRangeStart = highStart;
    HighLevelRangeEnd = highEnd;

    levelsEasingFunc = easingFunc;
  }

  // When the engine is at its lowest level, what start/end range of the parameter should be applied to the noise function
  float LowLevelRangeStart;
  float LowLevelRangeEnd;

  // When the engine is at its highest level, what start/end range of the parameter should be applied to the noise function
  float HighLevelRangeStart;
  float HighLevelRangeEnd;

  // Given the ranges above, how should the cruise level interpolate the range bounds from low/high level. See
  // https://easings.net/ for a description of what the various easing functions look like
  easing_functions levelsEasingFunc;

  float RangeStart()
  {
    return paramTerp(LowLevelRangeStart, HighLevelRangeStart, levelsEasingFunc);
  }

  float RangeEnd()
  {
    return paramTerp(LowLevelRangeEnd, HighLevelRangeEnd, levelsEasingFunc);
  }
};

const int HUE_DARK_BLUE = 165;
const int HUE_MID_DARK_BLUE = 150;
const int HUE_MID_LIGHT_BLUE = 145;
const int HUE_BLUE_AQUA = 130;

// Warp Core Color progression parameter
CruiseParam hueParam(HUE_DARK_BLUE, HUE_MID_DARK_BLUE, HUE_MID_LIGHT_BLUE, HUE_BLUE_AQUA, EaseInCirc);

// Warp Core Saturation (whiteness) progression parameter -- a fully saturated color has no white, a zero saturated
// color is pure white.  Higher engine levels push the engine color more towards the white end.
CruiseParam satParam(230, 255, 30, 180, EaseInExpo);

// Warp Core Value (brightness) parameter
CruiseParam valueParam(60, 230, 220, 255, EaseOutCubic);

float chaserPosition[REACTOR_SEGMENTS * CHASERS_PER_SEGMENT];
float chaserSpeedPct[REACTOR_SEGMENTS * CHASERS_PER_SEGMENT];

bool showDiags = false;

void reactor_setup()
{
  Logger.Info(F("Setup Chaser: Segs: %d, SegSize: %d"), REACTOR_SEGMENTS, SEGMENT_SIZE);

  reactor_cruise(0);

  if (showDiags)
  {
    Logger.Info(F("Init Chaser: Chaser Speed (sec/seg): %f"), MAX_CHASER_SPEED_SECONDS_PER_SEGMENT);
    Logger.Info(F("Init Chaser: Chaser Speed (px/sec): %f"), MAX_CHASER_SPEED_PIXELS_PER_SECOND);
  }
  for (unsigned int segmentIndex = 0; segmentIndex < REACTOR_SEGMENTS; segmentIndex++)
  {
    int segmentOffset = SEGMENT_SIZE * segmentIndex;

    for (unsigned int chaserIndex = 0; chaserIndex < CHASERS_PER_SEGMENT; chaserIndex++)
    {
      int flatIndex = segmentIndex * CHASERS_PER_SEGMENT + chaserIndex;

      int segmentPos = MoarRandom.randomInt(SEGMENT_SIZE);

      chaserPosition[flatIndex] = segmentPos + segmentOffset;
      chaserSpeedPct[flatIndex] = MoarRandom.randomFloat() * 80.0 + 20.0;
      if (showDiags)
      {
        Logger.Info(F("Init Chaser: Seg: %d, Chaser: %d, index: %d, offset: %d, pos: %f, speed: %f"),
                    segmentIndex, chaserIndex, flatIndex, segmentOffset, chaserPosition[flatIndex], chaserSpeedPct[flatIndex]);
      }
    }
  }
}

void reactor_cruise(float newCruiseLevel)
{
  cruiseLevel = clamp(newCruiseLevel, 0, 1.0);

  if (SHIFT_PALETTE)
  {
    setFogParamRange(FogParam_H, hueParam.RangeStart(), hueParam.RangeEnd());
    setFogParamRange(FogParam_S, satParam.RangeStart(), satParam.RangeEnd());
  }

  if (SHIFT_TWINKLE_SPEED)
  {
    setFogParamSpeed(FogParam_H, cruiseLevel * 100);
    setFogParamSpeed(FogParam_S, cruiseLevel * 100);
    setFogParamScale(FogParam_H, cruiseLevel * 100);
    setFogParamScale(FogParam_V, cruiseLevel * 100);
  }

  if (SHIFT_BRIGHTNESS)
  {
    setFogParamRange(FogParam_V, valueParam.RangeStart(), valueParam.RangeEnd());
  }
}

long unsigned int lastChaserUdate = 0;

void drawChasers(CRGBSet &leds)
{
  long unsigned int simTime = millis();

  float millisElapsed = simTime - lastChaserUdate;
  lastChaserUdate = simTime;

  int totalChasers = REACTOR_SEGMENTS * CHASERS_PER_SEGMENT;

  // This is how far each chaser should have moved, based upon the amount of time that has elapsed since we last updated
  float chaserDistance = ((MAX_CHASER_SPEED_PIXELS_PER_SECOND / 1000.0) * millisElapsed);
  chaserDistance *= clamp(cruiseLevel, 0.1, 1);

  if (showDiags)
  {
    Logger.Info(F("Updating Chasers: %d segments, %d per, total: %d, elapsed: %f, distance: %f"),
                REACTOR_SEGMENTS, CHASERS_PER_SEGMENT, totalChasers, millisElapsed, chaserDistance);
  }

  for (unsigned int segmentIndex = 0U; segmentIndex < REACTOR_SEGMENTS; segmentIndex++)
  {
    unsigned int segmentOffset = SEGMENT_SIZE * segmentIndex;

    for (unsigned int chaserIndex = 0U; chaserIndex < CHASERS_PER_SEGMENT; chaserIndex++)
    {
      unsigned int flatIndex = segmentIndex * CHASERS_PER_SEGMENT + chaserIndex;

      chaserPosition[flatIndex] += chaserDistance * chaserSpeedPct[flatIndex];

      if (chaserPosition[flatIndex] >= segmentOffset + SEGMENT_SIZE)
      {
        chaserPosition[flatIndex] -= SEGMENT_SIZE;
      }

      int pixelIndex = chaserPosition[flatIndex];

      if (showDiags)
      {
        Logger.Info(F("Updating Chaser: Seg: %d, Chaser: %d, index: %d, pix: %d"), segmentIndex, chaserIndex, flatIndex, pixelIndex);
      }

      leds[pixelIndex] = CRGB::White;
    }

    if (segmentOffset > 0)
    {
      leds[segmentOffset] = CRGB::Red;
    }
  }
  showDiags = false;
}

void reactor_loop(CRGBSet &leds)
{
  fog_loop(leds);

  if (SHOW_CHASERS)
  {
    drawChasers(leds);
  }

  for (unsigned int cruiseDiagIndex = 0; cruiseDiagIndex < cruiseLevel; cruiseDiagIndex++)
  {
    leds[cruiseDiagIndex + 1] = 0x004400;
  }

  FastLED.show();
}
