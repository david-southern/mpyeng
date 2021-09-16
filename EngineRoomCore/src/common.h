#pragma once

#include <Arduino.h>

#include "FastLED.h"

#include "ArduinoLog.h"

#include "twinkle.h"
#include "reactor.h"
#include "strip_test.h"

// Arduino library includes constrain(), but I prefer to call it clamp()
#define clamp constrain

#ifndef LOW_MEM
#define NUM_LEDS 100
#else
#define NUM_LEDS 300
#endif

#define VOLTS 12
#define MAX_MA 4000
#define LED_TYPE WS2812B
#define COLOR_ORDER RGB
#define DATA_PIN 3
#define BRIGHTNESS 128
