#pragma once

#include <Arduino.h>

#include <inttypes.h>
#include <stdarg.h>
#include <stdlib.h>
#include <limits.h>
#include <cmath>
#include <map>

// This line suppresses the FastLED warning advertising the FastLED version...
#define FASTLED_INTERNAL
#include "FastLED.h"

#include "Bounce2.h"

#include "utils.h"
#include "easing.h"

#include "RandomGenerator.h"
#include "ArduinoLog.h"
#include "SimplexNoise.h"

#include "fog.h"
#include "reactor.h"
#include "strip_test.h"

// Arduino library includes constrain(), but I prefer to call it clamp()
#define clamp constrain

#ifndef LOW_MEMORY_LOGGING
#define NUM_LEDS 300
#else
#define NUM_LEDS 100
#endif

#define VOLTS 12
#define MAX_MA 4000
#define LED_TYPE WS2812B
#define COLOR_ORDER RGB
#define DATA_PIN 12
#define BRIGHTNESS 250

#define CRUISE_UP_PIN 11
#define CRUISE_DOWN_PIN 10

#define FOG_DOUBLE
