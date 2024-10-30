using Microsoft.Extensions.Logging;

namespace Helpers
{
    public static class Logger
    {
        private static void Log(LogLevel level, string message, Exception? ex = null)
        {
            switch (level)
            {
                case LogLevel.Trace:
                    Serilog.Log.Logger.Verbose(message);
                    return;
                case LogLevel.Debug:
                    Serilog.Log.Logger.Debug(message);
                    return;
                default:
                case LogLevel.Information:
                    Serilog.Log.Logger.Information(message);
                    return;
                case LogLevel.Warning:
                    Serilog.Log.Logger.Warning(message);
                    return;
                case LogLevel.Error:
                    if (ex != null)
                    {
                        Serilog.Log.Logger.Error(ex, message);
                    }
                    else
                    {
                        Serilog.Log.Logger.Error(message);
                    }
                    return;
                case LogLevel.Critical:
                    Serilog.Log.Logger.Fatal(message);
                    return;
            }
        }

        public static void Info(string message)
        {
            Log(LogLevel.Information, message);
        }

        public static void Warn(string message)
        {
            Log(LogLevel.Warning, message);
        }

        public static void Error(string message)
        {
            Log(LogLevel.Error, message);
        }

        public static void Error(Exception ex, string message)
        {
            Log(LogLevel.Error, message, ex);
        }
    }
}
