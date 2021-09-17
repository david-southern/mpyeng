#include "common.h"
#include "limits.h"

// Attribution: This code was copied from the FastLED noise demo code.

// We want to create a 'fog' effect by animating a 1-dimension strip of LEDs, modifying both the hue and the brightness
// with user-defined ranges.  We'll call FastLED's 2D perlin noise function and use the Y coordinate as 'scan line' to
// sample noise values along the X axis so that the permuted attribute values will change smoothly from one random value
// to another.  We'll track separate noise arrays for hue and brightness since they don't need to be related to each
// other. (If we wanted them to be related, we could shift to a 3D noise function and use the X coordinate for the hue
// modification and the Y coordinate for the brightness modification, but I don't know that it would add anything to the
// animation.)

// attriuteSpeed determines how fast the sampling 'scan line' advances - essentially how quickly the sampled values
// change from one perlin noise area of concentration to another.
//
// Speed guidelines: (with a hue range from 1 - 254, these are the average hue 'distance' shifted per second and per
// single loop iteration, at various speeds.)
//
// *        |  Avg hue    |   Avg hue    |
// * Speed  | Shift/sec   | Shift/loop   | Notes
// * 100    |  6.5 - 11.7 | 0.08 - 0.17  | - very slow change, approx 4-5 seconds to change from one color to another
// * 500    | 40.4 - 51.2 | 0.62 - 0.80  | - noticable gradual color changes, approx one per second
// * 1500   |  135 - 148  | 1.92 - 2.29  | - fast but smooth color changes, 1-3 colors per second
// * 3000   |  270 - 299  | 3.93 - 4.48  | - fast and more extreme color changes, perhaps 4-5/second
// * 10000  |  872 - 955  | 12.7 - 14.1  | - Quite 'flickery', but still coherent blobs of color, maybe 10+ color changes per second
// * 50000  |    2738     |     40       | - Extreme flickering, no coherent colors, just "rainbow shades of white" - persistence of vision across all colors

uint16_t hueSpeed = 3000;
uint16_t brightnessSpeed = 3000;

// attributeScale determines how far apart the sampling locations in the noise field are for each pixel.  Smaller scale
// values will tend to cluster multiple pixels in a single perlin noise 'area of concentration', leading to a larger
// 'blob' of similarly colored pixels and more gradual color changes between groups of adjacent pixels.  Higher scale
// values essentially 'zoom out' the sampling of the noise field, making for smaller color blobs and more rapid color
// changes.
//
// Extremely low scale values will result in color changing so slowly that all pixels will appear to be the same color.
// Very large scale values will essentially make the pixel values unrelated to each other (i.e. 'random')
//
// Scale guidelines: (with a hue range from 1 - 254, and a strip length of 300 pixels these are the average pixel counts
// of 'color blobs' - areas of pixels that are essentially the same color - at various scale values)
//
// *        | Avg pixels/ | Transition |
// * Scale  | color blob  | pixels     | Notes
// * 10     | 300         | 0          | - Entire strip is the same color (no visible color change)
// * 100    | 80          | 30         | - Entire strip consisted of three colors - green to cyan to blue
// * 500    | 20-40       | 20-40      | - Approx 9 color zones
// * 1500   | 6 - 15      | 3-5        | - Approx 22 color zones
// * 15000  | 1 - 3       | 0 - 1      |
// * 30000  | 1           | 0          | - Every pixel is a different color, but the colors are mostly in adjacent hues
// * 60000  | 1           | 0          | - no coherence - multiple cases of adjacent pixels jumping across 4-5 hues
uint16_t hueScale = 16000;
uint16_t brightnessScale = 16000;

static uint32_t hueTime;
static uint32_t brightnessTime;

static uint32_t huePosition;
static uint32_t brightnessPosition;

int16_t hueNoise[NUM_LEDS];
int16_t brightnessNoise[NUM_LEDS];

uint32_t random32()
{
    uint32_t retval = random16();
    return (retval << 16) | random16();
}

unsigned long HASH_BASE = 5381;
unsigned long nextHash(unsigned long hash, unsigned long nextInt)
{
    return ((hash << 5) + hash) + nextInt; /* hash * 33 + nextInt */
}

void fog_setup()
{
    // Lots of Arduino code suggests analogRead() from an unconnected analog pin as a way to generate entropy.  In
    // practice, though, on my Arduino Due, I see the analogRead of a pin clustering within about 10 integers of the
    // same value, over multiple resets.  Different pins appear to cluster around different values, but even then they
    // are close. (i.e. all within the 700-800 range)  Given this, try to get a little bit of entropy by reading four
    // different pins, and hashing the results together.
    uint32_t randSeed = nextHash(HASH_BASE, analogRead(0));
    randSeed = nextHash(randSeed, analogRead(1));
    randSeed = nextHash(randSeed, analogRead(2));
    randSeed = nextHash(randSeed, analogRead(3));
    randSeed = randSeed & 0xffff;
    // random16_set_seed(randSeed);
    random16_set_seed(42);

    // Initialize our coordinates to some random values
    huePosition = random32();
    brightnessPosition = random32();
    hueTime = random32();
    brightnessTime = random32();
}

int32_t MIN_RAW_NOISE = -11508;
int32_t MAX_RAW_NOISE = 10750;
int32_t RAW_NOISE_DELTA = MAX_RAW_NOISE - MIN_RAW_NOISE;

int16_t adjustableRawNoise(uint32_t x, uint32_t y)
{
    int32_t retval = inoise16_raw(x, y);

    if(retval < MIN_RAW_NOISE) {
        MIN_RAW_NOISE = retval;
        RAW_NOISE_DELTA = MAX_RAW_NOISE - MIN_RAW_NOISE;
    }

    if(retval > MAX_RAW_NOISE) {
        MAX_RAW_NOISE = retval;
        RAW_NOISE_DELTA = MAX_RAW_NOISE - MIN_RAW_NOISE;
    }

    return (int16_t)retval;
}

void fillnoise()
{
    for (int i = 0; i < NUM_LEDS; i++)
    {
        hueNoise[i] = adjustableRawNoise(huePosition + i * hueScale, hueTime);
        brightnessNoise[i] = adjustableRawNoise(brightnessPosition + i * brightnessScale, brightnessTime);
    }
    hueTime += hueSpeed;
    brightnessTime += brightnessSpeed;
}

// Note: FastLED defined its hue range from 0 - 255, rather than 0-360.  Check this page for a visual representation of
// the FastLED hue range:
//
// https://github.com/FastLED/FastLED/wiki/FastLED-HSV-Colors
uint16_t fogHueStart = 140; // Blue-Aqua
uint16_t fogHueEnd = 168;   // Blue-Purple
// uint16_t fogHueStart = 0; // Full Range Test
// uint16_t fogHueEnd = 255;

uint16_t minBrightness = 16;
uint16_t maxBrightness = 250;

unsigned int fogDiags = 0;
double fogDiagFreqSec = 3;

unsigned int prevHue = 0;
double totalShift = 0;
double shiftSamples = 0;

int32_t minHue = INT32_MAX;
int32_t maxHue = INT32_MIN;

uint16_t normalizeNoise(int16_t rawNoise)
{
    int32_t noise32 = rawNoise;
    float adj32 = noise32 - MIN_RAW_NOISE;
    float normalizedNoiseFloat = adj32 / (float)RAW_NOISE_DELTA;
    uint16_t retval = (uint16_t)(normalizedNoiseFloat * UINT16_MAX);
    return retval;
}

void fog_loop(CRGBSet &leds)
{
    bool canShowDiags = millis() > 2000 && millis() < 3000;

    if (millis() > fogDiags)
    {
        fogDiags = millis() + fogDiagFreqSec * 1000;
    }

    fillnoise();

    int32_t loopMinHue = INT32_MAX;
    int32_t loopMaxHue = INT32_MIN;

    for (int i = 0; i < NUM_LEDS; i++)
    {
        // uint8_t fogHue = i % 255;
        // leds[i] = CHSV(fogHue, 255, 128);
        int32_t normalizedHueNoise = normalizeNoise(hueNoise[i]);
        int32_t fogHue = lerp16by16(fogHueStart, fogHueEnd, normalizedHueNoise);

        int32_t normalizedBrightnessNoise = normalizeNoise(brightnessNoise[i]);
        int32_t fogBrightness = lerp16by16(minBrightness, maxBrightness, normalizedBrightnessNoise);
        CHSV pixelColor = CHSV(fogHue, 255, fogBrightness);
        leds[i] = pixelColor;

        minHue = min(fogBrightness, minHue);
        maxHue = max(fogBrightness, maxHue);
        loopMinHue = min(fogBrightness, loopMinHue);
        loopMaxHue = max(fogBrightness, loopMaxHue);


        // if (i == 3)
        // {
        //     if (prevHue == 0)
        //     {
        //         prevHue = fogHue;
        //     }
        //     int thisShift = abs((int)prevHue - (int)fogHue);
        //     totalShift += thisShift;
        //     shiftSamples++;
        //     prevHue = fogHue;

        //     if (FOGshowDiags)
        //     {
        //         Logger.Info(F("Fog[3]: avg shift/sec: %f, avgShift/loop: %f, sampled: %d, hue: %u, brightness: %u"),
        //                     totalShift / fogDiagFreqSec, (totalShift / shiftSamples), (int)shiftSamples, fogHue, fogBrightness);
        //         totalShift = 0;
        //         shiftSamples = 0;
        //     }
        // }
    }

    // if (FOGshowDiags)
    // {
    //     Logger.Info(F("Fog: Loop Min: %d, Loop Max: %d, Overall Min: %d, Overall Max: %d"),
    //                 (int)loopMinHue, (int)loopMaxHue, (int)minHue, (int)maxHue);
    // }

    LEDS.show();
}