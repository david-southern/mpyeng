using System.Runtime.CompilerServices;

using Serilog.Context;
using Serilog.Events;

namespace SSG.Shared;

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

    public const string MEMBER_NAME_SEPARATOR = "::";

    public static void Debug(this ILogger logger, string message, [CallerMemberName] string memberName = "")
    {
        using var prop = LogContext.PushProperty("MemberName", MEMBER_NAME_SEPARATOR + memberName);
        logger.Write(LogEventLevel.Debug, message);
    }

    public static void Info(this ILogger logger, string message, [CallerMemberName] string memberName = "")
    {
        using var prop = LogContext.PushProperty("MemberName", MEMBER_NAME_SEPARATOR + memberName);
        logger.Write(LogEventLevel.Information, message);
    }

    public static void Warn(this ILogger logger, string message, [CallerMemberName] string memberName = "")
    {
        using var prop = LogContext.PushProperty("MemberName", MEMBER_NAME_SEPARATOR + memberName);
        logger.Write(LogEventLevel.Warning, message);
    }

    public static void Error(this ILogger logger, string message, [CallerMemberName] string memberName = "")
    {
        using var prop = LogContext.PushProperty("MemberName", MEMBER_NAME_SEPARATOR + memberName);
        logger.Write(LogEventLevel.Error, message);
    }

    public static void Error(this ILogger logger, Exception ex, string message, [CallerMemberName] string memberName = "")
    {
        using var prop = LogContext.PushProperty("MemberName", MEMBER_NAME_SEPARATOR + memberName);
        logger.Write(LogEventLevel.Error, message);
    }

    public static void Exception(this ILogger logger, Exception ex, string message, [CallerMemberName] string memberName = "")
    {
        using var prop = LogContext.PushProperty("MemberName", MEMBER_NAME_SEPARATOR + memberName);
        logger.Write(LogEventLevel.Error, message);
    }
}
