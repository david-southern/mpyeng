#include "common.h"

// Adjust these constants to configure the parameters of the core lighting

// How many vertical segments is the LED strip broken into
const unsigned int REACTOR_SEGMENTS = 8;
// const unsigned int REACTOR_SEGMENTS = 1;

// If true, we will animate pure white LED's that will progress along each section at random speeds.
const bool SHOW_CHASERS = true;

// If true, the "background fog" palette will shift from a dark blue to a nearly blue-white as the cruise level increases.
const bool SHIFT_PALETTE = true;

// If true, the "background fog" twinkle speed will shift increase as the cruise level increases.
const bool SHIFT_TWINKLE_SPEED = true;

// If true, the entire LED strip brightness will increase as the cruise level increases
const bool SHIFT_BRIGHTNESS = true;

// If true, we will render a vertical strobing 'pulse' of white light that will increase in speed and intensity as the
// cruise level increases
bool STROBE_PULSE_BY_SIZE = false;

// If true, we will render a vertical strobing 'pulse' of white light with a constant size and speed that will increase
// in frequency as the cruise level increases
const bool STROBE_PULSE_BY_FREQ = true;

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

// Note: FastLED defines its hue range from 0 - 255, rather than 0-360.  Check this page for a visual representation of
// the FastLED hue range:
//
// https://github.com/FastLED/FastLED/wiki/FastLED-HSV-Colors
const int HUE_PURE_RED = 0;
const int HUE_PURE_GREEN = 96;
const int HUE_PURE_YELLOW = 64;
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
CruiseParam fogColorRange(HUE_MID_DARK_BLUE, HUE_DARK_BLUE, HUE_BLUE_AQUA, HUE_DARK_BLUE, EaseLinear);
CruiseParam fogColorScale(7, 7, 10, 10, EaseLinear);
CruiseParam fogColorSpeed(2, 2, 12, 12, EaseLinear);

// Warp Core Saturation (whiteness) progression parameter -- a fully saturated color has no white, a zero saturated
// color is pure white.  Higher engine levels push the engine color more towards the white end.
CruiseParam fogWhitenessRange(200, 255, 64, 255, EaseLinear);
CruiseParam fogWhitenessScale(7, 7, 7, 7, EaseLinear);
CruiseParam fogWhitenessSpeed(1, 1, 12, 12, EaseLinear);

// Warp Core Value (brightness) parameter
// CruiseParam fogBrightnessRange(32, 180, 128, 255, EaseLinear);
CruiseParam fogBrightnessRange(80, 200, 180, 255, EaseLinear);
CruiseParam fogBrightnessScale(10, 10, 10, 10, EaseLinear);
CruiseParam fogBrightnessSpeed(1, 1, 12, 12, EaseLinear);

// Don't change the color for now, just the whiteness
CruiseParam chaserHueRange(HUE_PURE_GREEN, HUE_PURE_GREEN, HUE_PURE_GREEN, HUE_PURE_GREEN, EaseLinear);

// This is the Saturation parameter, inverse of 'whiteness'
CruiseParam chaserWhitenessRange(255, 255, 0, 0, EaseInCubic);
uint8_t chaserValue = 255;

CRGB CHASER_COLOR = CHSV(HUE_PURE_GREEN, 255, chaserValue);

CruiseParam pulseHueRange(HUE_PURE_YELLOW, HUE_PURE_YELLOW, HUE_PURE_RED, HUE_PURE_RED, EaseInCubic);
// This is the Saturation parameter, inverse of 'whiteness' -- Start out as a very white-yelllow, and progredd to a
// full-on red at max power
CruiseParam pulseWhitenessRange(196, 196, 255, 255, EaseInCubic);
uint8_t pulseValue = 255;

CRGB PULSE_COLOR = CHSV(HUE_PURE_GREEN, 255, pulseValue);

// Upwards floating chasers
// CruiseParam chaserSpeedSecondsPerSegment(10, 5, 2, 0.5, EaseLinear);

// Downwards floating chasers
CruiseParam chaserSpeedSecondsPerSegment(-10, -5, -2, -0.5, EaseLinear);

float chaserPosition[REACTOR_SEGMENTS * CHASERS_PER_SEGMENT];
float chaserSpeedPixPerSec[REACTOR_SEGMENTS * CHASERS_PER_SEGMENT];

#define MAX_PULSES 10

CruiseParam *pulseSpeedParamSecondsPerSegment;
CruiseParam *pulseWidthPix;
CruiseParam *pulseFreqParamSecondsPerPulse;

int pulseCount = 0;
float allPulsePos[MAX_PULSES];
float allPulseSpeedPixPerSecond[MAX_PULSES];
float allPulseWidth[MAX_PULSES];

bool showChaserDiags = false;
bool showPulseDiags = true;
long unsigned int lastChaserUpdate = 0;
long unsigned int lastPulseUpdate = 0;
long unsigned int nextPulseCreation = 0;

void createNewPulse()
{
  if (pulseCount >= MAX_PULSES)
  {
    Logger.Warning(F("Attempted to create a new strobe pulse, but there are already the max number (%d) of pulses"), MAX_PULSES);
    return;
  }

  allPulsePos[pulseCount] = 0;
  allPulseSpeedPixPerSecond[pulseCount] = SEGMENT_SIZE / pulseSpeedParamSecondsPerSegment->RandValue();
  allPulseWidth[pulseCount] = SEGMENT_SIZE * pulseWidthPix->RandValue();

  float nextPulseMillis = pulseFreqParamSecondsPerPulse->RandValue() * 1000;
  nextPulseCreation = millis() + nextPulseMillis;

  Logger.Warning(F("PL: %f - Creating new pulse - total of %d pulses, next pulse delay: %d millis"),
                 cruiseLevel, pulseCount, (int)nextPulseMillis);

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

void reactor_setup()
{
  // Initialize the fog sim for the reactor animation background
  fog_setup();

  Logger.Info(F("Reactor: ##################### INITIALIZING #####################"));
  Logger.Info(F("Reactor: ##################### INITIALIZING #####################"));
  Logger.Info(F("Reactor: ##################### INITIALIZING #####################"));
  Logger.Info(F("Reactor: Segs: %d, SegSize: %d"), REACTOR_SEGMENTS, SEGMENT_SIZE);

  setFogFrameRate(30);

  // We can render the strobe pulse either by size or by frequency.  I've feature flagged both approaches in case I want
  // to switch back and forth, however they are mutually exclusive.  If I accidentally set both at once, then prefer the
  // FREQ version.
  if (STROBE_PULSE_BY_FREQ && STROBE_PULSE_BY_SIZE)
  {
    STROBE_PULSE_BY_SIZE = false;
  }

  if (STROBE_PULSE_BY_SIZE)
  {
    pulseSpeedParamSecondsPerSegment = new CruiseParam(5, 5, 0.5, 0.5, EaseLinear);
    pulseWidthPix = new CruiseParam(0.025, 0.025, 0.2, 0.2, EaseLinear);
    pulseFreqParamSecondsPerPulse = new CruiseParam(5.5, 5.5, 0.55, 0.55, EaseLinear);
  }
  else
  {
    pulseSpeedParamSecondsPerSegment = new CruiseParam(0.4, 0.4, 0.4, 0.4, EaseLinear);
    pulseWidthPix = new CruiseParam(0.12, 0.12, 0.04, 0.04, EaseLinear);
    pulseFreqParamSecondsPerPulse = new CruiseParam(4, 4, 0.4, 0.4, EaseOutCirc);
  }

  if (STROBE_PULSE_BY_SIZE || STROBE_PULSE_BY_FREQ)
  {
    createNewPulse();
  }

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
  setFogParamRange(FogParam_H, fogColorRange.RangeStart(), fogColorRange.RangeEnd());
  setFogParamSpeed(FogParam_H, fogColorSpeed.RangeStart());
  setFogParamScale(FogParam_H, fogColorScale.RangeStart());

  setFogParamRange(FogParam_S, fogWhitenessRange.RangeStart(), fogWhitenessRange.RangeEnd());
  setFogParamSpeed(FogParam_S, fogWhitenessSpeed.RangeStart());
  setFogParamScale(FogParam_S, fogWhitenessScale.RangeStart());

  setFogParamRange(FogParam_V, fogBrightnessRange.RangeStart(), fogBrightnessRange.RangeEnd());
  setFogParamSpeed(FogParam_V, fogBrightnessSpeed.RangeStart());
  setFogParamScale(FogParam_V, fogBrightnessScale.RangeStart());

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

  CHASER_COLOR = CHSV(chaserHueRange.RandValue(), chaserWhitenessRange.RandValue(), chaserValue);
  PULSE_COLOR = CHSV(pulseHueRange.RandValue(), pulseWhitenessRange.RandValue(), pulseValue);

  if (SHIFT_PALETTE)
  {
    setFogParamRange(FogParam_H, fogColorRange.RangeStart(), fogColorRange.RangeEnd());
    setFogParamRange(FogParam_S, fogWhitenessRange.RangeStart(), fogWhitenessRange.RangeEnd());
  }

  if (SHIFT_TWINKLE_SPEED)
  {
    setFogParamSpeed(FogParam_H, fogColorSpeed.RangeStart());
    setFogParamScale(FogParam_H, fogColorScale.RangeStart());
    setFogParamSpeed(FogParam_S, fogWhitenessSpeed.RangeStart());
    setFogParamScale(FogParam_S, fogWhitenessScale.RangeStart());
  }

  if (SHIFT_BRIGHTNESS)
  {
    setFogParamRange(FogParam_V, fogBrightnessRange.RangeStart(), fogBrightnessRange.RangeEnd());
    setFogParamSpeed(FogParam_V, fogBrightnessSpeed.RangeStart());
    setFogParamScale(FogParam_V, fogBrightnessScale.RangeStart());
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

        chaserSpeedPixPerSec[flatIndex] = SEGMENT_SIZE / chaserSpeedSecondsPerSegment.RandValue();
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

      if (showChaserDiags)
      {
        Logger.Info(F("Updating Chaser: Seg: %d, Chaser: %d, index: %d, pix: %d, speed: %f"),
                    segmentIndex, chaserIndex, flatIndex, pixelPosition, chaserSpeedPixPerSec[flatIndex] * secondsElapsed);
      }

      leds[pixelPosition] = CHASER_COLOR;
    }
  }
  showChaserDiags = false;
}

void drawStrobe(CRGBSet &leds)
{
  long unsigned int simTime = millis();

  float secondsElapsed = (simTime - lastPulseUpdate) / 1000.0;
  lastPulseUpdate = simTime;

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
  showPulseDiags = false;
}

void drawDiags(CRGBSet &leds)
{
  for (unsigned int segmentIndex = 0U; segmentIndex < REACTOR_SEGMENTS; segmentIndex++)
  {
    int segmentOffset = SEGMENT_SIZE * segmentIndex;

    int topPixel = segmentOffset + SEGMENT_SIZE - 1;
    int bottomPixel = segmentOffset;

    if (SEGMENTS_ALTERNATE_DIRECTION && segmentIndex % 2 == 1)
    {
      int tmp = topPixel;
      topPixel = bottomPixel;
      bottomPixel = tmp;
    }

    leds[topPixel] = CRGB::Red;
    leds[bottomPixel] = CRGB::Magenta;
  }

  for (int cruiseDiagIndex = 0; cruiseDiagIndex < cruiseDiagLevel; cruiseDiagIndex++)
  {
    unsigned int diagColor = 0x004400;
    if (cruiseDiagIndex >= 6)
    {
      diagColor = 0x444400;
    }
    if (cruiseDiagIndex == 9)
    {
      diagColor = 0x440000;
    }
    leds[cruiseDiagIndex + 1] = diagColor;
  }
}

void reactor_loop(CRGBSet &leds)
{
  bool showFrame = fog_loop(leds);

  if (!showFrame)
  {
    return;
  }

  long unsigned int simTime = millis();

  if (SHOW_CHASERS)
  {
    drawChasers(leds);
  }

  if (STROBE_PULSE_BY_SIZE || STROBE_PULSE_BY_FREQ)
  {
    if (simTime > nextPulseCreation)
    {
      createNewPulse();
    }

    drawStrobe(leds);
  }

  drawDiags(leds);

  FastLED.show();
}
