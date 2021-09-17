#include "common.h"

// Attribution: This code was copied from the FastLED noise demo code.

// We want to create a 'fog' effect by animating a 1-dimension strip of LEDs, modifying both the hue around a central
// hue, and the brightness from a minimum to a maximum.  We'll call FastLED's 2D perlin noise function and use the Y
// coordinate as 'time' so that the X coordinate values will change smoothly.  We'll track separate noise arrays for hue
// and brightness since they don't need to be related to each other.  (If we wanted them to be related, we could shift
// to a 3D noise function and use the X coordinate for the hue modification and the Y coordinate for the brightness
// modification, but that would take a lot more memory, and I don't know that it would add anything to the animation.)

// Speed determines how fast time moves forward.  Try 1 for a very slow moving effect, almost static, or 60 for
// something that ends up looking like water.
uint16_t hueSpeed = 10;
uint16_t brightnessSpeed = 10;

// Scale determines how far apart the pixels in our noise field are.  Try changing these values around to see how it
// affects the motion of the display.  The higher the value of scale, the more "zoomed out" the noise will be.  A value
// of 1 will be so zoomed in, you'll mostly see solid colors, (very little variation from one pixel to the next) while a
// scale of 4000 wll be very zoomed out and the variation from pixel to pixel will be basically random

uint16_t hueScale = 311;
uint16_t brightnessScale = 311;

static uint32_t hueTime;
static uint32_t brightnessTime;

static uint32_t huePosition;
static uint32_t brightnessPosition;

uint16_t hueNoise[NUM_LEDS];
uint16_t brightnessNoise[NUM_LEDS];

uint32_t random32()
{
    uint32_t retval = random16();
    return (retval << 16) | random16();
}

void noise_setup()
{
    // Initialize our coordinates to some random values
    huePosition = random32();
    brightnessPosition = random32();
    hueTime = random32();
    brightnessTime = random32();
}

void fillnoise()
{
    for (int i = 0; i < NUM_LEDS; i++)
    {
        hueNoise[i] = inoise16(huePosition + i * hueScale, hueTime);
        brightnessNoise[i] = inoise16(brightnessPosition + i * brightnessScale, brightnessTime);
    }
    hueTime += hueSpeed;
    brightnessTime += brightnessSpeed;
}

// Note: FastLED defined its hue range from 0 - 255, rather than 0-360.  Check this page for a visual representation of
// the FastLED hue range:
//
// https://github.com/FastLED/FastLED/wiki/FastLED-HSV-Colors
uint16_t fogHueStart = 140; // Blue-Aqua
uint16_t fogHueEnd = 172;   // Blue-Purple

uint16_t minBrightness = 16;
uint16_t maxBrightness = 255;

void noise_loop(CRGBSet &leds)
{
    fillnoise();

    for (int i = 0; i < NUM_LEDS; i++)
    {
        uint8_t fogHue = lerp16by16(fogHueStart, fogHueEnd, hueNoise[i]) & 0xFF;
        uint8_t fogBrightness = lerp16by16(minBrightness, maxBrightness, brightnessNoise[i]) & 0xFF;
        leds[i] = CHSV(fogHue, 255, fogBrightness);
    }

    LEDS.show();
}