#pragma once

#include "FastLED.h"

// Overall twinkle speed
// 0 (VERY slow) to 8 (VERY fast)
// 4, 5, and 6 are recommended
// default is 4
void setTwinkleSpeed(unsigned int newSpeed);

// Overall twinkle density
// 0 (NONE lit) to 8 (ALL lit at once)
// Default is 8
void setTwinkleDensity(unsigned int newDensity);

// Background color for 'unlit' pixels
// default is CRGB::Black
void setBackgroundcolor(CRGB newBackgroundColor);

// If auto select is set to true then for any palette 
// where the first two entries are the same, a dimmed
// version of that color will automatically be used 
// as the background color.
// default is true
void setAutoSelectBackground(bool newAutoSelect);

// If COOL_LIKE_INCANDESCENT is set to 1, colors will
// fade out slighted 'reddened', similar to how
// incandescent bulbs change color as they get dim down.
// default is false
void setCoolLikeIncandescent(bool newIncandescentCool);

// Animate the twinkles with the given palette and color set
void drawTwinkles(CRGBPalette16 twinklePalette, CRGBSet &L);