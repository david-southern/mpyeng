#include "ArduinoLog.h"

#ifndef LOW_MEMORY_LOGGING

char printStr[2];

void Logging::print(const __FlashStringHelper *format, va_list *args)
{
    PGM_P p = reinterpret_cast<PGM_P>(format);
    while (true)
    {
        unsigned char printChar = pgm_read_byte(p++);
        if (printChar == 0) {
            break;
        }

        if (printChar == '%')
        {
            printChar = pgm_read_byte(p++);
            printFormat(printChar, args);
        }
        else
        {
            printStr[0] = printChar;
            Serial.print(printStr);
        }
    }
}

void Logging::print(const char *format, va_list *args)
{
    for (; *format != 0; ++format)
    {
        if (*format == '%')
        {
            ++format;
            printFormat(*format, args);
        }
        else
        {
            Serial.print(*format);
        }
    }
}

void Logging::printFormat(const char format, va_list *args)
{
    if (format == '\0')
        return;

    if (format == '%')
    {
        Serial.print(format);
        return;
    }

    if (format == 's')
    {
        register char *s = (char *)va_arg(*args, int);
        Serial.print(s);
        return;
    }

    if (format == 'd')
    {
        Serial.print(va_arg(*args, int), DEC);
        return;
    }

    if (format == 'u')
    {
        Serial.print(va_arg(*args, unsigned int), DEC);
        return;
    }

    if (format == 'f')
    {
        Serial.print(va_arg(*args, double), 5);
        return;
    }

    if (format == 'x')
    {
        Serial.print(va_arg(*args, int), HEX);
        return;
    }

    if (format == 'X')
    {
        Serial.print("0x");
        Serial.print(va_arg(*args, int), HEX);
        return;
    }

    if (format == 'b')
    {
        Serial.print(va_arg(*args, int), BIN);
        return;
    }

    if (format == 'B')
    {
        Serial.print("0b");
        Serial.print(va_arg(*args, int), BIN);
        return;
    }

    if (format == 'l')
    {
        Serial.print(va_arg(*args, long), DEC);
        return;
    }

    if (format == 'u')
    {
        Serial.print(va_arg(*args, unsigned long), DEC);
        return;
    }

    if (format == 'c')
    {
        Serial.print((char)va_arg(*args, int));
        return;
    }

    if (format == 't')
    {
        if (va_arg(*args, int) == 1)
        {
            Serial.print("T");
        }
        else
        {
            Serial.print("F");
        }
        return;
    }

    if (format == 'T')
    {
        if (va_arg(*args, int) == 1)
        {
            Serial.print(F("true"));
        }
        else
        {
            Serial.print(F("false"));
        }
        return;
    }
}

void PrintTimestamp()
{
    long milliseconds = millis();

    long hours = milliseconds / 3600000;
    milliseconds -= hours * 3600000;
    long minutes = milliseconds / 60000;
    milliseconds -= minutes * 60000;
    long seconds = milliseconds / 1000;
    milliseconds -= seconds * 1000;

    char timeStamp[100];
    sprintf(timeStamp, "%02ld:%02ld:%02ld.%03ld - ", hours, minutes, seconds, milliseconds);
    Serial.print(timeStamp);
}

void Logging::printLevel(int level, const __FlashStringHelper *msg, va_list *args)
{
    CheckInit();

    if (level > _level)
    {
        return;
    }

    if (_prefix != NULL)
    {
        _prefix();
    }

    _timestamp();

    char levels[] = "FEWIDV";
    Serial.print(levels[level - 1]);
    Serial.print(": ");

    print(msg, args);

    if (_suffix != NULL)
    {
        _suffix();
    }

    Serial.print('\n');
}

void Logging::printLevel(int level, const char *msg, va_list *args)
{
    CheckInit();

    if (level > _level)
    {
        return;
    }

    if (_prefix != NULL)
    {
        _prefix();
    }

    _timestamp();

    char levels[] = "FEWIDV";
    Serial.print(levels[level - 1]);
    Serial.print(": ");

    print(msg, args);

    if (_suffix != NULL)
    {
        _suffix();
    }

    Serial.print('\n');
}
#endif

void Logging::CheckInit()
{
    if (!isInitialized)
    {
        isInitialized = true;
        printStr[1] = 0;

        if (!skipSerialInit)
        {
            Serial.begin(_serialBaud);
        }
#ifndef LOW_MEMORY_LOGGING
        if (_timestamp == NULL)
        {
            _timestamp = PrintTimestamp;
        }
#endif
    }
}

Logging Logger = Logging();
