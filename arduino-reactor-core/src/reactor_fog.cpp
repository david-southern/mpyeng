#include "common.h"

bool SHOW_FOG = true;

// Demo parameters
// CruiseParam fogHueParam(HUE_MID_DARK_BLUE, HUE_DARK_BLUE, HUE_LIGHT_BLUE, HUE_DARK_BLUE, EaseLinear);
// CruiseParam fogSaturationParam(200, 255, 64, 255, EaseLinear);
// CruiseParam fogValueParam(80, 200, 180, 255, EaseLinear);
// CruiseParam fogScaleParam(7, 10, EaseLinear);
// CruiseParam fogSpeedParam(2, 12, EaseLinear);

CruiseParam fogHueParam(HUE_DARK_BLUE, HUE_DARK_BLUE, EaseLinear);
CruiseParam fogSaturationParam(255, 255, 16, 255, EaseLinear);
CruiseParam fogValueParam(80, 200, 180, 255, EaseLinear);

CruiseParam fogScaleParam(7);
CruiseParam fogSpeedParam(2, 6, EaseLinear);

float fogSpeed = 0;
float fogScale = 0;

float hPos;
float sPos;
float vPos;

float hScanline;
float sScanline;
float vScanline;

float minHue;
float maxHue;

float minSaturation;
float maxSaturation;

float minValue;
float maxValue;

const int STARTING_POSITION_RANGE = 9;

// The Simplex noise has trouble if we pass 'large' parameters.  Wrap parameter values that exceed this limit.
const float MAX_SIMPLEX_PARAM = 100;
const float SPEED_SCALE_DIVISOR = 100;

void fog_setup()
{
    if (!SHOW_FOG)
    {
        return;
    }

    // Initialize our coordinates to some random values
    hPos = MoarRandom.random() * STARTING_POSITION_RANGE;
    sPos = MoarRandom.random() * STARTING_POSITION_RANGE;
    vPos = MoarRandom.random() * STARTING_POSITION_RANGE;
    hScanline = MoarRandom.random() * STARTING_POSITION_RANGE;
    sScanline = MoarRandom.random() * STARTING_POSITION_RANGE;
    vScanline = MoarRandom.random() * STARTING_POSITION_RANGE;
}

void fog_update_params()
{
    if (!SHOW_FOG)
    {
        return;
    }

    minHue = fogHueParam.MinValue();
    maxHue = fogHueParam.MaxValue();

    minSaturation = fogSaturationParam.MinValue();
    maxSaturation = fogSaturationParam.MaxValue();

    minValue = fogValueParam.MinValue();
    maxValue = fogValueParam.MaxValue();

    fogSpeed = fogSpeedParam.MinValue() / SPEED_SCALE_DIVISOR;
    fogScale = fogScaleParam.MinValue() / SPEED_SCALE_DIVISOR;
}

float genNoise(float index, float pos, float scale, float scanline)
{
    float xParam = pos + index * scale;
    float yParam = scanline;

    float retNoise = SimplexNoise::noiseNormal(xParam, yParam);

    return retNoise;
}

float advanceScanline(float scanline, float speed)
{
    scanline += speed;
    if (scanline > MAX_SIMPLEX_PARAM)
    {
        scanline = 0;
    }

    return scanline;
}

void fog_loop(CRGBSet &leds, uint32_t simTime, float secondsElapsed)
{
    if (!SHOW_FOG)
    {
        return;
    }

    for (int i = 0; i < NUM_LEDS; i++)
    {
        float hNoise = genNoise(i, hPos, fogScale, hScanline);
        float sNoise = genNoise(i, sPos, fogScale, sScanline);
        float vNoise = genNoise(i, vPos, fogScale, vScanline);

        float hFog = lerp(minHue, maxHue, hNoise);
        float sFog = lerp(minSaturation, maxSaturation, sNoise);
        float vFog = lerp(minValue, maxValue, vNoise);

        CHSV pixelColor = CHSV((uint8_t)hFog, (uint8_t)sFog, (uint8_t)vFog);
        leds[i] = pixelColor;
    }

    hScanline = advanceScanline(hScanline, fogSpeed);
    sScanline = advanceScanline(sScanline, fogSpeed);
    vScanline = advanceScanline(vScanline, fogSpeed);
}

// Floating point math on a microcontroller!  Are you nuts!!
//
// Well, I initially wrote this fog module using FastLED's Perlin noise function.  However that library is focused on
// squeezing every last bit of performance and memory use out of older, tiny microcontrollers.  As such, it uses lots of
// integer math and small datatypes, which make the resulting nose defined over a strange range. (the comments say
// approximately -18K to +18K, but I was getting very different min/max values) This makes the generation of the
// interpolated values much more difficult, because I want them to be distributed evenly across the range, so I need
// noise that is uniformly distributed over a known min/max range. In addition, using their noise led to all sorts of
// integer overflow and non-normalized problems.  I was able to get it all to mostly work, but it was a bear to maintain
// and extend, so I decied to re-imp this using floating point math, and just require a more modern MCU.  I also found a
// public domain implementation of Simplex Noise, which is a successor to Perlin noise that gives smoother gradients
// than Perlin.
//
// For reference, this code running on my ESP32 produces 85 frames/sec

// OVERVIEW
//
// I want to create a 'fog' effect by animating a 1-dimension strip of LEDs, modifying the hues, saturations, and values
// of the pixel colors over caller-defined ranges.  We'll generate 2D Simplex noise function and use the Y coordinate as
// a 'scan line' to sample noise values along the X axis so that the permuted attribute values will change smoothly from
// one random value to another.

// <attriute>Speed determines how fast the sampling 'scan line' advances - essentially how quickly the sampled values
// change from one noise area of concentration to another.
//
// Speed guidelines: (with a hue range from 1 - 254, these are the average hue 'distance' shifted per second at various
// speeds.)
//
// *        |   Avg hue   |
// * Speed  |  Shift/sec  | Notes
// * 100    |  6.5 - 11.7 | - very slow change, approx 4-5 seconds to change from one color to another
// * 500    | 40.4 - 51.2 | - noticable gradual color changes, approx one per second
// * 1500   |  135 - 148  | - fast but smooth color changes, 1-3 colors per second
// * 3000   |  270 - 299  | - fast and more extreme color changes, perhaps 4-5/second
// * 10000  |  872 - 955  | - Quite 'flickery', but still coherent blobs of color, maybe 10+ color changes per second
// * 50000  |    2738     | - Extreme flickering, no coherent colors, just "rainbow shades of white" - persistence of
//   vision across all colors

// <attribute>Scale determines how far apart the sampling locations in the noise field are for each pixel.  Smaller
// scale values will tend to cluster multiple pixels in a single noise 'area of concentration', leading to a larger
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
// *        | Avg pixels/ | Avg delta  |
// * Scale  | color blob  | hue/pixel  | Notes
// * 0.02   | 300         | 0          | - Entire strip is the same color (no visible color change)
// * 0.25   | 80          | 0.81       | - Entire strip consisted of three colors zones
// * 1.74   | 20-40       | 4.75       | - Approx 9 color zones
// * 5      | 6 - 15      | 13         | - Approx 22 color zones
// * 10     | 3-5         | 25         |
// * 20     | 1           | 44         | - Every pixel is a different color, but the colors are mostly in adjacent hues
// * 50     | 1           | 64         | - no coherence - almost all adjacent pixels jumping across 4-5 hues
