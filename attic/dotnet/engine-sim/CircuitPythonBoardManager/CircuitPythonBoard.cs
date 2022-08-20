namespace CircuitPythonInterface;

public class CircuitPythonBoard
{
    public string Name { get; set; }
    public string VID { get; set; }
    public string PID { get; set; }
    public string SerialNumber { get; set; }
    public List<ClientType> ClientTypes { get; set; }

    private SerialProtocolHandler? ProtocolHandler = null;

    public CircuitPythonBoard(string name, string vid, string pid, string serNo, List<ClientType> clientTypes)
    {
        Name = name;
        VID = vid;
        PID = pid;
        SerialNumber = serNo;
        ClientTypes = clientTypes;
    }

    public bool SetCOMPort(string comPort)
    {
        ProtocolHandler = new SerialProtocolHandler(comPort, Name);

        if(!ProtocolHandler.EstablishConnection())
        {
            ProtocolHandler.Dispose();
            ProtocolHandler = null;
            return false;
        }

        return true;
    }

    public bool IsConnected => ProtocolHandler?.IsConnected ?? false;
    public string? COMPort => ProtocolHandler?.PortName;

    public List<EngCard> QueryCards() => ProtocolHandler?.QueryCards() ?? new List<EngCard>();
    public string SetReaderColor(List<ReaderColorDto> data)
        => ProtocolHandler?.SetReaderColor(data) ?? SerialProtocolHandler.SER_PROTO_ERR;
    public string SetPowerDisplay(List<PowerDisplayDto> data)
        => ProtocolHandler?.SetPowerDisplay(data) ?? SerialProtocolHandler.SER_PROTO_ERR;

    public override string ToString()
    {
        return $"{Name}//{VID}//{SerialNumber} - ClientTypes: {string.Join(", ", ClientTypes.Select(ct => ct.ToString()))}";
    }
}