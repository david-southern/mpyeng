#pragma once

#include "FastLED.h"

void reactor_setup();
void reactor_loop(CRGBSet &leds);
void reactor_cruise(uint8_t cruise_level);
void reactor_damage();
void reactor_danger(int intensity);
