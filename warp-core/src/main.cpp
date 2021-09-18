#include "common.h"

enum ProgramMode
{
  Undefined,
  StripTest,
  Reactor,
};

const ProgramMode mode = Reactor;

CRGBArray<NUM_LEDS> leds;

void fog_setup();
void fog_loop(CRGBSet &leds);

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
  Logger.Info(F("SpaceSimWarp starting up"));

  FastLED.addLeds<LED_TYPE, DATA_PIN, COLOR_ORDER>(leds, NUM_LEDS).setCorrection(TypicalLEDStrip);
  FastLED.setBrightness(BRIGHTNESS);
  FastLED.setMaxPowerInVoltsAndMilliamps(VOLTS, MAX_MA);

  switch (mode)
  {
  case StripTest:
    strip_test_setup();
    break;

  case Reactor:
    reactor_setup();
    break;
  }
}

unsigned long BLINK_DURATION = 1000;
unsigned long nextBlink = 0;
int blinkMode = 1;

unsigned long CRUISE_DURATION = 3000;
unsigned long nextCruiseShift = 0;
float cruise_level = 0;
float cruise_step = 0.1;

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

    cruise_level += cruise_step;

    if (cruise_level > 1)
    {
      cruise_level = 0;
    }

    reactor_cruise(cruise_level);

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
