#include "common.h"

enum ProgramMode
{
  Undefined,
  StripTest,
  Reactor,
};

const ProgramMode mode = Reactor;

CRGBArray<NUM_LEDS> leds;

void setup()
{
  pinMode(LED_BUILTIN, OUTPUT);

  unsigned long serialWaitExpire = millis() + 1500;

  // Serial.begin(115200);
  Logger.InitializeSerial();

  while (!Serial && millis() < serialWaitExpire)
  {
    ; // wait for serial port to connect. Needed for native USB
  }

  Logger.SetLogLevel(LOG_LEVEL_INFO);
  Logger.Info("SpaceSimWarp starting up");

  FastLED.addLeds<LED_TYPE, DATA_PIN, COLOR_ORDER>(leds, NUM_LEDS).setCorrection(TypicalLEDStrip);
  FastLED.setBrightness(BRIGHTNESS);
  FastLED.setMaxPowerInVoltsAndMilliamps(VOLTS, MAX_MA);

  Logger.Info("SpaceSimWarp starting up: A");
  switch (mode)
  {
  case StripTest:
    strip_test_setup();
    break;

  case Reactor:
  Logger.Info("SpaceSimWarp starting up: B");
    reactor_setup();
    break;
  }
}

unsigned long BLINK_DURATION = 1000;
unsigned long nextBlink = 0;
int blinkMode = 1;

unsigned long CRUISE_DURATION = 3000;
unsigned long nextCruiseShift = 0;
unsigned int cruise_level = 0;

void loop()
{
  unsigned long simTime = millis();

  if (simTime > nextBlink)
  {
    nextBlink = simTime + BLINK_DURATION;

    digitalWrite(LED_BUILTIN, blinkMode);
    blinkMode = !blinkMode;
  }

  if (simTime > nextCruiseShift)
  {
    nextCruiseShift = simTime + CRUISE_DURATION;

    reactor_cruise(cruise_level);

    cruise_level++;
    if (cruise_level >= 10)
    {
      cruise_level = 0;
    }

    BLINK_DURATION = 1000 - cruise_level * 100;
  }

  switch (mode)
  {
  case StripTest:
    strip_test_loop(leds);
    break;

  case Reactor:
    reactor_loop(leds);
    break;
  }
}
