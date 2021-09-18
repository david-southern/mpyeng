#pragma once

#include "common.h"

// Downlaoded from https://weber.itn.liu.se/~stegu/aqsis/aqsis-newnoise/simplexnoise1234.h
// SimplexNoise
// Copyright © 2003-2011, Stefan Gustavson
//
// Contact: stegu@itn.liu.se
//
// This library is public domain software, released by the author
// into the public domain in February 2011. You may do anything
// you like with it. You may even remove all attributions,
// but of course I'd appreciate it if you kept my name somewhere.
//
// This library is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
// General Public License for more details.

/** \file
		\brief Declares the SimplexNoise class for producing Perlin simplex noise.
		\author Stefan Gustavson (stegu@itn.liu.se)
*/

/*
 * This is a clean, fast, modern and free Perlin Simplex noise class in C++.
 * Being a stand-alone class with no external dependencies, it is
 * highly reusable without source code modifications.
 *
 *
 * Note:
 * Replacing the "float" type with "double" can actually make this run faster
 * on some platforms. A templatized version of SimplexNoise could be useful.
 */

class SimplexNoise
{
private:
  static unsigned char perm[];
  static float grad(int hash, float x);
  static float grad(int hash, float x, float y);
  static float grad(int hash, float x, float y, float z);
  static float grad(int hash, float x, float y, float z, float t);

public:
  SimplexNoise() {}
  ~SimplexNoise() {}

  /**
   *  Returns 1-D Simplex noise on the range [-1, 1]
   *  * Note that while the parameters of this function are float, internal calculations use int types, so parameter
   *    values that approach int limits will result in non-random noise values.
   */
  static float noise(float x);
  /**
   *  Returns 2-D Simplex noise on the range [-1, 1]
   *  * Note that while the parameters of this function are float, internal calculations use int types, so parameter
   *    values that approach int limits will result in non-random noise values.
   */
  static float noise(float x, float y);
  /**
   *  Returns 3-D Simplex noise on the range [-1, 1]
   *  * Note that while the parameters of this function are float, internal calculations use int types, so parameter
   *    values that approach int limits will result in non-random noise values.
   */
  static float noise(float x, float y, float z);
  /**
   *  Returns 4-D Simplex noise on the range [-1, 1]
   *  * Note that while the parameters of this function are float, internal calculations use int types, so parameter
   *    values that approach int limits will result in non-random noise values.
   */
  static float noise(float x, float y, float z, float w);

  /**
   *  Returns 1-D Simplex noise on the range [0, 1]
   *  * Note that while the parameters of this function are float, internal calculations use int types, so parameter
   *    values that approach int limits will result in non-random noise values.
   */
  static float noiseNormal(float x) { return (SimplexNoise::noise(x) + 1.0) * 0.5; }
  /**
   *  Returns 2-D Simplex noise on the range [0, 1]
   *  * Note that while the parameters of this function are float, internal calculations use int types, so parameter
   *    values that approach int limits will result in non-random noise values.
   */
  static float noiseNormal(float x, float y) { return (SimplexNoise::noise(x, y) + 1.0) * 0.5; }
  /**
   *  Returns 3-D Simplex noise on the range [0, 1]
   *  * Note that while the parameters of this function are float, internal calculations use int types, so parameter
   *    values that approach int limits will result in non-random noise values.
   */
  static float noiseNormal(float x, float y, float z) { return (SimplexNoise::noise(x, y, z) + 1.0) * 0.5; }
  /**
   *  Returns 41-D Simplex noise on the range [0, 1]
   *  * Note that while the parameters of this function are float, internal calculations use int types, so parameter
   *    values that approach int limits will result in non-random noise values.
   */
  static float noiseNormal(float x, float y, float z, float w) { return (SimplexNoise::noise(x, y, z, w) + 1.0) * 0.5; }
};