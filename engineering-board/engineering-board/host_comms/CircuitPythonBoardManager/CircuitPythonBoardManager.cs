// spell-checker: disable

namespace CircuitPythonInterface;

public enum ClientType
{
    None,
    EngineeringBoard,
}

public class CircuitPythonBoardManager
{
    /// <summary>
    /// Maps each ClientType to the board that serves it.
    /// Populated via <see cref="RegisterBoard"/>.
    /// </summary>
    private static readonly Dictionary<ClientType, CircuitPythonBoard> BoardRegistry = [];

    /// <summary>
    /// Cache of client types that are currently connected.
    /// </summary>
    private static readonly Dictionary<ClientType, CircuitPythonBoard> ClientTypeMap = [];

    // TODO: set the static IP address (or hostname) assigned to your Pimoroni Pico Plus 2 W.
    // The port must match TCP_PORT in secrets.py on the device.
    private const string EngineeringBoardIP = "192.168.1.100";
    private const int DefaultTCPPort = 8765;

    static CircuitPythonBoardManager()
    {
        List<ClientType> allClients = [ClientType.EngineeringBoard];

        RegisterBoard(
            new CircuitPythonBoard(
                "Pimoroni Pico Plus 2 W - EngineeringBoard",
                EngineeringBoardIP,
                DefaultTCPPort,
                allClients
            )
        );
    }

    private static void RegisterBoard(CircuitPythonBoard board)
    {
        foreach (var clientType in board.ClientTypes)
        {
            BoardRegistry[clientType] = board;
        }
    }

    private static void UnmapBoard(CircuitPythonBoard board)
    {
        var staleEntries = ClientTypeMap
            .Where(kvp => kvp.Value == board)
            .Select(kvp => kvp.Key)
            .ToList();
        staleEntries.ForEach(key => ClientTypeMap.Remove(key));
    }

    public static CircuitPythonBoard? FindBoard(ClientType clientType)
    {
        if (ClientTypeMap.TryGetValue(clientType, out CircuitPythonBoard? cached))
        {
            if (cached.IsConnected)
            {
                return cached;
            }

            UnmapBoard(cached);
        }

        if (!BoardRegistry.TryGetValue(clientType, out CircuitPythonBoard? board))
        {
            Log.Information($"No board registered for client type {clientType}");
            return null;
        }

        Log.Information($"Connecting to {board}...");
        if (!board.Connect())
        {
            Log.Information($"Failed to connect to {board}");
            return null;
        }

        foreach (var ct in board.ClientTypes)
        {
            ClientTypeMap[ct] = board;
        }

        return board;
    }
}
