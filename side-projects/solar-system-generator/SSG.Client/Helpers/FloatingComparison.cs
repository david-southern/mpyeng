namespace SSG.Helpers;

public static partial class Utils
{
    // From the .Net Single docs: https://learn.microsoft.com/en-us/dotnet/api/system.single?view=net-6.0
    // Single.Epsilon is sometimes used as an absolute measure of the distance between two Single values when
    // testing for equality. However, Single.Epsilon measures the smallest possible value that can be added to, or
    // subtracted from, a Single whose value is zero. For most positive and negative Single values, the value of
    // Single.Epsilon is too small to be detected. Therefore, except for values that are zero, we do not recommend
    // its use in tests for equality.
    // For reference: Single.Epsilon = 1.401298E-45
    public const float FloatingPointEqualityEpsilon = float.Epsilon * 100;

    /// <summary>
    /// Tests if value1 and value2 are exactly the same float value, or if either is Infinite or Nan, then if they are
    /// both the same Infinite or Nan value.
    /// </summary>
    /// <param name="value1"></param>
    /// <param name="value2"></param>
    /// <returns></returns>
    private static bool SimpleFloatEQ(float value1, float value2)
    {
        if (value1.Equals(value2))
        {
            return true;
        }

        if (float.IsInfinity(value1) || float.IsNaN(value1)
            || float.IsInfinity(value2) || float.IsNaN(value2))
        {
            return value1.Equals(value2);
        }

        return false;
    }

    /// <summary>
    /// Return an appropriate divisor for the FloatXX methods.  The divisor will always be positive.
    /// </summary>
    /// <param name="value1"></param>
    /// <param name="value2"></param>
    /// <returns></returns>
    public static float FloatEQDivisor(float value1, float value2)
    {
        // Handle zero to avoid division by zero
        float divisor = Math.Max(value1, value2);
        if (divisor.Equals(0))
        {
            divisor = Math.Min(value1, value2);
        }

        return divisor < 0 ? -divisor : divisor;
    }

    public static bool FloatEQ(float value1, float value2, float epsilon = FloatingPointEqualityEpsilon)
    {
        if(SimpleFloatEQ(value1, value2))
        {
            return true;
        }

        float divisor = FloatEQDivisor(value1, value2);

        return Math.Abs(value1 - value2) / divisor <= epsilon;
    }

    public static bool FloatNE(float value1, float value2, float epsilon = FloatingPointEqualityEpsilon)
        => !FloatEQ(value1, value2, epsilon);

    public static bool FloatLT(float value1, float value2, float epsilon = FloatingPointEqualityEpsilon)
    {
        if (SimpleFloatEQ(value1, value2))
        {
            return false;
        }

        float divisor = FloatEQDivisor(value1, value2);

        return (value1 - value2) / divisor < -epsilon;
    }

    public static bool FloatGT(float value1, float value2, float epsilon = FloatingPointEqualityEpsilon)
    {
        if (SimpleFloatEQ(value1, value2))
        {
            return false;
        }

        float divisor = FloatEQDivisor(value1, value2);

        return (value1 - value2) / divisor > epsilon;
    }


    public static bool FloatLE(float value1, float value2, float epsilon = FloatingPointEqualityEpsilon)
        => SimpleFloatEQ(value1, value2) || FloatLT(value1, value2, -epsilon);

    public static bool FloatGE(float value1, float value2, float epsilon = FloatingPointEqualityEpsilon)
        => SimpleFloatEQ(value1, value2) || FloatGT(value1, value2, -epsilon);
}