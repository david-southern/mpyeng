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

CRGBPalette16 reactorPalette;

enum CruiseBrightnessMode
{
  Undefined,
  CB_Linear,
  CB_Exp,
  CB_Log,
};

const CruiseBrightnessMode brightnessMode = CB_Linear;

const uint8_t CRUISE_LEVEL_MAX = 9;

const uint8_t CRUISE_BRIGHTNESS_MIN = 64;
const uint8_t CRUISE_BRIGHTNESS_MAX = 250;
const float cruiseDelta = CRUISE_BRIGHTNESS_MAX - CRUISE_BRIGHTNESS_MIN;

// Darker
#define Navy CRGB::Navy
#define DarkBlue CRGB::DarkBlue
#define MediumBlue CRGB::MediumBlue
#define Blue CRGB::Blue
#define DarkCyan CRGB::DarkCyan
#define DeepSkyBlue CRGB::DeepSkyBlue
#define Cyan CRGB::Cyan
#define DodgerBlue CRGB::DodgerBlue
#define Turquoise CRGB::Turquoise
#define MediumTurquoise CRGB::MediumTurquoise
#define CornflowerBlue CRGB::CornflowerBlue
#define CadetBlue CRGB::CadetBlue
#define MediumAquamarine CRGB::MediumAquamarine
#define Aquamarine CRGB::Aquamarine
// Lighter

const TProgmemRGBPalette16 Cruise0 FL_PROGMEM = {
    Navy, Navy, Navy, Navy, Navy, Navy, Navy, Navy,
    DarkBlue, DarkBlue, DarkBlue, DarkBlue, MediumBlue, MediumBlue, Blue, Blue};

const TProgmemRGBPalette16 Cruise1 FL_PROGMEM = {
    DarkBlue, DarkBlue, DarkBlue, DarkBlue, DarkBlue,
    DarkBlue, DarkBlue, DarkBlue, MediumBlue, MediumBlue,
    MediumBlue, Blue, Blue, DarkCyan, DeepSkyBlue};

const TProgmemRGBPalette16 Cruise2 FL_PROGMEM = {
    DarkBlue, DarkBlue, DarkBlue, DarkBlue, MediumBlue, MediumBlue,
    MediumBlue, MediumBlue, Blue, Blue, DarkCyan, DarkCyan,
    DeepSkyBlue, DeepSkyBlue, Cyan, Cyan};

const TProgmemRGBPalette16 Cruise3 FL_PROGMEM = {
    MediumBlue, MediumBlue, MediumBlue, MediumBlue, MediumBlue, MediumBlue,
    MediumBlue, MediumBlue, Blue, DarkCyan, DarkCyan, DeepSkyBlue,
    Cyan, Cyan, DodgerBlue, Turquoise};

const TProgmemRGBPalette16 Cruise4 FL_PROGMEM = {
    MediumBlue, MediumBlue, MediumBlue, MediumBlue, Blue, Blue,
    Blue, Blue, DarkCyan, DeepSkyBlue, Cyan, Cyan,
    DodgerBlue, Turquoise, MediumTurquoise, MediumTurquoise};

const TProgmemRGBPalette16 Cruise5 FL_PROGMEM = {
    Blue, Blue, Blue, Blue, DarkCyan, DarkCyan, DarkCyan, DeepSkyBlue,
    Cyan, Cyan, DodgerBlue, Turquoise, MediumTurquoise, MediumTurquoise, CornflowerBlue, CornflowerBlue};

const TProgmemRGBPalette16 Cruise6 FL_PROGMEM = {
    Blue, Blue, DarkCyan, DarkCyan, DarkCyan, DarkCyan, DeepSkyBlue, DeepSkyBlue,
    Cyan, DodgerBlue, Turquoise, MediumTurquoise, CornflowerBlue, CornflowerBlue, CadetBlue, MediumAquamarine};

const TProgmemRGBPalette16 Cruise7 FL_PROGMEM = {
    DarkCyan, DarkCyan, DarkCyan, DarkCyan, DeepSkyBlue, DeepSkyBlue, Cyan, Cyan,
    DodgerBlue, DodgerBlue, Turquoise, MediumTurquoise, MediumTurquoise, CornflowerBlue, CadetBlue, MediumAquamarine};

/*
#define CornflowerBlue CRGB::CornflowerBlue
#define CadetBlue CRGB::CadetBlue
#define MediumAquamarine CRGB::MediumAquamarine
#define Aquamarine CRGB::Aquamarine
*/
const TProgmemRGBPalette16 Cruise8 FL_PROGMEM = {
    DarkCyan, DarkCyan, DeepSkyBlue, DeepSkyBlue, Cyan, Cyan, DodgerBlue, DodgerBlue,
    DodgerBlue, Turquoise, MediumTurquoise, CornflowerBlue, CornflowerBlue, CadetBlue, MediumAquamarine, Aquamarine};

const TProgmemRGBPalette16 Cruise9 FL_PROGMEM = {
    DeepSkyBlue, DeepSkyBlue, Cyan, Cyan, DodgerBlue, DodgerBlue, Turquoise, Turquoise,
    MediumTurquoise, CornflowerBlue, CadetBlue, CadetBlue, MediumAquamarine, Aquamarine, Aquamarine, Aquamarine};

const TProgmemRGBPalette16 *CruiseLevelPaletteList[] = {
    &Cruise0,
    &Cruise1,
    &Cruise2,
    &Cruise3,
    &Cruise4,
    &Cruise5,
    &Cruise6,
    &Cruise7,
    &Cruise8,
    &Cruise9,
};

/*
        Amethyst=0x9966CC,

        Coral=0xFF7F50,
        Crimson=0xDC143C,
        DeepPink=0xFF1493,
        HotPink=0xFF69B4,
        IndianRed=0xCD5C5C,
        LightCoral=0xF08080,
        LightPink=0xFFB6C1,
        LightSalmon=0xFFA07A,
        Maroon=0x800000,
        DarkRed=0x8B0000,
        DarkSalmon=0xE9967A,
        MediumVioletRed=0xC71585,
        MistyRose=0xFFE4E1,
        Pink=0xFFC0CB,
        Red=0xFF0000,
        Salmon=0xFA8072,
        Tomato=0xFF6347,


        RosyBrown=0xBC8F8F,
        Orange=0xFFA500,
        OrangeRed=0xFF4500,
        DarkOrange=0xFF8C00,
        DarkOrchid=0x9932CC,

        LightYellow=0xFFFFE0,
        Yellow=0xFFFF00,

        AliceBlue=0xF0F8FF,
        Aqua=0x00FFFF,
        Aquamarine=0x7FFFD4,
        Azure=0xF0FFFF,
        Blue=0x0000FF,
        BlueViolet=0x8A2BE2,
        CadetBlue=0x5F9EA0,
        CornflowerBlue=0x6495ED,
        Cyan=0x00FFFF,
        DarkBlue=0x00008B,
        DarkCyan=0x008B8B,
        DeepSkyBlue=0x00BFFF,
        DodgerBlue=0x1E90FF,

        Indigo=0x4B0082,
        LightBlue=0xADD8E6,
        LightCyan=0xE0FFFF,
        LightSkyBlue=0x87CEFA,

        MediumAquamarine=0x66CDAA,
        MediumBlue=0x0000CD,
        MediumTurquoise=0x48D1CC,
        MidnightBlue=0x191970,
        Navy=0x000080,
        PowderBlue=0xB0E0E6,
        RoyalBlue=0x4169E1,
        SkyBlue=0x87CEEB,
        Turquoise=0x40E0D0,
*/

// const TProgmemRGBPalette16 Emergency FL_PROGMEM = {
//     CRGB::DarkRed,
//     CRGB::DarkRed,
//     CRGB::DarkRed,
//     CRGB::Red,
//     CRGB::Red,
//     CRGB::Red,
//     CRGB::Red,
//     CRGB::Red,
//     CRGB::OrangeRed,
//     CRGB::OrangeRed,
//     CRGB::OrangeRed,
//     CRGB::OrangeRed,
//     CRGB::OrangeRed,
//     CRGB::OrangeRed,
//     CRGB::OrangeRed,
// };

// const TProgmemRGBPalette16 Damaged FL_PROGMEM = {
//     CRGB::Red, CRGB::Red, CRGB::Red, CRGB::Red,
//     CRGB::Red, CRGB::Orange, CRGB::Orange, CRGB::Yellow,
//     CRGB::Yellow, CRGB::Yellow, CRGB::White, CRGB::White,
//     CRGB::White, CRGB::White, CRGB::White, CRGB::White};

// const TProgmemRGBPalette16 Critical FL_PROGMEM = {
//     CRGB::White, CRGB::White, CRGB::White, CRGB::White, CRGB::White, CRGB::White,
//     CRGB::White, CRGB::White, CRGB::White, CRGB::White, CRGB::White, CRGB::White,
//     CRGB::White, CRGB::White, CRGB::White, CRGB::White};

CRGBPalette16 ActivePalette;
float chaserPosition[REACTOR_SEGMENTS * CHASERS_PER_SEGMENT];
float chaserSpeed[REACTOR_SEGMENTS * CHASERS_PER_SEGMENT];
uint8_t cruiseLevel;

int totalBytes = 0;

void resetMemoryUsage()
{
  totalBytes = 0;
}

void addMemoryUsage(const char *name, int size)
{
  Logger.Info(F("Meory Usage: %s size: %d"), name, size);
  totalBytes += size;
}

void logMemoryUsage()
{
  resetMemoryUsage();
  addMemoryUsage("reactorPalette", sizeof(reactorPalette));
  addMemoryUsage("ActivePalette", sizeof(ActivePalette));
  addMemoryUsage("chaserPosition", sizeof(chaserPosition));
  addMemoryUsage("chaserSpeed", sizeof(chaserSpeed));

  Logger.Info(F("Total Meory Usage: %d"), totalBytes);
}

float cruiseLevelProgress()
{
  return ((float)cruiseLevel / CRUISE_LEVEL_MAX);
}

uint8_t cruiseBrightness()
{
  uint8_t newBrightness = CRUISE_BRIGHTNESS_MIN;

  switch (brightnessMode)
  {
  case CB_Exp:
    break;
  case CB_Log:
    break;

  default: // Default to CB_Linear
    newBrightness =
        CRUISE_BRIGHTNESS_MIN + cruiseDelta * cruiseLevelProgress();
    break;
  }

  newBrightness =
      clamp(newBrightness, CRUISE_BRIGHTNESS_MIN, CRUISE_BRIGHTNESS_MAX);

  return newBrightness;
}

bool showDiags = false;

void reactor_setup()
{
  logMemoryUsage();

  Logger.Info(F("Setup Chaser: Segs: %d, SegSize: %d"), REACTOR_SEGMENTS, SEGMENT_SIZE);

  ActivePalette = *(CruiseLevelPaletteList[0]);
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

      int segmentPos = random(SEGMENT_SIZE);

      chaserPosition[flatIndex] = segmentPos + segmentOffset;
      chaserSpeed[flatIndex] = (20 + random(80)) / 100.0;
      if (showDiags)
      {
        Logger.Info(F("Init Chaser: Seg: %d, Chaser: %d, index: %d, offset: %d, pos: %f, speed: %f"),
                    segmentIndex, chaserIndex, flatIndex, segmentOffset, chaserPosition[flatIndex], chaserSpeed[flatIndex]);
      }
    }
  }
}

void reactor_cruise(uint8_t newCruiseLevel)
{
  // showDiags = true;
  cruiseLevel = clamp(newCruiseLevel, 0, CRUISE_LEVEL_MAX);

  uint8_t brightness = cruiseBrightness();
  uint8_t newSpeed = 0 + cruiseLevelProgress() * 8;

  // Logger.Info(F("reactor_cruise: Setting cruise level to %d, brightness to: %d, speed to: %d"), cruiseLevel, brightness, newSpeed);

  if (SHIFT_PALETTE)
  {
    ActivePalette = *(CruiseLevelPaletteList[cruiseLevel]);
  }

  if (SHIFT_TWINKLE_SPEED)
  {
    setTwinkleSpeed(newSpeed);
  }

  if (SHIFT_BRIGHTNESS)
  {
    FastLED.setBrightness(brightness);
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
  chaserDistance *= clamp(cruiseLevelProgress(), 0.1, 1);

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

      chaserPosition[flatIndex] += chaserDistance * chaserSpeed[flatIndex];

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
  drawTwinkles(ActivePalette, leds);

  if (SHOW_CHASERS)
  {
    drawChasers(leds);
  }

  for (unsigned int cruiseDiagIndex = 0; cruiseDiagIndex < cruiseLevel; cruiseDiagIndex++) {
    leds[cruiseDiagIndex + 1] = 0x004400;
  }

    FastLED.show();
}
