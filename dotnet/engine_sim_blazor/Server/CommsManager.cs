using System.Collections.Generic;

using CircuitPythonInterface;

namespace engine_sim.Server;

public static class CommsManager
{
    public static string? UpdatePowerGrids(List<PowerGrid> data)
    {
        try
        {
            CircuitPythonBoard? readerBoard = CircuitPythonBoardManager.FindBoard(ClientType.CardReader);

            if (readerBoard == null)
            {
                Logger.Info($"No PowerGrid CPy board found");
                return null;
            }

            return readerBoard.SetPowerGridLevel(data);
        }
        catch (Exception ex)
        {
            if (ex.Message.Contains("SerProto"))
            {
                Logger.Error(ex.Message);
            }
            else
            {
                Logger.Error(ex, $"UpdatePowerGrids");
            }
        }

        return null;
    }

    public static Switchboard? QuerySwitchboard()
    {
        try
        {
            CircuitPythonBoard? readerBoard = CircuitPythonBoardManager.FindBoard(ClientType.Switchboard);

            if (readerBoard == null)
            {
                Logger.Info($"No Switchboard CPy board found");
                return null;
            }

            List<List<string>>? switchboardData = readerBoard.QuerySwitchboard();

            if (switchboardData == null)
            {
                Logger.Error("QuerySwitchboard: Null result from CPy board");
                return null;
            }

            Switchboard retval = new(switchboardData
                .Where(conn => conn?.Count == 2)
                .Select(conn => new SwitchboardConn(conn[0], conn[1]))
                .ToList()
            );

            Logger.Info($"Switchboard: {retval}");

            return retval;
        }
        catch (Exception ex)
        {
            if (ex.Message.Contains("SerProto"))
            {
                Logger.Error(ex.Message);
            }
            else
            {
                Logger.Error(ex, $"QuerySwitchboard");
            }
        }

        return null;
    }

    public static List<EngCard>? QueryCardReaders()
    {
        try
        {
            CircuitPythonBoard? readerBoard = CircuitPythonBoardManager.FindBoard(ClientType.CardReader);

            if (readerBoard == null)
            {
                Logger.Info($"No CardReader CPy board found");
                return null;
            }

            return readerBoard.QueryCards();
        }
        catch (Exception ex)
        {
            if (ex.Message.Contains("SerProto"))
            {
                Logger.Error(ex.Message);
            }
            else
            {
                Logger.Error(ex, $"QueryCardReaders");
            }
        }

        return null;
    }

    public static string? UpdateCardReaders(List<CardReader> data)
    {
        try
        {
            CircuitPythonBoard? readerBoard = CircuitPythonBoardManager.FindBoard(ClientType.CardReader);

            if (readerBoard == null)
            {
                Logger.Info($"No CardReader CPy board found");
                return null;
            }

            return readerBoard.SetReaderColor(data);
        }
        catch (Exception ex)
        {
            if (ex.Message.Contains("SerProto"))
            {
                Logger.Error(ex.Message);
            }
            else
            {
                Logger.Error(ex, $"UpdateCardReaders");
            }
        }

        return null;
    }

    public static string? UpdatePowerDisplays(List<PowerDisplay> powerDisplays)
    {
        try
        {
            if (powerDisplays == null)
            {
                throw new ArgumentNullException(nameof(powerDisplays));
            }

            Logger.Info($"UpdatePowerDisplays: Starting update of: {string.Join(", ", powerDisplays.Select(pd => pd.ToString()))}");

            CircuitPythonBoard? sevenSegBoard = CircuitPythonBoardManager.FindBoard(ClientType.SevenSeg);

            if (sevenSegBoard == null)
            {
                throw new Exception($"No SevenSeg SerProto board found");
            }

            return sevenSegBoard.SetPowerDisplay(powerDisplays);
        }
        catch (Exception ex)
        {
            Logger.Error(ex, $"UpdatePowerDisplays");
        }

        return null;
    }
}
