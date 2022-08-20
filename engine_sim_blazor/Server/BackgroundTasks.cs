using System.Collections.Generic;

using CircuitPythonInterface;

using GraphQL;

namespace engine_sim.Server;

public class BackgroundTaskManager : BackgroundService
{
    private CancellationToken ServerEnding;

    public BackgroundTaskManager()
    {
    }

    protected override Task ExecuteAsync(CancellationToken stoppingToken)
    {
        Logger.Info("BackgroundTaskManager starting.");

        ServerEnding = stoppingToken;

        return Task.Run(() => DoWork(), ServerEnding);
    }

    private static readonly double DiagsIntervalSeconds = 5;
    private static DateTime LastDiags = DateTime.MinValue;
    private static int frameCount = 0;

    private void CheckFrameRate(string desc = "")
    {
        frameCount++;
        double elapsedSeconds = (DateTime.Now - LastDiags).TotalSeconds;
        if (elapsedSeconds > DiagsIntervalSeconds)
        {
            Logger.Info($"CheckFrameRate({desc}): elapsed: {elapsedSeconds:N3}, " +
                $"frames: {frameCount}, frame rate: {frameCount / elapsedSeconds:N3} "
            );
            LastDiags = DateTime.Now;
            frameCount = 0;
        }
    }

    private async Task DoWork()
    {
        try
        {
            Logger.Info("DoWork is starting");

            while (!ServerEnding.IsCancellationRequested)
            {
                CheckFrameRate("BackgroundTaskManager");

                await Task.Delay(100);
            }

            Logger.Info("DoWork is exiting");
        }
        catch (Exception ex)
        {
            Logger.Error($"BackgroundTaskManager.DoWork caught exception: {ex}");
        }
    }

    public override async Task StopAsync(CancellationToken stoppingToken)
    {
        try
        {
            Logger.Info("BackgroundTaskManager Service is stopping.");
            await base.StopAsync(stoppingToken);
        }
        catch (Exception ex)
        {
            Logger.Error($"BackgroundTaskManager.StopAsync caught exception: {ex}");
        }
    }
}
