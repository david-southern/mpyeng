#include "common.h"

bool isInitialized = false;

void RandomGenerator::checkInitialization()
{
    if (!isInitialized)
    {
        Logger.Info(F("MoarRandom.checkInit: called"));
        randomizeRandomSeed();
    }
}

void RandomGenerator::setRandomSeed(uint32_t seed)
{
    Logger.Info(F("MoarRandom.setRandomSeed: called"));
    isInitialized = true;
    randomSeed(seed);
}

void RandomGenerator::randomizeRandomSeed()
{
    setRandomSeed(generateRandomSeed(0));
}

uint32_t RandomGenerator::generateRandomSeed(uint8_t numPins, ...)
{
    Logger.Info(F("MoarRandom.genRand: numPins: %u"), numPins);
    // Lots of Arduino code suggests analogRead() from an unconnected analog pin as a way to generate entropy.  In
    // practice, though, on my Arduino Due, I see the analogRead of a pin clustering within about 10 integers of the
    // same value, over multiple resets.  Different pins appear to cluster around different values, but even then they
    // are close to each other. (i.e. all within the 700-900 range)  Given this, try to get a little bit of entropy by
    // reading four different pins, and hashing the results together.
    if (numPins < 1 || numPins > MAX_ENTROPY_PINS)
    {
        Logger.Info(F("MoarRandom.genRand: calling default init"));
        return generateRandomSeed(4, 0, 1, 2, 3);
    }

    // Even with hashing four pins together, I am still getting very similar seeds, since all the starting numbers are
    // small integers, I am getting lots of initial seed values around the 1900000000 to 2100000000 ranges.  There is
    // more variation in the lower bits, so let's do this whole thing multiple times with a bit of a delay, and use the
    // lower few bits of each result to make a hopefully moar random seed value.
    const uint8_t hashTimes = 4;
    const uint32_t retryDelayMS = 5;
    const uint32_t hashBitmask = 0xFF;
    const uint32_t hashShiftBits = 8;

    uint32_t randomSeed = 0;

    for (uint8_t hashIndex = 0; hashIndex < hashTimes; hashIndex++)
    {
        delay(retryDelayMS);

        uint32_t thisHash = 0;

        va_list args;
        va_start(args, numPins);

        for (uint8_t pinIndex = 0; pinIndex < numPins; pinIndex++)
        {
            // The type parameter on this va_arg call should really be uint8_t, but when I use that, I get a compiler
            // warning indicating that uint8_t is promoted to int when passed throug ... args.  So use int and constrain it
            // to uint8_t. The method is documented as requiring uint8_t, so the caller should already know this.
            uint8_t nextPin = (uint8_t)(va_arg(args, int) & 0xFF);
            uint32_t pinValue = analogRead(nextPin);

            if (pinIndex == 0)
            {
                thisHash = initializeHash(pinValue);
            }
            else
            {
                thisHash = nextHash(thisHash, pinValue);
            }
        }
        va_end(args);

        uint32_t maskedHash = (thisHash & hashBitmask);
        uint32_t shiftSeed = randomSeed << hashShiftBits;
        randomSeed = shiftSeed | maskedHash;
    }

    Logger.Info(F("Seeding MoarRandom with: %u"), randomSeed);

    return randomSeed;
}

uint32_t RandomGenerator::randomUInt()
{
    checkInitialization();
    return (uint32_t)rand();
}

uint32_t RandomGenerator::randomUInt(uint32_t max)
{
    checkInitialization();
    if (max == 0)
    {
        return 0;
    }

    return (uint32_t)(rand() % max);
}

uint32_t RandomGenerator::randomUInt(uint32_t min, uint32_t max)
{
    checkInitialization();
    if (max == min)
    {
        return 0;
    }

    if (max < min)
    {
        uint32_t t = max;
        max = min;
        min = t;
    }
    return min + (uint32_t)(rand() % (max - min));
}

int32_t RandomGenerator::randomInt()
{
    checkInitialization();
    return (int32_t)rand();
}

int32_t RandomGenerator::randomInt(int32_t max)
{
    checkInitialization();
    if (max <= 0)
    {
        return 0;
    }

    return (uint32_t)(rand() % max);
}

int32_t RandomGenerator::randomInt(int32_t min, int32_t max)
{
    checkInitialization();
    if (max == min)
    {
        return 0;
    }

    if (max < min)
    {
        uint32_t t = max;
        max = min;
        min = t;
    }
    return min + (uint32_t)(rand() % (max - min));
}

float RandomGenerator::randomFloat()
{
    checkInitialization();
    return (float)rand() / (float)RAND_MAX;
}

double RandomGenerator::random()
{
    checkInitialization();
    return (double)rand() / (double)RAND_MAX;
}

RandomGenerator MoarRandom = RandomGenerator();
