using System.Runtime.CompilerServices;
using Serilog.Context;

namespace Helpers
{
    public static class LoggerExtensions
    {
        public const string DATE_LOG_FORMAT = "yyyy-MM-dd";
        public const string DATETIME_LOG_FORMAT = "yyyy-MM-dd HH:mm:ss";
        public const string DATETIME_LOG_FORMAT_HIRES = "yyyy-MM-dd HH:mm:ss.fff";

        public static string ToLogFormat(this DateTime dt, bool hiRes = true)
        {
            return dt.ToString(hiRes ? DATETIME_LOG_FORMAT_HIRES : DATETIME_LOG_FORMAT);
        }

        public static string? ToLogFormat(this DateTime? dt, bool hiRes = true)
        {
            return dt?.ToString(hiRes ? DATETIME_LOG_FORMAT_HIRES : DATETIME_LOG_FORMAT);
        }

        public static string ToLogDateFormat(this DateTime dt)
        {
            return dt.ToString(DATE_LOG_FORMAT);
        }

        public static string? ToLogDateFormat(this DateTime? dt)
        {
            return dt?.ToString(DATE_LOG_FORMAT);
        }

        public static void Debug(this ILogger logger, string message, [CallerMemberName] string memberName = "")
        {
            using var prop = LogContext.PushProperty("MemberName", "." + memberName);
            logger.LogDebug(message);
        }

        public static void Info(this ILogger logger, string message, [CallerMemberName] string memberName = "")
        {
            using var prop = LogContext.PushProperty("MemberName", "." + memberName);
            logger.LogInformation(message);
        }

        public static void Warn(this ILogger logger, string message, [CallerMemberName] string memberName = "")
        {
            using var prop = LogContext.PushProperty("MemberName", "." + memberName);
            logger.LogWarning(message);
        }

        public static void Error(this ILogger logger, string message, [CallerMemberName] string memberName = "")
        {
            using var prop = LogContext.PushProperty("MemberName", "." + memberName);
            logger.LogError(message);
        }

        public static void Error(this ILogger logger, Exception ex, string message, [CallerMemberName] string memberName = "")
        {
            using var prop = LogContext.PushProperty("MemberName", "." + memberName);
            logger.LogError(ex, message);
        }
    }
}
