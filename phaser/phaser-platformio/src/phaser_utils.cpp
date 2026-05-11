#include <Arduino.h>
#include <NeoPixelBus.h>

#include "common.h"
#include "phaser.h"

RgbColor COLOR_BLACK = RgbColor(0, 0, 0);

// This helper function interpolates the chargeProgress across a range of pixCount pixels to determine the color that
// the pixel at pixIndex should be. This allows for mapping a non-equal charge range across a pixel count.
// * Parameters:
// * pixIndex: The zero-based of the pixel to return the color for.  Any pixIndex < 0 or >= pixCount will return the
//   color black.
// * pixCount: Total number of pixels to be 'charged'
// * chargeProgress: The progress of the charging on the range of 0 - 1.0.  Any value < 0 will return the uncharged
//   color, and and value > 1.0 will return the charged color.
HsbColor ChargingProgress(int pixIndex, int pixCount, double chargeProgress, HsbColor chargedColor, HsbColor unchargedColor)
{
  if (pixIndex < 0 || pixIndex >= pixCount)
  {
    return COLOR_BLACK;
  }

  if (chargeProgress < 0)
  {
    return unchargedColor;
  }

  if (chargeProgress >= 1)
  {
    return chargedColor;
  }

  HsbColor returnColor;

  double pixelProgress = chargeProgress * pixCount;
  double progressIndex = (int)pixelProgress;

  if (pixIndex < progressIndex)
  {
    return chargedColor;
  }

  if (pixIndex > pixelProgress)
  {
    return unchargedColor;
  }

  pixelProgress -= progressIndex;

  HsbColor retval = HsbColor::LinearBlend<NeoHueBlendShortestDistance>(unchargedColor, chargedColor, pixelProgress);

  return retval;
}

void SetPixel(PixelType pixType, int pixIndex, RgbColor pixColor)
{
  if (pixIndex < 0)
  {
    snprintf(errMsg, ERR_MSG_SIZE, "SetPixel: Invalid pixIndex < 0: %d", pixIndex);
    log_error(errMsg);
    return;
  }

  int strip_index = 0;
  switch (pixType)
  {
  case PixelType_PowerPack:
    if (pixIndex >= POWER_PACK_PIXEL_COUNT)
    {
      snprintf(errMsg, ERR_MSG_SIZE, "SetPixel: Invalid pixIndex > POWER_PACK_PIXEL_COUNT(%d): %d", POWER_PACK_PIXEL_COUNT, pixIndex);
      log_error(errMsg);
      return;
    }
    strip_index = POWER_PACK_PIXEL_OFFSET + pixIndex;
    break;

  case PixelType_Barrel:
    if (pixIndex >= PHASER_BARREL_PIXEL_COUNT)
    {
      snprintf(errMsg, ERR_MSG_SIZE, "SetPixel: Invalid pixIndex > PHASER_BARREL_PIXEL_COUNT(%d): %d", PHASER_BARREL_PIXEL_COUNT, pixIndex);
      log_error(errMsg);
      return;
    }
    strip_index = PHASER_BARREL_PIXEL_OFFSET + pixIndex;
    // snprintf(diagsMsg, DIAGS_SIZE, "Set Barrel %d(%d) to: (%d, %d, %d)", pixIndex, strip_index, pixColor.R, pixColor.G, pixColor.B);
    // log(diagsMsg);
    break;

  case PixelType_Reticle:
    if (pixIndex >= PHASER_RETICLE_PIXEL_COUNT)
    {
      snprintf(errMsg, ERR_MSG_SIZE, "SetPixel: Invalid pixIndex > PHASER_RETICLE_PIXEL_COUNT(%d): %d", PHASER_RETICLE_PIXEL_COUNT, pixIndex);
      log_error(errMsg);
      return;
    }
    strip_index = PHASER_RETICLE_PIXEL_OFFSET + pixIndex;
    // snprintf(diagsMsg, DIAGS_SIZE, "Set Reticle %d(%d) to: (%d, %d, %d)", pixIndex, strip_index, pixColor.R, pixColor.G, pixColor.B);
    // log(diagsMsg);
    break;

  default:
    snprintf(errMsg, ERR_MSG_SIZE, "SetPixel: Unknown PixelType: %d", pixType);
    log_error(errMsg);
    return;
  }

  phaser_strip.SetPixelColor(strip_index, phaser_colorGamma.Correct(pixColor));
}

#ifdef STRIP_TEST
int blinkMode = 0;

void phaser_strip_test()
{
  if (blinkMode)
  {
    RgbColor red(colorSaturation, 0, 0);
    RgbColor green(0, colorSaturation, 0);
    RgbColor blue(0, 0, colorSaturation);
    RgbColor white(colorSaturation);

    phaser_strip.SetPixelColor(0, phaser_colorGamma.Correct(red));
    phaser_strip.SetPixelColor(1, phaser_colorGamma.Correct(green));
    phaser_strip.SetPixelColor(2, phaser_colorGamma.Correct(blue));
    phaser_strip.SetPixelColor(3, phaser_colorGamma.Correct(white));
  }
  else
  {
    RgbColor black(0);

    phaser_strip.SetPixelColor(0, black);
    phaser_strip.SetPixelColor(1, black);
    phaser_strip.SetPixelColor(2, black);
    phaser_strip.SetPixelColor(3, black);
  }

  blinkMode = !blinkMode;

  phaser_strip.Show();
  return;
}
#endif