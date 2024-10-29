namespace Helpers
{
    public static class Rand
    {
        private static readonly Random MyRand = new();

        /// <summary>
        /// A random double value linearly distributed between:
        /// * No Parameters: [0, 1.0)
        /// * One Parameters: [0, param)
        /// * Two Parameters: [firstParam, secondParam)
        /// </summary>
        public static double Linear(double? firstValue = null, double? secondValue = null)
        {
            double minValue, maxValue;

            if (firstValue == null) { minValue = 0; maxValue = 1; }
            else if (secondValue == null) { minValue = 0; maxValue = firstValue.Value; }
            else { minValue = firstValue.Value; maxValue = secondValue.Value; }
            if (maxValue < minValue) { double tmp = maxValue; maxValue = minValue; minValue = tmp; }
            return minValue + MyRand.NextDouble() * (maxValue - minValue);
        }

        /// <summary>
        /// A random double value linearly distributed between:
        /// * No Parameters: [0, int.MaxValue)
        /// * One Parameters: [0, param)
        /// * Two Parameters: [firstParam, secondParam)
        /// </summary>
        public static int LinearInt(int? firstValue = null, int? secondValue = null)
        {
            int minValue, maxValue;

            if (firstValue == null) { minValue = 0; maxValue = int.MaxValue; }
            else if (secondValue == null) { minValue = 0; maxValue = firstValue.Value; }
            else { minValue = firstValue.Value; maxValue = secondValue.Value; }
            if (maxValue < minValue) { int tmp = maxValue; maxValue = minValue; minValue = tmp; }
            return MyRand.Next(minValue, maxValue);
        }
    }

    public static partial class Utils
    {
        public static double Clamp(double value, double minValue = 0, double maxValue = 1)
        {
            return Math.Min(Math.Max(value, minValue), maxValue);
        }

        public static double Lerp(double start, double end, double progress)
        {
            double retval = start + (end - start) * progress;
            return retval;
        }

        public static Vector3 Lerp(Vector3 start, Vector3 end, double progress)
        {
            progress = Clamp(progress);
            return Vector3.Interpolate(start, end, progress);
        }

        public static double ListLerp(List<double> lerpList, double progress)
        {
            double realIndex = (lerpList.Count - 1) * progress;
            int intIndex = (int)Math.Floor(realIndex);

            if (intIndex >= lerpList.Count - 1)
            {
                return lerpList[lerpList.Count - 1];
            }

            return Lerp(lerpList[intIndex], lerpList[intIndex + 1], realIndex - intIndex);
        }
    }
}
