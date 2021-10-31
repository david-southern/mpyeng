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

#include "reactor_fog.h"
#include "reactor_control.h"
#include "strip_test.h"

// Arduino library includes constrain(), but I prefer to call it clamp()
#define clamp constrain

#define BRIGHTNESS 250
#ifndef LOW_MEMORY_LOGGING
#define NUM_LEDS 976
#else
#define NUM_LEDS 100
#endif

#define LED_TYPE WS2812B

// 12-volt strip
// #define COLOR_ORDER RGB

// 5-volt strip
#define COLOR_ORDER GRB

// For ESP32
#define LED_DATA_PIN 15
#define CRUISE_UP_PIN 14
#define CRUISE_DOWN_PIN 32

// For Feather M4 Express
// #define LED_DATA_PIN 12
// #define CRUISE_UP_PIN 11
// #define CRUISE_DOWN_PIN 10



void checkBlink(const char *loc);
