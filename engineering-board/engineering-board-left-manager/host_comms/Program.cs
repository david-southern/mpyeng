using CircuitPythonInterface;
using Helpers;

Log.Logger = new LoggerConfiguration()
    .WriteTo.Console(outputTemplate: "{Timestamp:yyyy-MM-dd HH:mm:ss.fff} [{Level:u3}]  {SourceContext}: {Message:lj}{NewLine}{Exception}")
    .MinimumLevel.Debug()
    .CreateLogger();

Log.Information("Starting usb-protocol-client");

try
{
    CircuitPythonBoard? engBoard = CircuitPythonBoardManager.FindBoard(ClientType.EngineeringBoard);

    if (engBoard == null)
    {
        Log.Information($"No EngineeringBoard CPy board found");
        return;
    }

    var systemStatus = engBoard.QuerySystemPower();
    Log.Information($"SystemPower: {systemStatus.SafeJson()}");

//     engBoard.SetSystemPower(systemStatus);
}
catch (Exception ex)
{
    if (ex.Message.Contains("SerProto"))
    {
        Log.Error(ex.Message);
    }
    else
    {
        Log.Error(ex, $"usb-protocol-client");
    }
}
