#include "common.h"

const int TEST_COLORS = 4;

uint32_t stripTestColors[] = {
    CRGB::Black,
    // Darker
    CRGB::Red,
    CRGB::Green,
    CRGB::Blue,
    // Lighter
};
// uint32_t stripTestColors[] = {
//     CRGB::Black,
//     // Darker
//     CRGB::Navy,
//     CRGB::DarkBlue,
//     CRGB::MediumBlue,
//     CRGB::Blue,
//     CRGB::DarkCyan,
//     CRGB::DeepSkyBlue,
//     CRGB::Cyan,
//     CRGB::DodgerBlue,
//     CRGB::Turquoise,
//     CRGB::MediumTurquoise,
//     CRGB::CornflowerBlue,
//     CRGB::CadetBlue,
//     CRGB::MediumAquamarine,
//     CRGB::Aquamarine,
//     // Lighter
// };

void strip_test_setup()
{
}

const unsigned long STRIP_TEST_DURATION = 3500;
unsigned long nextStripChange = 0;
unsigned int stripIndex = 0;

void strip_test_loop(CRGBSet &leds)
{
  if (millis() > nextStripChange)
  {
    Logger.Info(F("StripTest: Color: #%x"), stripTestColors[stripIndex]);

    FastLED.showColor(stripTestColors[stripIndex]);
    stripIndex++;
    if (stripIndex >= TEST_COLORS)
    {
      stripIndex = 0;
    }

    nextStripChange = millis() + STRIP_TEST_DURATION;
  }
}
