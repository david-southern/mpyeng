#pragma once

void reactor_setup();
void reactor_loop(CRGBSet &leds);
void reactor_cruise(float cruise_level);
void reactor_damage();
void reactor_danger(int intensity);
