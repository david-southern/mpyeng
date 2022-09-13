#include <Arduino.h>

#include "common.h"

const int SERIAL_ACTIVATION_WAIT_MILLIS = 3000;

bool serialActivated = true;

void uptimeHeader()
{
  if (serialActivated)
  {
    Serial.print("Uptime: ");
    Serial.print(millis());
    Serial.print(" - ");
  }
}

void log(const char *message)
{
  if (serialActivated)
  {
    uptimeHeader();
    Serial.println(message);
    Serial.flush();
  }
}

void log_error(const char *message) {
  if (serialActivated)
  {
    uptimeHeader();
    Serial.print("ERROR: ");
    Serial.println(message);
    Serial.flush();
  }
}

void logger_setup()
{
  Serial.begin(SERIAL_BAUD_RATE);

  long waitUntil = millis() + SERIAL_ACTIVATION_WAIT_MILLIS;

  while (!Serial)
  {
    // wait for serial attach
    if (millis() > waitUntil)
    {
      serialActivated = false;
      break;
    }
  }

  log("Starting logging");
}