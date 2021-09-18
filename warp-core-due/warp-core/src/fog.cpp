#include "common.h"
#include "limits.h"

#ifdef FOG_DOUBLE
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
// than Perlin

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

void initParams()
{
    setFogParamSpeed(FogParam_H, 7);
    setFogParamScale(FogParam_H, 7);

    setFogParamSpeed(FogParam_S, 5);
    setFogParamScale(FogParam_S, 5);

    setFogParamSpeed(FogParam_V, 5);
    setFogParamScale(FogParam_V, 5);
}

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

float hSpeed = 0;
float sSpeed = 0;
float vSpeed = 0;

float hScale = 0;
float sScale = 0;
float vScale = 0;

float hPos;
float sPos;
float vPos;

float hScanline;
float sScanline;
float vScanline;

// Note: FastLED defines its hue range from 0 - 255, rather than 0-360.  Check this page for a visual representation of
// the FastLED hue range:
//
// https://github.com/FastLED/FastLED/wiki/FastLED-HSV-Colors
float hStart = 140; // Blue-Aqua
float hEnd = 165;   // Blue-Purple

// float hStart = 0; // Full Range Test
// float hEnd = 254;

float sStart = 200;
float sEnd = 255;

float vStart = 32;
float vEnd = 255;

const int STARTING_POSITION_RANGE = 9;

// The Simplex noise has trouble if we pass 'large' parameters.  Wrap parameter values that exceed this limit.
const float MAX_SIMPLEX_PARAM = 100;

void setFogParamRange(FogParam param, float start, float end)
{
    switch (param)
    {
    case FogParam_H:
        hStart = start;
        hEnd = end;
        break;
    case FogParam_S:
        sStart = start;
        sEnd = end;
        break;
    case FogParam_V:
        vStart = start;
        vEnd = end;
        break;
    }
}

void setFogParamSpeed(FogParam param, float speed)
{
    switch (param)
    {
    case FogParam_H:
        hSpeed = speed / 100;
        break;
    case FogParam_S:
        sSpeed = speed / 100;
        break;
    case FogParam_V:
        vSpeed = speed / 100;
        break;
    }
}

void setFogParamScale(FogParam param, float scale)
{
    switch (param)
    {
    case FogParam_H:
        hScale = scale / 100;
        Logger.Info("Set hScale to %f", hScale);
        break;
    case FogParam_S:
        sScale = scale / 100;
        break;
    case FogParam_V:
        vScale = scale / 100;
        break;
    }
}

void fog_setup()
{
    MoarRandom.randomizeRandomSeed();

    // Initialize our coordinates to some random values
    hPos = MoarRandom.random() * STARTING_POSITION_RANGE;
    sPos = MoarRandom.random() * STARTING_POSITION_RANGE;
    vPos = MoarRandom.random() * STARTING_POSITION_RANGE;
    hScanline = MoarRandom.random() * STARTING_POSITION_RANGE;
    sScanline = MoarRandom.random() * STARTING_POSITION_RANGE;
    vScanline = MoarRandom.random() * STARTING_POSITION_RANGE;

    Logger.Info(F("Starting with h: (%f, %f), s: (%f, %f), v: (%f, %f)"), hPos, hScanline, sPos, sScanline, vPos, vScanline);

    initParams();
}

unsigned int fogDiags = 0;
float fogDiagFreqSec = 1;

#ifdef DIAGNOSE_SHIFT_RATE
unsigned int prevHue = 0;
float totalShift = 0;
float shiftSamples = 0;
#endif

// #define DIAGNOSE_MIN_MAX

#ifdef DIAGNOSE_MIN_MAX
float minVal = STARTING_POSITION_RANGE;
float maxVal = -STARTING_POSITION_RANGE;
float maxX = -MAX_SIMPLEX_PARAM;
float minX = MAX_SIMPLEX_PARAM;
float maxY = -MAX_SIMPLEX_PARAM;
float minY = MAX_SIMPLEX_PARAM;
#endif

float genNoise(float index, float pos, float scale, float scanline)
{
    float xParam = pos + index * scale;
    float yParam = scanline;

#ifdef DIAGNOSE_MIN_MAX
    maxX = max(xParam, maxX);
    minX = min(xParam, minX);
    maxY = max(yParam, maxY);
    minY = min(yParam, minY);
#endif

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

bool showFogDiags = false;

float logXParam[NUM_LEDS];
float logNoise[NUM_LEDS];
float logDelta[NUM_LEDS];
float logV[NUM_LEDS];

void fog_loop(CRGBSet &leds)
{
    // if (showFogDiags)
    // {
    //     if (millis() > fogDiags)
    //     {
    //         double totalDeltaN = 0;
    //         double totalDeltaV = 0;
    //         double prevV = logV[0];
    //         for (int i = 0; i < NUM_LEDS; i++)
    //         {
    //             Logger.Info("LED: %d, scale: %f, xP: %f, noise: %f, v: %f, deltaNoise: %f", i, hScale, logXParam[i], logNoise[i], logV[i], logDelta[i]);
    //             totalDeltaN += logDelta[i];
    //             double deltaV = abs(logV[i] - prevV);
    //             totalDeltaV += deltaV;
    //             prevV = logV[i];
    //         }
    //         Logger.Info("Scale: %f, average deltaNoise: %f, avg deltaV: %f", hScale, totalDeltaN / NUM_LEDS, totalDeltaV / NUM_LEDS);
    //         fogDiags = LONG_MAX;
    //     }
    //     return;
    // }

    // // float prevNoise = SimplexNoise::noiseNormal(0, 42);
    // float prevNoise = genNoise(0, hPos, hScale, hScanline);

    // for (int i = 0; i < NUM_LEDS; i++)
    // {
    //     float xParam = hPos + i * hScale;

    //     logXParam[i] = xParam;

    //     // float noise = SimplexNoise::noiseNormal(xParam, 42);
    //     float noise = genNoise(i, hPos, hScale, hScanline);
    //     logNoise[i] = noise;

    //     uint8_t vNoise = noise * 255;

    //     leds[i] = CHSV(vNoise, 255, 255);

    //     float deltaNoise = abs(noise - prevNoise);
    //     logDelta[i] = deltaNoise;
    //     logV[i] = (float)vNoise;

    //     prevNoise = noise;

    //     hScanline = advanceScanline(hScanline, hSpeed);
    // }

    // FastLED.show();

    // fogDiags = millis() + fogDiagFreqSec * 1000;
    // showFogDiags = true;
    // return;

    showFogDiags = false;
    if (millis() > fogDiags)
    {
        fogDiags = millis() + fogDiagFreqSec * 1000;
        showFogDiags = true;
    }

#ifdef DIAGNOSE_MIN_MAX
    maxX = -MAX_SIMPLEX_PARAM;
    minX = MAX_SIMPLEX_PARAM;
    maxY = -MAX_SIMPLEX_PARAM;
    minY = MAX_SIMPLEX_PARAM;
    minVal = 10;
    maxVal = -10;
#endif

    for (int i = 0; i < NUM_LEDS; i++)
    {
        // Strip Test
        // uint8_t hFog = i % 255;
        // leds[i] = CHSV(hFog, 255, 128);
        // continue;

        float hNoise = genNoise(i, hPos, hScale, hScanline);
        float sNoise = genNoise(i, sPos, sScale, sScanline);
        float vNoise = genNoise(i, vPos, vScale, vScanline);

        float hFog = lerp(hStart, hEnd, hNoise);
        float sFog = lerp(sStart, sEnd, sNoise);
        float vFog = lerp(vStart, vEnd, vNoise);

        CHSV pixelColor = CHSV((uint8_t)hFog, (uint8_t)sFog, (uint8_t)vFog);
        leds[i] = pixelColor;

#ifdef DIAGNOSE_MIN_MAX
        minVal = min(hNoise, minVal);
        maxVal = max(hNoise, maxVal);
#endif

#ifdef DIAGNOSE_SHIFT_RATE
        if (i == 3)
        {
            if (prevHue == 0)
            {
                prevHue = hFog;
            }
            int thisShift = abs((int)prevHue - (int)hFog);
            totalShift += thisShift;
            shiftSamples++;
            prevHue = hFog;

            if (showFogDiags)
            {
                Logger.Info(F("Fog[3]: avg shift/sec: %f, avgShift/loop: %f, sampled: %d, hue: %u, brightness: %u"),
                            totalShift / fogDiagFreqSec, (totalShift / shiftSamples), (int)shiftSamples, hFog, vFog);
                totalShift = 0;
                shiftSamples = 0;
            }
        }
#endif // DIAGNOSE_SHIFT_RATE
    }

    hScanline = advanceScanline(hScanline, hSpeed);
    sScanline = advanceScanline(sScanline, sSpeed);
    vScanline = advanceScanline(vScanline, vSpeed);

#ifdef DIAGNOSE_MIN_MAX
    if (showFogDiags)
    {
        Logger.Info(F("Fog: hNoise Min: %f, hNoise Max: %f, hPos: %f, hScanline: %f, minX: %f, maxX: %f, minY: %f, maxY: %f"),
                    minVal, maxVal, hPos, hScanline, minX, maxX, minY, maxY);
    }
#endif // DIAGNOSE_MIN_MAX

    FastLED.show();
}
#endif