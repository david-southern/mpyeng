using EngBoard;

namespace CircuitPythonInterface;

public class CircuitPythonBoard
{
    public string Name { get; set; }
    public string IPAddress { get; set; }
    public int TCPPort { get; set; }
    public List<ClientType> ClientTypes { get; set; }

    private TcpProtocolHandler? ProtocolHandler = null;

    public CircuitPythonBoard(
        string name,
        string ipAddress,
        int tcpPort,
        List<ClientType> clientTypes
    )
    {
        Name = name;
        IPAddress = ipAddress;
        TCPPort = tcpPort;
        ClientTypes = clientTypes;
    }

    public bool Connect()
    {
        ProtocolHandler?.Dispose();
        ProtocolHandler = null;

        try
        {
            var handler = new TcpProtocolHandler(IPAddress, TCPPort, Name);
            if (!handler.EstablishConnection())
            {
                handler.Dispose();
                return false;
            }

            ProtocolHandler = handler;
            return true;
        }
        catch (Exception ex)
        {
            Log.Error(ex, $"{this}: Failed to connect");
            return false;
        }
    }

    public bool IsConnected => ProtocolHandler?.IsConnected ?? false;
    public string? ConnectionId => ProtocolHandler?.ConnectionId;

    public List<EnginePower> QueryEnginePower() => ProtocolHandler?.QueryEnginePower() ?? [];

    public List<TransformerPower> QueryTransformerPower() =>
        ProtocolHandler?.QueryTransformerPower() ?? [];

    public List<SystemPower> QuerySystemPower() => ProtocolHandler?.QuerySystemPower() ?? [];

    public string SetEnginePower(List<EnginePower> data) =>
        ProtocolHandler?.SetEnginePower(data) ?? string.Empty;

    public string SetTransformerPower(List<TransformerPower> data) =>
        ProtocolHandler?.SetTransformerPower(data) ?? string.Empty;

    public string SetSystemPower(List<SystemPower> data) =>
        ProtocolHandler?.SetSystemPower(data) ?? string.Empty;

    public override string ToString()
    {
        return $"{Name}//{IPAddress}:{TCPPort} - ClientTypes: {string.Join(", ", ClientTypes.Select(ct => ct.ToString()))}";
    }
}
