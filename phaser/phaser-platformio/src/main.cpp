#include <Arduino.h>

#include "common.h"
#include "phaser.h"
#include "strip_test.h"

const int DIAG_FREQUENCY_MILLIS = 1000;
const int BLINK_LENGTH_MILLIS = 100;
char errMsg[ERR_MSG_SIZE];
char diagsMsg[DIAGS_SIZE];

void setup()
{
  logger_setup();

  pinMode(LED_BUILTIN, OUTPUT);

  log("Starting main");

  phaser_setup();
}

ulong nextDiag = 0;
ulong unblink = ULONG_MAX;

void loop()
{
  unsigned long simTime = millis();

  phaser_loop(simTime);

  if (simTime > nextDiag)
  {
    phaser_diags();

    int diagInterval = phaser_interesting() ? DIAG_FREQUENCY_MILLIS / 10 : DIAG_FREQUENCY_MILLIS;
    nextDiag = simTime + diagInterval;

    digitalWrite(LED_BUILTIN, HIGH);
    unblink = simTime + BLINK_LENGTH_MILLIS;
  }

  if (simTime > unblink)
  {
    digitalWrite(LED_BUILTIN, LOW);
    unblink = ULONG_MAX;
  }
}

void SetRandomSeed()
{
  uint32_t seed;

  // random works best with a seed that can use 31 bits
  // analogRead on a unconnected pin tends toward less than four bits
  seed = analogRead(0);
  delay(1);

  for (int shifts = 3; shifts < 31; shifts += 3)
  {
    seed ^= analogRead(0) << shifts;
    delay(1);
  }

  // Serial.println(seed);
  randomSeed(seed);
}