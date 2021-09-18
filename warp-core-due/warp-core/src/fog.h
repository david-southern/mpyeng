#pragma once

#include <FastLED.h>

enum FogParam
{
    FogParam_H,
    FogParam_S,
    FogParam_V
};

/**
 * Indicate the start/end range of the parameter that should be applied to the noise function
 */
void setFogParamRange(FogParam param, float start, float end);

/**
 * Indicate how quickly the parameter's values should change over time.  Typical speed values should range from 5 - 10.
 */
void setFogParamSpeed(FogParam param, float speed);

/**
 * Indicate how dramatically the parameter's values should change from one pixel to the next. Typical scale values should range from 5 - 10.
 */
void setFogParamScale(FogParam param, float scale);

void fog_setup();
void fog_loop(CRGBSet &leds);