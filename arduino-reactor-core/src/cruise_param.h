#pragma once

#include "common.h"

class CruiseParam
{
private:
  float InterpolateByPower(float lowValue, float highValue, easing_functions easingFunc)
  {
    auto easingFunction = getEasingFunction(easingFunc);
    double progress = easingFunction(CorePowerLevel);
    return lerp(lowValue, highValue, progress);
  }

public:
  CruiseParam(float constantValue)
  {
    LowPowerMinValue = constantValue;
    LowPowerMaxValue = constantValue;
    LowPowerAvgValue = constantValue;
    
    HighPowerMinValue = constantValue;
    HighPowerMaxValue = constantValue;
    HighPowerAvgValue = constantValue;

    PowerLevelEasingFunc = EaseLinear;
  }

  CruiseParam(float lowPowerValue, float highPowerValue, easing_functions easingFunc)
  {
    LowPowerMinValue = lowPowerValue;
    LowPowerMaxValue = lowPowerValue;
    LowPowerAvgValue = lowPowerValue;

    HighPowerMinValue = highPowerValue;
    HighPowerMaxValue = highPowerValue;
    HighPowerAvgValue = highPowerValue;

    PowerLevelEasingFunc = easingFunc;
  }

  CruiseParam(float lowPowerMinValue, float lowPowerMaxValue, float highPowerMinValue, float highPowerMaxValue, easing_functions easingFunc)
  {
    LowPowerMinValue = lowPowerMinValue;
    LowPowerMaxValue = lowPowerMaxValue;
    LowPowerAvgValue = (lowPowerMinValue + lowPowerMaxValue) / 2;

    HighPowerMinValue = highPowerMinValue;
    HighPowerMaxValue = highPowerMaxValue;
    HighPowerAvgValue = (highPowerMinValue + highPowerMaxValue) / 2;

    PowerLevelEasingFunc = easingFunc;
  }

  // When the reactor is at its lowest level, what are the min/max values of the parameter
  float LowPowerMinValue;
  float LowPowerMaxValue;
  float LowPowerAvgValue;

  // When the reactor is at its highest level, what are the min/max values of the parameter
  float HighPowerMinValue;
  float HighPowerMaxValue;
  float HighPowerAvgValue;

  // Given the ranges above, how should the power level interpolate the min/max bounds from low power to high power. See
  // https://easings.net/ for a description of what the various easing functions look like
  easing_functions PowerLevelEasingFunc;

  float Value()
  {
    return InterpolateByPower(LowPowerAvgValue, HighPowerAvgValue, PowerLevelEasingFunc);
  }

  float MinValue()
  {
    return InterpolateByPower(LowPowerMinValue, HighPowerMinValue, PowerLevelEasingFunc);
  }

  float MaxValue()
  {
    return InterpolateByPower(LowPowerMaxValue, HighPowerMaxValue, PowerLevelEasingFunc);
  }

  float RandomValue()
  {
    return lerp(MinValue(), MaxValue(), MoarRandom.randomFloat());
  }
};

