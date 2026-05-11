using System.Text.RegularExpressions;
using System.Runtime.InteropServices;

using System.Diagnostics.CodeAnalysis;
using System.Net;

namespace Helpers
{
    public static class HelpersExtensions
    {
        /// <summary>
        /// Returns true if the string is non-null
        /// </summary>
        public static bool IsDefined([NotNullWhen(true)]this string? checkString)
        {
            return checkString != null && checkString.Length > 0;
        }

        /// <summary>
        /// Returns true if the string is non-null and non-empty
        /// </summary>
        public static bool HasValue([NotNullWhen(true)]this string? checkString)
        {
            return checkString != null && checkString.Length > 0;
        }

        /// <summary>
        /// Returns true if the List is non-null and non-empty
        /// </summary>
        public static bool HasValue<T>([NotNullWhen(true)]this List<T>? checkList)
        {
            return checkList != null && checkList.Count > 0;
        }

        /// <summary>
        /// Perform CompareTo but return 0 (equal) if both instances are null
        /// </summary>
        /// <param name="first"></param>
        /// <param name="second"></param>
        /// <returns></returns>
        public static int CompareToNull(this string? first, string? second)
        {
            if (first == null && second == null) return 0;
            if (first == null) return 1;
            if (second == null) return -1;
            return first.CompareTo(second);
        }

        /// <summary>
        /// Perform CompareTo but return 0 (equal) if both instances are null
        /// </summary>
        /// <param name="first"></param>
        /// <param name="second"></param>
        /// <returns></returns>
        public static int CompareToNull(this DateTime? first, DateTime? second)
        {
            if (first == null && second == null) return 0;
            if (first == null) return 1;
            if (second == null) return -1;
            return first.Value.CompareTo(second.Value);
        }

        /// <summary>
        /// Determine whether the two dates fall within the same month
        /// </summary>
        public static bool IsSameMonthAs(this DateTime dateTime, DateTime otherDateTime)
        {
            return dateTime.Year == otherDateTime.Year && dateTime.Month == otherDateTime.Month;
        }

        /// <summary>
        /// Determine whether the two dates fall within the same month.  If either date is null, this check always fails.
        /// </summary>
        public static bool IsSameMonthAs(this DateTime? dateTime, DateTime otherDateTime)
        {
            if (dateTime == null) return false;
            return dateTime.Value.IsSameMonthAs(otherDateTime);
        }

        /// <summary>
        /// Determine whether the two dates fall within the same month.  If either date is null, this check always fails.
        /// </summary>
        public static bool IsSameMonthAs(this DateTime dateTime, DateTime? otherDateTime)
        {
            if (otherDateTime == null) return false;
            return dateTime.IsSameMonthAs(otherDateTime.Value);
        }

        /// <summary>
        /// Determine whether the two dates fall within the same month.  If either date is null, this check always fails.
        /// </summary>
        public static bool IsSameMonthAs(this DateTime? dateTime, DateTime? otherDateTime)
        {
            // NULL IsSameMonthAs always fails, even NULL.IsSameMonthAs(NULL)
            if (dateTime == null || otherDateTime == null) return false;
            return dateTime.Value.IsSameMonthAs(otherDateTime.Value);
        }

        public static bool IsMatch(this string? input, string regEx, RegexOptions? options = null)
        {
            if (input == null)
            {
                return false;
            }

            if (options == null) options = RegexOptions.None;

            return Regex.IsMatch(input, regEx, options.Value);
        }

        public static string? Match(this string? input, string regEx, RegexOptions? options = null)
        {
            if (input == null)
            {
                return null;
            }

            if (options == null) options = RegexOptions.None;

            Match? result = Regex.Match(input, regEx, options.Value);

            return (result?.Success ?? false) ? result.Value : null;
        }

        /// <summary>
        /// Returns true if 1) both lists are null, or 2) neither list is null, and neither list contains any value
        /// that is not in the other list.  
        /// Note: This method does not consider the number of occurences of an elelement in each list, nor does it
        /// consider the order of the elements.  So [1, 2, 2, 2, 3] would be considered equal to [3, 2, 1].
        /// </summary>
        /// <typeparam name="T"></typeparam>
        /// <param name="self"></param>
        /// <param name="other"></param>
        /// <returns></returns>
        public static bool ContentsEqualTo<T>(this List<T>? self, List<T>? other)
        {
            if(self == null && other == null)
            {
                return true;
            }

            if(self == null || other == null)
            {
                return false;
            }

            bool exception = self.Except(other).Any();

            if (exception) return false;

            return !other.Except(self).Any();
        }
    }

    public static partial class Utils
    {
        public static class OperatingSystem
        {
            public static bool IsWindows() => RuntimeInformation.IsOSPlatform(OSPlatform.Windows);
            public static bool IsMacOS() => RuntimeInformation.IsOSPlatform(OSPlatform.OSX);
            public static bool IsLinux() => RuntimeInformation.IsOSPlatform(OSPlatform.Linux);
        }

        /// <summary>
        /// Return the first parameter that is not zero.  Allows quick tie-breaking of CompareTo calls.
        /// </summary>
        /// <param name="compareResults"></param>
        /// <returns></returns>
        public static int CoalesceCompareTo(params int[] compareResults)
        {
            return compareResults.FirstOrDefault(check => check != 0);
        }

        public static string AddURLQueryParam(string baseUrl, string paramName, object? paramValue)
        {
            if (!baseUrl.HasValue())
            {
                throw new ArgumentNullException("AddURLQueryParam called without a baseUrl");
            }

            if (paramValue == null)
            {
                return baseUrl;
            }

            if (!paramName.HasValue())
            {
                throw new ArgumentNullException("AddURLQueryParam called without a paramName");
            }

            string? paramValueString = SafeString(paramValue);

            if (!paramValueString.HasValue())
            {
                throw new ArgumentNullException("AddURLQueryParam called without a paramValue");
            }

            string paramSep = baseUrl.Contains("?") ? "&" : "?";

            return baseUrl + paramSep + WebUtility.UrlEncode(paramName) + "=" + WebUtility.UrlEncode(paramValueString);
        }

        public static double Lerp(double startValue, double endValue, double lerpAmount, bool clamp = true)
        {
            double lerpResult = startValue + (endValue - startValue) * lerpAmount;
            if(clamp)
            {
                if(startValue > endValue)
                {
                    double tmp = startValue;
                    startValue = endValue;
                    endValue = tmp;
                }
                lerpResult = Math.Max(Math.Min(lerpResult, endValue), startValue);
            }
            return lerpResult;
        }
    }
}
