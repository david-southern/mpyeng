#include "common.h"

#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SH110X.h>
#include <MFRC522.h>

Adafruit_SH1107 display = Adafruit_SH1107(64, 128, &Wire);
uint16_t TEXT_WIDTH_PIXELS, TEXT_HEIGHT_PIXELS;

#if defined(ESP32) && !defined(ARDUINO_ADAFRUIT_FEATHER_ESP32S2)
#define BUTTON_A 15
#define BUTTON_B 32
#define BUTTON_C 14
#else // 32u4, M0, M4, nrf52840, esp32-s2 and 328p
#define BUTTON_A 9
#define BUTTON_B 6
#define BUTTON_C 5
#endif

#define RFID_RESET_PIN 21
#define RFID_CS_PIN 12

MFRC522 mfrc522(RFID_CS_PIN, RFID_RESET_PIN); // Create MFRC522 instance

const int BUTTON_DEBOUNCE_MILLIS = 20;

Bounce2::Button buttonA = Bounce2::Button();
Bounce2::Button buttonB = Bounce2::Button();
Bounce2::Button buttonC = Bounce2::Button();

void setTextCursor(int x, int y)
{
  display.setCursor(x * TEXT_WIDTH_PIXELS, y * TEXT_HEIGHT_PIXELS);
}

void setup()
{
  pinMode(LED_BUILTIN, OUTPUT);

  buttonA.attach(BUTTON_A, INPUT_PULLUP);
  buttonA.interval(BUTTON_DEBOUNCE_MILLIS);
  buttonA.setPressedState(LOW);

  buttonB.attach(BUTTON_B, INPUT_PULLUP);
  buttonB.interval(BUTTON_DEBOUNCE_MILLIS);
  buttonB.setPressedState(LOW);

  buttonC.attach(BUTTON_C, INPUT_PULLUP);
  buttonC.interval(BUTTON_DEBOUNCE_MILLIS);
  buttonC.setPressedState(LOW);

  unsigned int serialWaitExpire = millis() + 1500;

  Logger.InitializeSerial();

  while (!Serial && millis() < serialWaitExpire)
  {
    ; // wait for serial port to connect. Needed for native USB
  }

  Logger.SetLogLevel(LOG_LEVEL_INFO);

  Logger.Info(F("RFID-test starting up"));

  display.begin(0x3C, true); // Address 0x3C default
  display.setRotation(1);
  display.setTextSize(1);
  display.setTextColor(SH110X_WHITE, SH110X_BLACK);
  int16_t x1, y1;
  display.getTextBounds("M", 0, 0, &x1, &y1, &TEXT_WIDTH_PIXELS, &TEXT_HEIGHT_PIXELS);

  display.clearDisplay();
  display.setCursor(0, 0);
  display.print("  Btn status:");
  display.display();

  Logger.Info(F("Starting SPI"));
  SPI.begin(); // Init SPI bus

  Logger.Info(F("Init RFID"));
  mfrc522.PCD_Init(); // Init MFRC522

  delay(500);         // Optional delay. Some board do need more time after init to be ready, see Readme

  Logger.Info(F("Initial RFID Gain: %d"), mfrc522.PCD_GetAntennaGain());

  mfrc522.PCD_SetAntennaGain(0x07 << 4);

  Logger.Info(F("Raised RFID Gain: %d"), mfrc522.PCD_GetAntennaGain());

  Logger.Info(F("Scan RFID card..."));
}

unsigned int led_blink = 0;
unsigned int text_blink = 1;
unsigned int do_blink = led_blink || text_blink;
unsigned int BLINK_DURATION = 2000;
int blinkMode = 1;
unsigned int nextBlinkTime = 0;
unsigned int prevBlinkTime = 0;
int frameCount = 0;

float cruise_level = 0;
float button_cruise_step = 0.1;

void handleButton(Bounce2::Button &whichButton, int xCoord, const char *btnName)
{
  whichButton.update();

  if (whichButton.pressed())
  {
    setTextCursor(xCoord + 14, 0);
    display.println(btnName);
    display.display();
  }
  if (whichButton.released())
  {
    setTextCursor(xCoord + 14, 0);
    display.println(" ");
    display.display();
  }
}

bool isCardPresent()
{
  byte bufferATQA[2];
  byte bufferSize = sizeof(bufferATQA);

  // Reset baud rates
  mfrc522.PCD_WriteRegister(MFRC522::PCD_Register::TxModeReg, 0x00);
  mfrc522.PCD_WriteRegister(MFRC522::PCD_Register::RxModeReg, 0x00);
  // Reset ModWidthReg
  mfrc522.PCD_WriteRegister(MFRC522::PCD_Register::ModWidthReg, 0x26);

  MFRC522::StatusCode result = mfrc522.PICC_WakeupA(bufferATQA, &bufferSize);
  return (result == MFRC522::STATUS_OK || result == MFRC522::STATUS_COLLISION);
}

uint32_t getRFID_UID()
{
  if (!isCardPresent())
  {
    return 0;
  }

  uint32_t tagID = 0;

  if (mfrc522.PICC_ReadCardSerial())
  {
    for (uint8_t i = 0; i < 4; i++)
    {
      // The MIFARE PICCs that we use have 4 byte UID
      tagID <<= 8;
      tagID |= mfrc522.uid.uidByte[i];
    }

    mfrc522.PICC_HaltA();
  }

  return tagID;
}

uint32_t prevRFID = 0;

void loop()
{
  unsigned int simTime = millis();

  frameCount++;

  if (do_blink && simTime > nextBlinkTime)
  {
    nextBlinkTime = simTime + BLINK_DURATION;
    if (text_blink)
    {
      setTextCursor(0, 0);

      if (blinkMode)
      {
        display.println("*");
      }
      else
      {
        display.println(" ");
      }

      setTextCursor(0, 1);
      display.print("Frames: ");
      display.print(frameCount);
      display.print("   ");
      display.display();

      frameCount = 0;
    }

    if (led_blink)
    {
      digitalWrite(LED_BUILTIN, blinkMode);
    }
    blinkMode = !blinkMode;
  }

  handleButton(buttonA, 0, "A");
  handleButton(buttonB, 1, "B");
  handleButton(buttonC, 2, "C");

  uint32_t rfid = getRFID_UID();

  if (rfid != prevRFID)
  {
    Logger.Info(F("Saw RFID: %d"), rfid);

    setTextCursor(0, 2);
    display.print("RFID: ");

    if (rfid > 0)
    {
      display.print(rfid, HEX);
    }
    else
    {
      display.print("<none>   ");
    }

    display.display();

    prevRFID = rfid;
  }
}
