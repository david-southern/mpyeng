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

// Arduino library includes constrain(), but I prefer to call it clamp()
#define clamp constrain

#define BRIGHTNESS 250
#define NUM_LEDS 976
#define LED_TYPE WS2812B

#define COLOR_ORDER GRB

// For ESP32
#define LED_DATA_PIN 15
#define CRUISE_UP_PIN 14
#define CRUISE_DOWN_PIN 32

// For Feather M4 Express
// #define LED_DATA_PIN 12
// #define CRUISE_UP_PIN 11
// #define CRUISE_DOWN_PIN 10

#define REACTOR_SEGMENTS 8
#define SEGMENT_SIZE 122
#define SEGMENTS_ALTERNATE_DIRECTION true

// The level of power being drawn from the reactor code, expressed as a floating point value on the range [0, 1]
extern float CorePowerLevel;

// Note: FastLED defines its hue range from 0 - 255, rather than 0-360.  Check this page for a visual representation of
// the FastLED hue range:
//
// https://github.com/FastLED/FastLED/wiki/FastLED-HSV-Colors
#define HUE_RED 0
#define HUE_ORANGE 32
#define HUE_YELLOW 64
#define HUE_GREEN 96
#define HUE_CYAN 128
#define HUE_BLUE 160
#define HUE_MAGENTA 192
#define HUE_PINK 224

#define HUE_DARK_BLUE 165
#define HUE_MID_DARK_BLUE 150
#define HUE_MID_LIGHT_BLUE 145
#define HUE_LIGHT_BLUE 138

#include "cruise_param.h"
#include "reactor.h"
#include "strip_test.h"
