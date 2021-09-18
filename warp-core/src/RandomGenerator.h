#pragma once

#include <inttypes.h>
#include <stdarg.h>
#include "Arduino.h"

#define MAX_ENTROPY_PINS 20

/**
 * Yet another Random class! I created this helper class so I could easily get decent random numbers without having to
 * re-lookup how to properly seed the Arduino's random number generator every time, and to make it a bit more convenient
 * to grab different types of random numbers.  This class doesn't make any claims about being fast or optimized, or even
 * producting high-quality randomness. (specifically I don't do anything to address modulo bias) It is just a
 * convenience class that calls the Arduino library rand() behind the scenes.
 */
class RandomGenerator
{
private:
    uint32_t HASH_BASE = 5381;

    // I could have seeded the RNG in a `static void init()` method to make sure we are always initialized, however
    // since I instantiate a singleton of this class in the global scope, that would mean that we would always set the
    // Arduino's random seed, even if the caller didn't want to.  Handling things this way means that the caller doesn't
    // have to remember to initialize the class, but that we don't have any unexpected side effects either.
    void checkInitialization();

public:
    // Return a random uint32_t value on the range of 0 - UINT32_MAX, inclusive
    uint32_t randomUInt();

    // Return a random uint32_t value on the range of 0 - max, inclusive
    uint32_t randomUInt(uint32_t max);

    // Return a random uint32_t value on the range of min - max, inclusive
    uint32_t randomUInt(uint32_t min, uint32_t max);

    // Return a random int32_t value on the range of 0 - UINT32_MAX, inclusive
    int32_t randomInt();

    // Return a random int32_t value on the range of 0 - max, inclusive
    int32_t randomInt(int32_t max);

    // Return a random int32_t value on the range of min - max, inclusive
    int32_t randomInt(int32_t min, int32_t max);

    // Return a random float value on the range of 0 - 1.0, inclusive
    float randomFloat();

    // Return a random double value on the range of 0 - 1.0, inclusive
    double random();

    /**
     * Use this method if you want to specify your own random seed
     */
    void setRandomSeed(uint32_t seed);

    /**
     * This utility function created a sort-of entropic random number by reading the values from a collection of one or
     * more unconnected analog input pins and hashing them together.  Make sure to pass in pins that are not in use in
     * your circuit, otherwise they won't generate any entropy.  If you pass in zero (or any value larger than
     * MAX_ENTROPY_PINS) for numPins, the method will return the result for analog pins 0, 1, 2, and 3.  The pins
     * arguments must all be of type uint8_t.
     */
    uint32_t generateRandomSeed(uint8_t numPins, ...);

    /**
     * Seed the Arduino library's randomSeed() function with the results of calling generateRandomSeed(0)
     */
    void randomizeRandomSeed();

    /**
     * Given a collection of unsigned integer values, create a progressive unique hash by passing them in one at a time.
     * Start by calling initializeHash with the first integer, then call nextHash with the previous hash and each
     * subsequent integer.
     */
    uint32_t initializeHash(uint32_t nextInt) { return ((HASH_BASE << 5) + HASH_BASE) + nextInt; /* hash * 33 + nextInt */ }

    /**
     * Given a collection of unsigned integer values, create a progressive unique hash by passing them in one at a time.
     * Start by calling initializeHash with the first integer, then call nextHash with the previous hash and each
     * subsequent integer.
     */
    uint32_t nextHash(uint32_t prevHash, uint32_t nextInt) { return ((prevHash << 5) + prevHash) + nextInt; /* hash * 33 + nextInt */ }
};

extern RandomGenerator MoarRandom;
