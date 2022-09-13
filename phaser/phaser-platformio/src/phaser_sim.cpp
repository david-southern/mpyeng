#include "common.h"
#include "phaser.h"

// Range from 0 (no LED light at all) to 1 (full LED brightness)
const double NEOPIXEL_BRIGHTNESS = 0.5;
const int colorSaturation = 255 * NEOPIXEL_BRIGHTNESS;

// These constants control the PhaserSim settings

// How many charges can the power pack hold?  This simulation assumes a single LED pixel per charge, so you can't have
// more charges than the POWER_PACK_PIXEL_COUNT.
const double MAX_CHARGE = POWER_PACK_PIXEL_COUNT;

// How many milliseconds does it take to charge an empty pack to MAX_CHARGE
const double MILLIS_PER_FULL_CHARGE = 15000;

// How many milliseconds does it take the phaser to connect
const double MILLIS_PER_FULL_CONNECT = 3000;

// How many milliseconds does a 'firing' animation take
const double FIRING_MILLIS = 300;

// Setting ALLOW_PARTIAL_CHARGES to true simulates the ability for the power pack to carry a 'partial charge' - if the
// pack is removed from the charging station while it has 3.4 shots charged, the extra 0.4 can't be used for another
// shot, but when the pack is placed on the charging station again, it will start charging from 0.4 rather than starting
// over from 3.0.  If the per-shot charging time is long, this could make a difference.
//
// If set to false, we will simulate an 'all-or-nothing' charging approach, where any non-integral charge is lost when
// the pack is removed from the charging station.
const bool ALLOW_PARTIAL_CHARGES = false;

const HsbColor HSB_BLACK = HsbColor(RgbColor(0, 0, 0));

const HsbColor PHASER_CHARGED_COLOR = HsbColor(RgbColor(0, colorSaturation, 0));   // GREEN = charged
const HsbColor PHASER_UNCHARGED_COLOR = HsbColor(RgbColor(colorSaturation, 0, 0)); // RED = uncharged

const HsbColor PHASER_BARREL_CONNECTED = HsbColor(RgbColor(colorSaturation, colorSaturation, 0));  // YELLOW = Connected to power, not ready to fire
const HsbColor PHASER_BARREL_READY = HsbColor(RgbColor(0, colorSaturation, 0));      // GREEN = Ready to fire
const HsbColor PHASER_BARREL_FIRING = HsbColor(RgbColor(colorSaturation, 0, 0));     // RED = firing

// Number of millis per individual charge
const double MILLIS_PER_CHARGE = MILLIS_PER_FULL_CHARGE / MAX_CHARGE;

// These variables control the PhaserSim state
int chargeButtonState = 0;
double powerPackCharge = 0;
int chargingStartMillis = 0;

const double MILLIS_PER_CONNECTION = MILLIS_PER_FULL_CONNECT / PHASER_BARREL_PIXEL_COUNT;
double connectionCharge = 0;
int connectingStartMillis = 0;

int connectedButtonState = 0;
int connectedDebounce = 0;
int connectedState = 0;
bool readyToFire = false;

int triggerButtonState = 0;
int triggerDebounce = 0;
int triggerState = 0;

int shotsFired = 0;
int clicksFired = 0;
int fireAnimationEnd = 0;
double fireAnimationProgress = 0;

const int DIAG_INTERVAL = 1000;
int PIXEL_REFRESH_MILLIS = 20;
int nextPixelUpdate = 0;

NeoGamma<NeoGammaTableMethod> phaser_colorGamma; // for any fade animations, best to correct gamma
NeoPixelBus<NeoGrbFeature, Neo800KbpsMethod> phaser_strip(TOTAL_PIXELS, NEOPIXEL_PIN);

void set_pixel_refresh_millis(int refresh_millis)
{
  PIXEL_REFRESH_MILLIS = refresh_millis;
}

int prevPackPixels[TOTAL_PIXELS];
int prevBarrelPixels[TOTAL_PIXELS];
int prevReticlePixels[TOTAL_PIXELS];

void phaser_setup()
{
  SetRandomSeed();

  pinMode(CHARGING_INPUT_PIN, INPUT_PULLDOWN);
  pinMode(TRIGGER_INPUT_PIN, INPUT_PULLDOWN);
  pinMode(PHASER_CONNECTED_INPUT_PIN, INPUT_PULLDOWN);

  for (int index = 0; index < TOTAL_PIXELS; index++)
  {
    prevPackPixels[index] = 0;
    prevBarrelPixels[index] = 0;
    prevReticlePixels[index] = 0;
  }

  phaser_strip.Begin();
  phaser_strip.Show();

  log("Starting PhaserSim");
}

char stripDiag[DIAGS_SIZE];

void update_pixels()
{
  strcpy(stripDiag, "");

  bool stripChanged = false;

  // Update the power pack pixels
  for (int index = 0; index < POWER_PACK_PIXEL_COUNT; index++)
  {

    HsbColor pixelColorHSB = ChargingProgress(index, POWER_PACK_PIXEL_COUNT,
                                              powerPackCharge / MAX_CHARGE, PHASER_CHARGED_COLOR, PHASER_UNCHARGED_COLOR);
    RgbColor pixelColorRGB = RgbColor(pixelColorHSB);

    int thisPixel = pixelColorRGB.R << 16 | pixelColorRGB.G << 8 | pixelColorRGB.B;

    if (prevPackPixels[index] != thisPixel)
    {
      stripChanged = true;
      prevPackPixels[index] = thisPixel;
      SetPixel(PixelType_PowerPack, index, phaser_colorGamma.Correct(pixelColorRGB));
    }
  }

  // Update the phaser barrel pixels
  for (int index = 0; index < PHASER_BARREL_PIXEL_COUNT; index++)
  {
    HsbColor pixelColorHSB = HSB_BLACK;

    if(connectionCharge > 0) {
      pixelColorHSB = ChargingProgress(index, PHASER_BARREL_PIXEL_COUNT,
      connectionCharge / PHASER_BARREL_PIXEL_COUNT, PHASER_BARREL_READY, PHASER_BARREL_CONNECTED);
    }

    RgbColor pixelColorRGB = RgbColor(pixelColorHSB);

    int thisPixel = pixelColorRGB.R << 16 | pixelColorRGB.G << 8 | pixelColorRGB.B;

    if (prevBarrelPixels[index] != thisPixel)
    {
      stripChanged = true;
      prevBarrelPixels[index] = thisPixel;
      SetPixel(PixelType_Barrel, index, phaser_colorGamma.Correct(pixelColorRGB));
    }
  }

  // Update the phaser reticle pixels
  for (int index = 0; index < PHASER_RETICLE_PIXEL_COUNT; index++)
  {
    HsbColor pixelColorHSB = HSB_BLACK;

    if(connectionCharge > 0) {
      pixelColorHSB = readyToFire ? PHASER_BARREL_READY : PHASER_BARREL_CONNECTED;
    }

    if(fireAnimationProgress > 0) {
      pixelColorHSB = PHASER_BARREL_FIRING;
    }

    RgbColor pixelColorRGB = RgbColor(pixelColorHSB);

    int thisPixel = pixelColorRGB.R << 16 | pixelColorRGB.G << 8 | pixelColorRGB.B;

    if (prevReticlePixels[index] != thisPixel)
    {
      stripChanged = true;
      prevReticlePixels[index] = thisPixel;
      SetPixel(PixelType_Reticle, index, phaser_colorGamma.Correct(pixelColorRGB));
    }
  }

  if (stripChanged)
  {
    phaser_strip.Show();
  }
}

void handle_pixels(unsigned long simTime)
{
  if (simTime > nextPixelUpdate)
  {
    update_pixels();
    nextPixelUpdate = simTime + PIXEL_REFRESH_MILLIS;
  }
}

void handle_connection(unsigned long simTime)
{
  connectedButtonState = digitalRead(PHASER_CONNECTED_INPUT_PIN);

  // Phaser is connected
  if (connectedButtonState == 1)
  {
    // Current connect state is unconnected
    if (connectedState == 0)
    {
      // We aren't in the debounce period of a connection, start a new debounce period
      if (connectedDebounce == 0)
      {
        // Wait BUTTON_DEBOUNCE_MILLIS
        connectedDebounce = simTime + BUTTON_DEBOUNCE_MILLIS;
      }

      // If the connection hasn't 'disconnected' during the debounce period, then it's a good connection
      if (simTime > connectedDebounce)
      {
        connectedState = 1;
      }
    }
  }
  else
  {
    connectedDebounce = 0;
    connectedState = 0;
  }

  if (connectedState)
  {
    if (connectingStartMillis == 0)
    {
      connectingStartMillis = simTime;
    }

    double connectingProgress = (simTime - connectingStartMillis) / (MILLIS_PER_CONNECTION);
    connectionCharge += connectingProgress;
    connectingStartMillis = simTime;
    connectionCharge = min(connectionCharge, (double)PHASER_BARREL_PIXEL_COUNT);
  }
  else
  {
    connectionCharge = 0;
    connectingStartMillis = 0;
  }

  readyToFire = connectionCharge >= PHASER_BARREL_PIXEL_COUNT;
}

void handle_trigger(unsigned long simTime)
{
  if(fireAnimationEnd > simTime) {
    fireAnimationProgress = (double)(fireAnimationEnd - simTime) / FIRING_MILLIS;
  } else {
    fireAnimationProgress = 0;
  }

  if (!readyToFire)
  {
    return;
  }

  triggerButtonState = digitalRead(TRIGGER_INPUT_PIN);

  // Trigger is pressed
  if (triggerButtonState == 1)
  {
    // Current trigger state is unpressed
    if (triggerState == 0)
    {
      // We aren't in the debounce period of a trigger press, start a new debounce period
      if (triggerDebounce == 0)
      {
        // Wait BUTTON_DEBOUNCE_MILLIS
        triggerDebounce = simTime + BUTTON_DEBOUNCE_MILLIS;
      }

      // If the trigger hasn't 'unpressed' during the debounce period, then it's a good press
      if (simTime > triggerDebounce)
      {
        triggerState = 1;
        if (powerPackCharge > 0)
        {
          fireAnimationEnd = simTime + FIRING_MILLIS;
          Serial.println("Pew! Pew!");
          powerPackCharge--;
          shotsFired++;
        }
        else
        {
          Serial.println("Click, click...");
          clicksFired++;
        }
      }
    }
  }
  else
  {
    triggerDebounce = 0;
    triggerState = 0;
  }
}

void handle_charging(unsigned long simTime)
{
  chargeButtonState = digitalRead(CHARGING_INPUT_PIN);

  if (chargeButtonState)
  {
    // We'll re-calculate the charging progress every cycle, that way we don't need to worry about de-bouncing the
    // charging signal.  If the signal bounces, we'll just re-start the charing animation, which is what we want anyway.
    if (chargingStartMillis == 0)
    {
      chargingStartMillis = simTime;
    }

    // Increment the charge by the charge progress and then reset the start time every time through the cycle.  This
    // protecte us in case our phaser_loop function isn't called regularly
    double chargeProgress = (simTime - chargingStartMillis) / (MILLIS_PER_CHARGE);
    powerPackCharge += chargeProgress;
    chargingStartMillis = simTime;
    powerPackCharge = min(powerPackCharge, MAX_CHARGE);
  }
  else
  {
    if (chargingStartMillis && !ALLOW_PARTIAL_CHARGES)
    {
      // If we were charging and now are not, and if we don't allow partial charges then truncate the charge now
      powerPackCharge = (int)powerPackCharge;
    }
    chargingStartMillis = 0;
  }
}

void phaser_loop(unsigned long simTime)
{
  handle_connection(simTime);
  handle_trigger(simTime);
  handle_connection(simTime);
  handle_charging(simTime);
  handle_pixels(simTime);
}

void phaser_diags()
{
  // Adafruit Feather Huzzah32 ties A13 to the batery voltage
  int sensorValue = analogRead(A13);
  // A13 sensor is tied to a voltage divider, so scale it to show voltage correctly.
  double battVoltage = (sensorValue * 2.0) / 1000.0;

  snprintf(diagsMsg, DIAGS_SIZE,
           "Batt: %.3f, ChargeButton: %d, Connected: %.3f, TriggerButton: %d, ChargeLevel: %.3f/%d, strip: %s",
           battVoltage, chargeButtonState, connectionCharge, triggerButtonState,
           powerPackCharge, (int)MAX_CHARGE,
           stripDiag);
  log(diagsMsg);
}

int phaser_interesting()
{
  return false;
  return chargeButtonState || triggerButtonState;
}
