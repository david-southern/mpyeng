#ifndef COMMON_H

#define COMMON_H

#include <Arduino.h>
#include <NeoPixelBus.h>

#include "constants.h"
#include "logger.h"

#define ERR_MSG_SIZE 1024
#define DIAGS_SIZE 300

void SetRandomSeed();

extern char errMsg[ERR_MSG_SIZE];
extern char diagsMsg[DIAGS_SIZE];

#endif