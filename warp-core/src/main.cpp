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

  unsigned long serialWaitExpire = millis() + 1500;

  // Serial.begin(115200);
  Logger.InitializeSerial();

  while (!Serial && millis() < serialWaitExpire)
  {
    ; // wait for serial port to connect. Needed for native USB
  }

  delay(3000);

  // Analog pin config for ESP32
  MoarRandom.setRandomSeed(MoarRandom.generateRandomSeed(4, 26, 25, 34, 39));

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

unsigned long CRUISE_DURATION = 300;
unsigned long nextCruiseShift = 0;
float cruise_level = 0;
float cruise_step = 0.002;
float button_cruise_step = 0.1;

void loop()
{
  cruiseLevelUp.update();
  cruiseLevelDown.update();

  if (cruiseLevelUp.pressed())
  {
    cruise_level += button_cruise_step;
    if(cruise_level > 1.0) {
      cruise_level = 1.0;
    }

    reactor_cruise(cruise_level);
  }

  if (cruiseLevelDown.pressed())
  {
    cruise_level -= button_cruise_step;
    if(cruise_level < 0.0) {
      cruise_level = 0.0;
    }
    reactor_cruise(cruise_level);
  }

  unsigned long simTime = millis();

  if (simTime > nextBlink)
  {
    nextBlink = simTime + BLINK_DURATION;

    digitalWrite(LED_BUILTIN, blinkMode);
    blinkMode = !blinkMode;
  }

  // if (simTime > nextCruiseShift)
  // {
  //   nextCruiseShift = simTime + CRUISE_DURATION;

  //   cruise_level += cruise_step;

  //   if (cruise_level > 1)
  //   {
  //     cruise_level = 0;
  //   }

  //   reactor_cruise(cruise_level);

  //   BLINK_DURATION = 1000 - cruise_level * 100;
  // }

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
