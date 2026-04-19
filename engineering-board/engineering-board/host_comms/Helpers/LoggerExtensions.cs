using System.Runtime.CompilerServices;
using Serilog.Context;

namespace Helpers;

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

    public static void DBG(this ILogger logger, string message, [CallerMemberName] string memberName = "")
    {
        using var prop = LogContext.PushProperty("MemberName", "." + memberName);
        Log.Debug(message);
    }

    public static void INF(this ILogger logger, string message, [CallerMemberName] string memberName = "")
    {
        using var prop = LogContext.PushProperty("MemberName", "." + memberName);
        Log.Information(message);
    }

    public static void WRN(this ILogger logger, string message, [CallerMemberName] string memberName = "")
    {
        using var prop = LogContext.PushProperty("MemberName", "." + memberName);
        Log.Warning(message);
    }

    public static void ERR(this ILogger logger, string message, [CallerMemberName] string memberName = "")
    {
        using var prop = LogContext.PushProperty("MemberName", "." + memberName);
        Log.Error(message);
    }

    public static void ERR(this ILogger logger, Exception ex, string message, [CallerMemberName] string memberName = "")
    {
        using var prop = LogContext.PushProperty("MemberName", "." + memberName);
        Log.Error(ex, message);
    }
}
