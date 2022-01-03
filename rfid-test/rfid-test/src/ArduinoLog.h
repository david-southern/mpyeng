#pragma once

#include "common.h"

// #define LOW_MEMORY_LOGGING

typedef void (*printfunction)();

#define LOG_LEVEL_SILENT 0
#define LOG_LEVEL_FATAL 1
#define LOG_LEVEL_ERROR 2
#define LOG_LEVEL_WARNING 3
#define LOG_LEVEL_INFO 4
#define LOG_LEVEL_DEBUG 5
#define LOG_LEVEL_VERBOSE 6

/*!
 Output format string can contain below wildcards. Every wildcard
 must be start with percent sign (\%)

**** Wildcards

* %s	replace with an string (char*)
* %c	replace with an character
* %d	replace with an integer value
* %l	replace with an long value
* %x	replace and convert integer value into hex
* %X	like %x but combine with 0x123AB
* %b	replace and convert integer value into binary
* %B	like %x but combine with 0b10100011
* %t	replace and convert boolean value into "t" or "f"
* %T	like %t but convert into "true" or "false"

**** Loglevels

* 0 - LOG_LEVEL_SILENT     no output
* 1 - LOG_LEVEL_FATAL      fatal errors
* 2 - LOG_LEVEL_ERROR      all errors
* 3 - LOG_LEVEL_WARNING    errors and warnings
* 4 - LOG_LEVEL_INFO       errors, warnings and infos
* 5 - LOG_LEVEL_DEBUG      errors, warnings, infos, debugs
* 6 - LOG_LEVEL_VERBOSE    all
*/

class Logging
{
private:
  int _level = LOG_LEVEL_INFO;

  bool isInitialized = false;
  bool skipSerialInit = false;
  unsigned long _serialBaud = 115200;

  printfunction _prefix = NULL;
  printfunction _suffix = NULL;
  printfunction _timestamp = NULL;

  void CheckInit();

#ifndef LOW_MEMORY_LOGGING
  void printFormat(const char format, va_list *args);

  void print(const char *format, va_list *args);
  void printLevel(int level, const char *msg, va_list *args);

  void print(const __FlashStringHelper *format, va_list *args);
  void printLevel(int level, const __FlashStringHelper *msg, va_list *args);
#endif

public:
  Logging() {}

  void InitializeSerial() { CheckInit(); }

  /**
	 * Sets a function to be called before each log command.
	 */
  void SetPrefix(printfunction prefixFunction) { _prefix = prefixFunction; }

  /**
	 * Set a function to print the timestamp to the log
	 */
  void SetTimestamp(printfunction timestampFunction) { _timestamp = timestampFunction; }

  /**
	 * Sets a function to be called after each log command.
	 */
  void SetSuffix(printfunction suffixFunction) { _suffix = suffixFunction; }

  /**
	 * Skip automatic initialization of the Serial port
	 */
  void SkipSerialInitialization() { skipSerialInit = true; }

  void SetLogLevel(int newLevel) { _level = constrain(newLevel, LOG_LEVEL_SILENT, LOG_LEVEL_VERBOSE); }

  void SetSerialBaud(int newBaud) { _serialBaud = newBaud; }

#ifndef LOW_MEMORY_LOGGING
#define LOG_HELPER(LEVEL)        \
  va_list args;                  \
  va_start(args, msg);           \
  printLevel(LEVEL, msg, &args); \
  va_end(args);
#else
#define LOG_HELPER(LEVEL) ;
#endif

  void Fatal(const char *msg, ...) { LOG_HELPER(LOG_LEVEL_FATAL) }
  void Error(const char *msg, ...) { LOG_HELPER(LOG_LEVEL_ERROR) }
  void Warning(const char *msg, ...) { LOG_HELPER(LOG_LEVEL_WARNING) }
  void Info(const char *msg, ...) { LOG_HELPER(LOG_LEVEL_INFO) }
  void Debug(const char *msg, ...) { LOG_HELPER(LOG_LEVEL_DEBUG) }
  void Verbose(const char *msg, ...) { LOG_HELPER(LOG_LEVEL_VERBOSE) }

  void Fatal(const __FlashStringHelper *msg, ...) { LOG_HELPER(LOG_LEVEL_FATAL) }
  void Error(const __FlashStringHelper *msg, ...) { LOG_HELPER(LOG_LEVEL_ERROR) }
  void Warning(const __FlashStringHelper *msg, ...) { LOG_HELPER(LOG_LEVEL_WARNING) }
  void Info(const __FlashStringHelper *msg, ...) { LOG_HELPER(LOG_LEVEL_INFO) }
  void Debug(const __FlashStringHelper *msg, ...) { LOG_HELPER(LOG_LEVEL_DEBUG) }
  void Verbose(const __FlashStringHelper *msg, ...) { LOG_HELPER(LOG_LEVEL_VERBOSE) }
};

extern Logging Logger;
