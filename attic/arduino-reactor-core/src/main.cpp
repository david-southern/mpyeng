#include "common.h"

enum ProgramMode
{
  StripTest,
  Reactor,
};

const ProgramMode mode = Reactor;

CRGBArray<NUM_LEDS> leds;

const int BUTTON_DEBOUNCE_MILLIS = 20;

Bounce2::Button cruiseLevelUp = Bounce2::Button();
Bounce2::Button cruiseLevelDown = Bounce2::Button();

void setup()
{
  pinMode(LED_BUILTIN, OUTPUT);

  cruiseLevelUp.attach(CRUISE_UP_PIN, INPUT_PULLDOWN);
  cruiseLevelUp.interval(BUTTON_DEBOUNCE_MILLIS);
  cruiseLevelUp.setPressedState(HIGH);

  cruiseLevelDown.attach(CRUISE_DOWN_PIN, INPUT_PULLDOWN);
  cruiseLevelDown.interval(BUTTON_DEBOUNCE_MILLIS);
  cruiseLevelDown.setPressedState(HIGH);

  unsigned int serialWaitExpire = millis() + 1500;

  Logger.InitializeSerial();

  while (!Serial && millis() < serialWaitExpire)
  {
    ; // wait for serial port to connect. Needed for native USB
  }

  Logger.SetLogLevel(LOG_LEVEL_INFO);

  MoarRandom.setRandomSeed(MoarRandom.generateRandomSeed(4, A0, A1, A2, A3));

  Logger.Info(F("SpaceSimWarp starting up"));

  FastLED.addLeds<LED_TYPE, LED_DATA_PIN, COLOR_ORDER>(leds, NUM_LEDS).setCorrection(TypicalLEDStrip);
  FastLED.setBrightness(BRIGHTNESS);

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

unsigned int BLINK_DURATION = 1000;
int blinkMode = 1;
unsigned int nextBlinkTime = 0;
unsigned int prevBlinkTime = 0;

float cruise_level = 0;
float button_cruise_step = 0.1;

void loop()
{
  unsigned int simTime = millis();

  if (simTime > nextBlinkTime)
  {
    nextBlinkTime = simTime + BLINK_DURATION;

    digitalWrite(LED_BUILTIN, blinkMode);
    blinkMode = !blinkMode;
  }

  cruiseLevelUp.update();
  cruiseLevelDown.update();

  if (cruiseLevelUp.pressed())
  {
    cruise_level += button_cruise_step;
    if (cruise_level > 1.0)
    {
      cruise_level = 1.0;
    }

    reactor_cruise(cruise_level);

    BLINK_DURATION = 1000 - cruise_level * 900;
  }

  if (cruiseLevelDown.pressed())
  {
    cruise_level -= button_cruise_step;
    if (cruise_level < 0.0)
    {
      cruise_level = 0.0;
    }
    reactor_cruise(cruise_level);

    BLINK_DURATION = 1000 - cruise_level * 900;
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
