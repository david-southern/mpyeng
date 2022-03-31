namespace CircuitPythonInterface;

[Flags]
public enum ClientType
{
    None,
    CardReader,
    Lighting,
    SevenSeg,
    Switchboard
}

public class CircuitPythonBoardManager
{
    public static readonly Dictionary<string, CircuitPythonBoard> KnownCPyBoards = new();
    public static readonly Dictionary<string, CircuitPythonBoard> PortToBoardMap = new();
    public static readonly Dictionary<ClientType, CircuitPythonBoard> ClientTypeMap = new();

    static CircuitPythonBoardManager()
    {
        static void AddBoard(string name, string vid, string pid, string mi, ClientType clientType)
            => KnownCPyBoards.Add(MakeKey(vid, pid, mi), new CircuitPythonBoard(name, vid, pid, mi, clientType));

        AddBoard("Adafruit Feather RP2040", "VID_239A", "PID_80F2", "MI_02", ClientType.CardReader);
    }

    private static string MakeKey(string vid, string pid, string mi)
    {
        return $"{vid}//{pid}//{mi}";
    }

    private static CircuitPythonBoard? GetBoard(string? vid, string? pid, string? mi)
    {
        if (vid == null || pid == null || mi == null) { return null; }
        KnownCPyBoards.TryGetValue(MakeKey(vid, pid, mi), out CircuitPythonBoard? retval);
        return retval;
    }

    public static void ScanSerialPorts()
    {
        var portInfo = SerialPortInfo.GetPortInformation();
        Logger.Info($"Serial Port Scan: {string.Join(", ", portInfo.Select(pi => pi.ToString()))}");
    }

    public static CircuitPythonBoard? FindBoard(ClientType clientType)
    {
        if (ClientTypeMap.TryGetValue(clientType, out CircuitPythonBoard? clientBoard))
        {
            if (clientBoard.IsConnected)
            {
                return clientBoard;
            }

            // If we found a board mapping but it is no longer connected then remove it from the
            // mappings
            ClientTypeMap.Remove(clientType);
            if (clientBoard.COMPort != null && PortToBoardMap.ContainsKey(clientBoard.COMPort))
            {
                PortToBoardMap.Remove(clientBoard.COMPort);
            }
        }

        List<SerialPortInfo> serialPorts = SerialPortInfo.GetPortInformation();

        foreach (SerialPortInfo portInfo in serialPorts)
        {
            // If the serialPort is connected to a device that doesn't match our CPy DeviceID
            // format, then the PortName field will not be set.  Ignore these ports
            if (portInfo.PortName == null)
            {
                continue;
            }

            // See if we already have a CPy board connected to this port
            if (PortToBoardMap.TryGetValue(portInfo.PortName, out CircuitPythonBoard? portBoard))
            {
                // Make sure that our port mapping is still valid
                if (!portBoard.IsConnected || portBoard.COMPort != portInfo.PortName)
                {
                    if (portBoard.COMPort != null)
                    {
                        // If not, then remove it from the mapping
                        PortToBoardMap.Remove(portBoard.COMPort);
                    }
                }
                else if (portBoard.ClientType == clientType)
                {
                    // If the connected board is the correct client type, then use it
                    return portBoard;
                }
            }

            // We don't have a board already connected to this port.  See if the port info indicated
            // that the attached device is a CPy board, according to the VID/PID/MI
            CircuitPythonBoard? boardInfo = GetBoard(portInfo.VID, portInfo.PID, portInfo.MI);

            if (boardInfo == null)
            {
                // The device on this port is  not a CPy board, so ignore it
                continue;
            }

            if (boardInfo.ClientType == clientType)
            {
                // See if we can connect to this board through the PortName we are checking
                if (boardInfo.SetCOMPort(portInfo.PortName))
                {
                    // Update our board mappings
                    ClientTypeMap[clientType] = boardInfo;
                    PortToBoardMap[portInfo.PortName] = boardInfo;

                    return boardInfo;
                }
            }
        }

        Logger.Info($"No {clientType} board found");
        return null;
    }
}