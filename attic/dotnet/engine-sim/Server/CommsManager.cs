using CircuitPythonInterface;

namespace Server;

public class CommsManager : BackgroundService
{
    private CancellationToken ServerEnding;

    public CommsManager()
    {
    }

    protected override Task ExecuteAsync(CancellationToken stoppingToken)
    {
        Logger.Info("CommsManager starting.");

        ServerEnding = stoppingToken;

        return Task.Run(() => DoWork(), ServerEnding);
    }

    private static readonly double DiagsIntervalSeconds = 5;
    private static DateTime LastDiags = DateTime.MinValue;
    private static int frameCount = 0;

    private async Task CheckFrameRate(string desc = "")
    {
        frameCount++;
        double elapsedSeconds = (DateTime.Now - LastDiags).TotalSeconds;
        if (elapsedSeconds > DiagsIntervalSeconds)
        {
            await HandleCardReaders();

            Logger.Info($"CheckFrameRate({desc}): elapsed: {elapsedSeconds:N3}, " +
                $"frames: {frameCount}, frame rate: {frameCount / elapsedSeconds:N3} "
            );
            LastDiags = DateTime.Now;
            frameCount = 0;
        }
    }

    private async Task HandleCardReaders()
    {
        await Task.CompletedTask;

        try
        {
            CircuitPythonBoard? readerBoard = CircuitPythonBoardManager.FindBoard(ClientType.CardReader);

            if(readerBoard == null)
            {
                Logger.Info($"No CardReader CPy board found");
                return;
            }

            List<EngCard> cardStatus = readerBoard.QueryCards();
            Logger.Info($"Cards: {string.Join(", ", cardStatus)}");

            readerBoard.SetReaderColor(
                new List<ReaderColorDto>() {
                    new ReaderColorDto { ReaderIndex = 3, R = 255, G = 71, B = 96 },
                    new ReaderColorDto { ReaderIndex = 5, R = 0, G = 255, B = 23 },
                    new ReaderColorDto { ReaderIndex = 7, R = 42, G = 0, B = 196 }
                }
            );


            readerBoard.SetPowerDisplay(
                new List<PowerDisplayDto>() {
                    new PowerDisplayDto { DisplayIndex = 3, Value = 867 },
                    new PowerDisplayDto { DisplayIndex = 5, Value = 530 },
                    new PowerDisplayDto { DisplayIndex = 7, Value = 9 }
                }
            );
        }
        catch (Exception ex)
        {
            if (ex.Message.Contains("SerProto"))
            {
                Logger.Error(ex.Message);
            }
            else
            {
                Logger.Error(ex, $"HandleCardReaders");
            }
        }
    }

    private async Task DoWork()
    {
        try
        {
            Logger.Info("DoWork is starting");

            while (!ServerEnding.IsCancellationRequested)
            {
                await CheckFrameRate("CommsManager");
                await Task.Delay(100);
            }

            Logger.Info("DoWork is exiting");
        }
        catch (Exception ex)
        {
            Logger.Error($"CommsManager.DoWork caught exception: {ex}");
        }
    }

    public override async Task StopAsync(CancellationToken stoppingToken)
    {
        try
        {
            Logger.Info("CommsManager Service is stopping.");
            await base.StopAsync(stoppingToken);
        }
        catch (Exception ex)
        {
            Logger.Error($"CommsManager.StopAsync caught exception: {ex}");
        }
    }
}
