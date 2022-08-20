#pragma once

void setReactorFrameRate(float framesPerSec);

void fog_setup();
void fog_update_params();
void fog_loop(CRGBSet &leds, uint32_t simTime, float secondsElapsed);

void chaser_setup();
void chaser_update_params();
void chaser_loop(CRGBSet &leds, uint32_t simTime, float secondsElapsed);

void pulse_setup();
void pulse_update_params();
void pulse_loop(CRGBSet &leds, uint32_t simTime, float secondsElapsed);

void reactor_setup();
void reactor_loop(CRGBSet &leds);
void reactor_cruise(float cruise_level);
void reactor_damage();
void reactor_danger(int intensity);
