#ifndef PHASER_H

#define PHASER_H

#include "common.h"

const int POWER_PACK_PIXEL_OFFSET = 0;
const int POWER_PACK_PIXEL_COUNT = 10;

const int PHASER_BARREL_PIXEL_OFFSET = 10;
const int PHASER_BARREL_PIXEL_COUNT = 20;

const int PHASER_RETICLE_PIXEL_OFFSET = 30;
const int PHASER_RETICLE_PIXEL_COUNT = 3;

const int TOTAL_PIXELS = POWER_PACK_PIXEL_COUNT + PHASER_BARREL_PIXEL_COUNT + PHASER_RETICLE_PIXEL_COUNT;

enum PixelType
{
    PixelType_Unknown,
    PixelType_PowerPack,
    PixelType_Barrel,
    PixelType_Reticle
};

extern NeoGamma<NeoGammaTableMethod> phaser_colorGamma;
extern NeoPixelBus<NeoGrbFeature, Neo800KbpsMethod> phaser_strip;

extern RgbColor COLOR_BLACK;

extern const HsbColor PHASER_CHARGED_COLOR;
extern const HsbColor PHASER_UNCHARGED_COLOR;

extern const HsbColor PHASER_BARREL_NEUTRAL;
extern const HsbColor PHASER_BARREL_FIRING;

void phaser_setup();
void phaser_loop(unsigned long simTime);
void set_pixel_refresh_millis(int refresh_millis);
void phaser_diags();
int phaser_interesting();

void SetPixel(PixelType pixType, int pixIndex, RgbColor pixColor);
HsbColor ChargingProgress(int pixIndex, int pixCount, double chargeProgress, HsbColor chargedColor, HsbColor unchargedColor);

#endif