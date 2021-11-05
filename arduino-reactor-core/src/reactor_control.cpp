#include "common.h"

// The level of power being drawn from the reactor code, expressed as a floating point value on the range [0, 1]
float CorePowerLevel = 0;

// Set to a default of 50 frames/sec
float desiredMillisPerFrame = 20;
bool reportFrameRate = false;
uint32_t lastFrameUpdate;

bool SHOW_DIAGS = false;

void setReactorFrameRate(float framesPerSec)
{
  if (framesPerSec < 0.1)
  {
    desiredMillisPerFrame = 0;
    reportFrameRate = true;
  }
  else
  {
    desiredMillisPerFrame = 1000.0 / framesPerSec;
  }
  Logger.Info("FogSim: Setting frame rate to %f", framesPerSec);
}

void reactor_setup()
{
  Logger.Info(F("Reactor: ##################### INITIALIZING #####################"));
  Logger.Info(F("Reactor: ##################### INITIALIZING #####################"));
  Logger.Info(F("Reactor: ##################### INITIALIZING #####################"));
  Logger.Info(F("Reactor: Segs: %d, SegSize: %d"), REACTOR_SEGMENTS, SEGMENT_SIZE);

  setReactorFrameRate(0);

  // Initialize the fog sim for the reactor animation background
  fog_setup();

  chaser_setup();
  pulse_setup();

  reactor_cruise(0);

  lastFrameUpdate = millis();
}

int cruiseDiagLevel = 0;

void reactor_cruise(float newCruiseLevel)
{
  CorePowerLevel = clamp(newCruiseLevel, 0, 1.0);
  cruiseDiagLevel = CorePowerLevel * 10;

  fog_update_params();
  chaser_update_params();
  pulse_update_params();
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

uint32_t nextFrameMillis = 0;
float frameCount = 0;
float frameMillis = 0;

const uint32_t FRAME_RATE_REPORT_FREQUENCY_MILLIS = 10000;
uint32_t lastFrameRateReport = 0;

void reactor_loop(CRGBSet &leds)
{
  uint32_t simTime = millis();

  if (desiredMillisPerFrame > 0)
  {
    if (simTime < nextFrameMillis)
    {
      return;
    }

    nextFrameMillis = simTime + desiredMillisPerFrame;
  }

  frameCount++;

  if (reportFrameRate)
  {
    double elapsedReportTime = simTime - lastFrameRateReport;

    if (elapsedReportTime > FRAME_RATE_REPORT_FREQUENCY_MILLIS)
    {
      double frameRate = (frameCount / elapsedReportTime) * 1000;
      Logger.Info("Reactor: Frame Rate %f frames/sec", frameRate);
      frameCount = 0;
      lastFrameRateReport = simTime;
    }
  }

  float elapsedSeconds = (float)(simTime - lastFrameUpdate) / 1000.0;
  lastFrameUpdate = simTime;

  fog_loop(leds, simTime, elapsedSeconds);
  chaser_loop(leds, simTime, elapsedSeconds);
  pulse_loop(leds, simTime, elapsedSeconds);

  if (SHOW_DIAGS)
  {
    drawDiags(leds);
  }

  FastLED.show();
}
