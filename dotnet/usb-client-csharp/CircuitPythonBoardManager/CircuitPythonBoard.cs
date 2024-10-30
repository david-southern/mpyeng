using EngBoard;

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

    public List<EnginePower> QueryEnginePower() => ProtocolHandler?.QueryEnginePower() ?? [];
    public List<TransformerPower> QueryTransformerPower() => ProtocolHandler?.QueryTransformerPower() ?? [];
    public List<SystemPower> QuerySystemPower() => ProtocolHandler?.QuerySystemPower() ?? [];

    public string SetEnginePower(List<EnginePower> data) => ProtocolHandler?.SetEnginePower(data) ?? string.Empty;
    public string SetTransformerPower(List<TransformerPower> data) => ProtocolHandler?.SetTransformerPower(data) ?? string.Empty;
    public string SetSystemPower(List<SystemPower> data) => ProtocolHandler?.SetSystemPower(data) ?? string.Empty;


    public override string ToString()
    {
        return $"{Name}//{VID}//{SerialNumber} - ClientTypes: {string.Join(", ", ClientTypes.Select(ct => ct.ToString()))}";
    }
}