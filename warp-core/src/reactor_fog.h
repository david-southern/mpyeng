#pragma once

#include "common.h"

enum FogParam
{
    FogParam_H,
    FogParam_S,
    FogParam_V
};

extern const char *FogParamName[];

/**
 * Set the desired frame rate for the fog animation.  If your processor can run faster than this then the fog sim will
 * not consume more CPU than needed to achieve this rate.
 */
void setFogFrameRate(float framesPerSec);

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
bool fog_loop(CRGBSet &leds);