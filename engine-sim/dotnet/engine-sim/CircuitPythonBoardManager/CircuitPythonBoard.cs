namespace CircuitPythonInterface;

public class CircuitPythonBoard
{
    public string Name { get; set; }
    public string VID { get; set; }
    public string PID { get; set; }
    public string MI { get; set; }
    public ClientType ClientType { get; set; }

    private SerialProtocolHandler? ProtocolHandler = null;

    public CircuitPythonBoard(string name, string vid, string pid, string mi, ClientType clientType)
    {
        Name = name;
        VID = vid;
        PID = pid;
        MI = mi;
        ClientType = clientType;
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

    public override string ToString()
    {
        string typeString = ClientType == ClientType.None ? "" : $"({ClientType})";
        return $"{Name}//{VID}//{PID}{typeString}";
    }
}