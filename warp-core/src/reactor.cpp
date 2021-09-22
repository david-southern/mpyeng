#include "common.h"

// Adjust these constants to configure the parameters of the core lighting

// How many vertical segments is the LED strip broken into
const unsigned int REACTOR_SEGMENTS = 4;

// If true, we will animate pure white LED's that will progress along each section at random speeds.
const bool SHOW_CHASERS = true;

// If true, the "background fog" palette will shift from a dark blue to a nearly blue-white as the cruise level increases.
const bool SHIFT_PALETTE = true;

// If true, the "background fog" twinkle speed will shift increase as the cruise level increases.
const bool SHIFT_TWINKLE_SPEED = true;

// If true, the entire LED strip brightness will increase as the cruise level increases
const bool SHIFT_BRIGHTNESS = true;

// If true, we will render a vertical strobing 'pulse; of white light that will increase in speed and intensity as the
// cruise level increases
const bool STROBE_PULSE = true;
const CRGB PULSE_COLOR(200, 255, 60);

const unsigned int CHASERS_PER_SEGMENT = 3;

// Set this flag to true if the segments are arranged in up/down/up/down/etc orientation (to make soldering connections
// shorter) or false if all the segments are arranged in the same direction.
const bool SEGMENTS_ALTERNATE_DIRECTION = true;

// These constants are calculated from the simultion settings above, you should probably not set them directly
const unsigned int SEGMENT_SIZE = NUM_LEDS / REACTOR_SEGMENTS;

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

  float RandValue()
  {
    return lerp(RangeStart(), RangeEnd(), MoarRandom.randomFloat());
  }
};

const int HUE_DARK_BLUE = 165;
const int HUE_MID_DARK_BLUE = 150;
const int HUE_MID_LIGHT_BLUE = 145;
const int HUE_BLUE_AQUA = 130;

// Low Level Params:
// hScale = 7, hSpeed = 2, gRange = 150, 165
// sScale = 7, sSpeed = 1, sRange = 200, 255
// vScale = 10, vSpeed = 1, vRange = 32, 180

// High Level Params:
// hScale = 10, hSpeed = 12, gRange = 130, 165
// sScale = 7, sSpeed = 12, sRange = 64, 255
// vScale = 10, vSpeed = 12, vRange = 128, 255

// Warp Core Color progression parameter
CruiseParam hueRange(HUE_MID_DARK_BLUE, HUE_DARK_BLUE, HUE_BLUE_AQUA, HUE_DARK_BLUE, EaseLinear);
CruiseParam hueScale(7, 7, 10, 10, EaseLinear);
CruiseParam hueSpeed(2, 2, 12, 12, EaseLinear);

// Warp Core Saturation (whiteness) progression parameter -- a fully saturated color has no white, a zero saturated
// color is pure white.  Higher engine levels push the engine color more towards the white end.
CruiseParam satRange(200, 255, 64, 255, EaseLinear);
CruiseParam satScale(7, 7, 7, 7, EaseLinear);
CruiseParam satSpeed(1, 1, 12, 12, EaseLinear);

// Warp Core Value (brightness) parameter
CruiseParam valueRange(32, 180, 128, 255, EaseLinear);
CruiseParam valueScale(10, 10, 10, 10, EaseLinear);
CruiseParam valueSpeed(1, 1, 12, 12, EaseLinear);

CruiseParam chaserSpeedSecondsPerSegment(10, 5, 2, 0.5, EaseLinear);
float chaserPosition[REACTOR_SEGMENTS * CHASERS_PER_SEGMENT];
float chaserSpeedPixPerSec[REACTOR_SEGMENTS * CHASERS_PER_SEGMENT];

CruiseParam pulseSpeedParamSecondsPerSegment(5, 5, 0.5, 0.5, EaseLinear);
CruiseParam pulseWidthPix(0.05, 0.05, 0.25, 0.25, EaseLinear);
float pulsePos;
float pulseSpeedPixPerSecond;
float pulseWidth;

bool showChaserDiags = false;
bool showPulseDiags = true;
long unsigned int lastChaserUpdate = 0;
long unsigned int lastPulseUpdate = 0;
long unsigned int lastPulseWrap = 0;

void reactor_setup()
{
  // Initialize the fog sim for the reactor animation background
  fog_setup();

  Logger.Info(F("Reactor: ##################### INITIALIZING #####################"));
  Logger.Info(F("Reactor: ##################### INITIALIZING #####################"));
  Logger.Info(F("Reactor: ##################### INITIALIZING #####################"));
  Logger.Info(F("Reactor: Segs: %d, SegSize: %d"), REACTOR_SEGMENTS, SEGMENT_SIZE);

  setFogFrameRate(30);

  // Set cruiseLevel so tests that need it work correctly
  // cruiseLevel = 0;

  // Low Level Params:
  // hScale = 7, hSpeed = 2, gRange = 150, 165
  // sScale = 7, sSpeed = 1, sRange = 200, 255
  // vScale = 10, vSpeed = 1, vRange = 32, 180

  // High Level Params:
  // hScale = 10, hSpeed = 12, gRange = 130, 165
  // sScale = 7, sSpeed = 12, sRange = 64, 255
  // vScale = 10, vSpeed = 12, vRange = 128, 255

  // Low Level Params:
  // setFogParamScale(FogParam_H, 7);
  // setFogParamSpeed(FogParam_H, 2);
  // setFogParamRange(FogParam_H, 150, 165);

  // setFogParamScale(FogParam_S, 7);
  // setFogParamSpeed(FogParam_S, 1);
  // setFogParamRange(FogParam_S, 200, 255);

  // setFogParamScale(FogParam_V, 10);
  // setFogParamSpeed(FogParam_V, 1);
  // setFogParamRange(FogParam_V, 32, 180);

  // High Level Params:
  // setFogParamScale(FogParam_H, 10);
  // setFogParamSpeed(FogParam_H, 12);
  // setFogParamRange(FogParam_H, 130, 165);

  // setFogParamScale(FogParam_S, 7);
  // setFogParamSpeed(FogParam_S, 12);
  // setFogParamRange(FogParam_S, 64, 255);

  // setFogParamScale(FogParam_V, 10);
  // setFogParamSpeed(FogParam_V, 12);
  // setFogParamRange(FogParam_V, 128, 255);

  // Test Params
  // setFogParamRange(FogParam_H, 120, 165);
  // setFogParamRange(FogParam_S, 255, 255);
  // setFogParamRange(FogParam_V, 196, 196);

  reactor_cruise(0);

  // Initialize everything so that parameters that aren't animated still get their correct initial value
  setFogParamRange(FogParam_H, hueRange.RangeStart(), hueRange.RangeEnd());
  setFogParamSpeed(FogParam_H, hueSpeed.RangeStart());
  setFogParamScale(FogParam_H, hueScale.RangeStart());

  setFogParamRange(FogParam_S, satRange.RangeStart(), satRange.RangeEnd());
  setFogParamSpeed(FogParam_S, satSpeed.RangeStart());
  setFogParamScale(FogParam_S, satScale.RangeStart());

  setFogParamRange(FogParam_V, valueRange.RangeStart(), valueRange.RangeEnd());
  setFogParamSpeed(FogParam_V, valueSpeed.RangeStart());
  setFogParamScale(FogParam_V, valueScale.RangeStart());

  for (unsigned int segmentIndex = 0; segmentIndex < REACTOR_SEGMENTS; segmentIndex++)
  {
    int segmentOffset = SEGMENT_SIZE * segmentIndex;

    for (unsigned int chaserIndex = 0; chaserIndex < CHASERS_PER_SEGMENT; chaserIndex++)
    {
      int flatIndex = segmentIndex * CHASERS_PER_SEGMENT + chaserIndex;

      int segmentPos = MoarRandom.randomInt(SEGMENT_SIZE);

      chaserPosition[flatIndex] = segmentPos;
      chaserSpeedPixPerSec[flatIndex] = SEGMENT_SIZE / chaserSpeedSecondsPerSegment.RandValue();
      if (showChaserDiags)
      {
        Logger.Info(F("Init Chaser: Seg: %d, Chaser: %d, index: %d, offset: %d, pos: %f, speed: %f"),
                    segmentIndex, chaserIndex, flatIndex, segmentOffset, chaserPosition[flatIndex], chaserSpeedPixPerSec[flatIndex]);
      }
    }
  }

  lastChaserUpdate = millis();
  lastPulseUpdate = millis();
  lastPulseWrap = millis();
}

int cruiseDiagLevel = 0;
int lastCruiseDiagLevel = 0;

void reactor_cruise(float newCruiseLevel)
{
  cruiseLevel = clamp(newCruiseLevel, 0, 1.0);
  cruiseDiagLevel = cruiseLevel * 10;

  if (lastCruiseDiagLevel != cruiseDiagLevel)
  {
    Logger.Info("Reactor: Setting cruise level to: %f", cruiseLevel);
    showPulseDiags = true;
  }

  if (SHIFT_PALETTE)
  {
    setFogParamRange(FogParam_H, hueRange.RangeStart(), hueRange.RangeEnd());
    setFogParamRange(FogParam_S, satRange.RangeStart(), satRange.RangeEnd());
  }

  if (SHIFT_TWINKLE_SPEED)
  {
    setFogParamSpeed(FogParam_H, hueSpeed.RangeStart());
    setFogParamScale(FogParam_H, hueScale.RangeStart());
    setFogParamSpeed(FogParam_S, satSpeed.RangeStart());
    setFogParamScale(FogParam_S, satScale.RangeStart());
  }

  if (SHIFT_BRIGHTNESS)
  {
    setFogParamRange(FogParam_V, valueRange.RangeStart(), valueRange.RangeEnd());
    setFogParamSpeed(FogParam_V, valueSpeed.RangeStart());
    setFogParamScale(FogParam_V, valueScale.RangeStart());
  }

  if (SHOW_CHASERS)
  {
    // TODO: Right now we're only adjusting the chaser speed when we change cruiselevel by more than +/- 10%.  This is
    // because if they make lots of small/smooth changes, we don't want to potenitally be jumping the chase speed from
    // the bottom of the range all the way up to the top at every small change, that will make the chaser speed
    // animation look chaotic and janky.

    // Update the chaser speeds
    for (unsigned int segmentIndex = 0; segmentIndex < REACTOR_SEGMENTS; segmentIndex++)
    {
      for (unsigned int chaserIndex = 0; chaserIndex < CHASERS_PER_SEGMENT; chaserIndex++)
      {
        int flatIndex = segmentIndex * CHASERS_PER_SEGMENT + chaserIndex;
        chaserSpeedPixPerSec[flatIndex] = SEGMENT_SIZE / chaserSpeedSecondsPerSegment.RandValue();
      }
    }
  }

  if (STROBE_PULSE)
  {
    pulseSpeedPixPerSecond =  SEGMENT_SIZE / pulseSpeedParamSecondsPerSegment.RandValue();
    pulseWidth = SEGMENT_SIZE * pulseWidthPix.RandValue();
  }

  lastCruiseDiagLevel = cruiseDiagLevel;
}

void drawChasers(CRGBSet &leds)
{
  long unsigned int simTime = millis();

  float secondsElapsed = (simTime - lastChaserUpdate) / 1000.0;
  lastChaserUpdate = simTime;

  int totalChasers = REACTOR_SEGMENTS * CHASERS_PER_SEGMENT;

  if (showChaserDiags)
  {
    Logger.Info(F("Updating Chasers: %d segments, %d per, total: %d, elapsed: %f"),
                REACTOR_SEGMENTS, CHASERS_PER_SEGMENT, totalChasers, secondsElapsed);
  }

  for (unsigned int segmentIndex = 0U; segmentIndex < REACTOR_SEGMENTS; segmentIndex++)
  {
    unsigned int segmentOffset = SEGMENT_SIZE * segmentIndex;

    for (unsigned int chaserIndex = 0U; chaserIndex < CHASERS_PER_SEGMENT; chaserIndex++)
    {
      unsigned int flatIndex = segmentIndex * CHASERS_PER_SEGMENT + chaserIndex;

      chaserPosition[flatIndex] += chaserSpeedPixPerSec[flatIndex] * secondsElapsed;

      if (chaserPosition[flatIndex] >= SEGMENT_SIZE)
      {
        chaserPosition[flatIndex] = std::fmod(chaserPosition[flatIndex], SEGMENT_SIZE);
        chaserSpeedPixPerSec[flatIndex] = SEGMENT_SIZE / chaserSpeedSecondsPerSegment.RandValue();
      }

      int pixelIndex = chaserPosition[flatIndex] + segmentOffset;

      if (showChaserDiags)
      {
        Logger.Info(F("Updating Chaser: Seg: %d, Chaser: %d, index: %d, pix: %d, speed: %f"),
                    segmentIndex, chaserIndex, flatIndex, pixelIndex, chaserSpeedPixPerSec[flatIndex] * secondsElapsed);
      }

      if (flatIndex == 1)
      {
        leds[pixelIndex] = CRGB::Red;
      }
      else
      {
        leds[pixelIndex] = CRGB::White;
      }

      leds[pixelIndex] = CRGB::White;
    }

    if (segmentOffset > 0)
    {
      leds[segmentOffset] = CRGB::Red;
    }
  }
  showChaserDiags = false;
}

void drawStrobe(CRGBSet &leds)
{
  long unsigned int simTime = millis();

  float secondsElapsed = (simTime - lastPulseUpdate) / 1000.0;
  lastPulseUpdate = simTime;

  // if (showPulseDiags)
  // {
  //   Logger.Info(F("Updating Pulse: %d segments, pos: %f, speed: %f, width: %d, elapsed: %f"),
  //               REACTOR_SEGMENTS, CHASERS_PER_SEGMENT, pulsePos, pulseSpeedPixPerSecond, (int)pulseWidth, secondsElapsed);
  // }

  pulsePos += pulseSpeedPixPerSecond * secondsElapsed;

  if (pulsePos >= SEGMENT_SIZE)
  {
    pulsePos = 0;
    pulseSpeedPixPerSecond = SEGMENT_SIZE / pulseSpeedParamSecondsPerSegment.RandValue();
    lastPulseWrap = simTime;
  }

  for (unsigned int segmentIndex = 0U; segmentIndex < REACTOR_SEGMENTS; segmentIndex++)
  {
    unsigned int segmentOffset = SEGMENT_SIZE * segmentIndex;

    for (unsigned int pulseIndex = 0U; pulseIndex < pulseWidth; pulseIndex++)
    {
      unsigned int pixelIndex = pulsePos + pulseIndex;

      if (pixelIndex > SEGMENT_SIZE)
      {
        pixelIndex = pixelIndex % SEGMENT_SIZE;
      }

      if (SEGMENTS_ALTERNATE_DIRECTION && segmentIndex % 2 == 1)
      {
        pixelIndex = segmentOffset + SEGMENT_SIZE - pixelIndex;
      }
      else
      {
        pixelIndex += segmentOffset;
      }

      leds[pixelIndex] = PULSE_COLOR;
    }

    if (segmentOffset > 0)
    {
      leds[segmentOffset] = CRGB::Red;
    }
  }
  showPulseDiags = false;
}

void reactor_loop(CRGBSet &leds)
{
  bool showFrame = fog_loop(leds);

  if (!showFrame)
  {
    return;
  }

  if (SHOW_CHASERS)
  {
    drawChasers(leds);
  }

  if (STROBE_PULSE)
  {
    drawStrobe(leds);
  }

  for (int cruiseDiagIndex = 0; cruiseDiagIndex < cruiseDiagLevel; cruiseDiagIndex++)
  {
    unsigned int diagColor = 0x004400;
    if(cruiseDiagIndex >= 6) {
      diagColor = 0x444400;
    }
    if(cruiseDiagIndex == 9) {
      diagColor = 0x440000;
    }
    leds[cruiseDiagIndex + 1] = diagColor;
  }

  FastLED.show();
}
