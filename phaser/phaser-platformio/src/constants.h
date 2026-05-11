#ifndef CONSTANTS_H

#define CONSTANTS_H

const int SERIAL_BAUD_RATE = 115200;
const int BUTTON_DEBOUNCE_MILLIS = 100;

// ESP32 safe GPIO pins (Espressif) 16, 17, 18, 19, 21, 22, 23, 25, 26, 27, 32, 33
// ESP32 safe GPIO pins (Adafruit): 21, 27, 15, 14
const int CHARGING_INPUT_PIN = 14;
const int NEOPIXEL_PIN = 15;
const int TRIGGER_INPUT_PIN = 21;
const int PHASER_CONNECTED_INPUT_PIN = 27;

#endif