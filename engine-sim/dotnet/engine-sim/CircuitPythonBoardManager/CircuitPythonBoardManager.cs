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
        #region Serial Port Device IDs for various Circuit Python boards:

        // Board ID (Feather RP2040 Pink)
        // * Adafruit CircuitPython 7.2.3 on 2022-03-16; Adafruit Feather RP2040 with rp2040
        // * Board ID:adafruit_feather_rp2040
        // * Scan Results - Data:
        // * Port: COM19 // VID: VID_239A, PID: PID_80F2, MI: MI_02, Addl: 6&6E93409&0&0002
        // *       Raw Name: USB Serial Device (COM19)
        // *       Raw DeviceID: USB\VID_239A&PID_80F2&MI_02\6&6E93409&0&0002
        // * Scan Results - Console:
        // * Port: COM18 // VID: VID_239A, PID: PID_80F2, MI: MI_00, Addl: 6&6E93409&0&0000
        // *       Raw Name: USB Serial Device (COM18)
        // *       Raw DeviceID: USB\VID_239A&PID_80F2&MI_00\6&6E93409&0&0000

        // Board ID (Feather RP2040 Black)
        // 8 Adafruit CircuitPython 7.2.3 on 2022-03-16; Adafruit Feather RP2040 with rp2040
        // * Board ID:adafruit_feather_rp2040
        // * Scan Results - Console:
        // * Port: COM30 // VID: VID_239A, PID: PID_80F2, MI: MI_00, Addl: 6&1F8589CA&0&0000
        // *       Raw Name: USB Serial Device (COM30)
        // *       Raw DeviceID: USB\VID_239A&PID_80F2&MI_00\6&1F8589CA&0&0000
        // * Scan Results - Data:
        // * Port: COM31 // VID: VID_239A, PID: PID_80F2, MI: MI_02, Addl: 6&1F8589CA&0&0002
        // *       Raw Name: USB Serial Device (COM31)
        // *       Raw DeviceID: USB\VID_239A&PID_80F2&MI_02\6&1F8589CA&0&0002

        // Board ID
        // * Adafruit CircuitPython 7.2.3 on 2022-03-16; Adafruit Grand Central M4 Express with samd51p20
        // * Scan Results - Console:
        // * Board ID:grandcentral_m4_express
        // * Port: COM3 // VID: VID_239A, PID: PID_8032, MI: MI_00, Addl: 7&256F071&0&0000
        // *       Raw Name: USB Serial Device (COM3)
        // *       Raw DeviceID: USB\VID_239A&PID_8032&MI_00\7&256F071&0&0000
        // * Scan Results - Data:
        // * Port: COM33 // VID: VID_239A, PID: PID_8032, MI: MI_02, Addl: 7&256F071&0&0002
        // *       Raw Name: USB Serial Device (COM33)
        // *       Raw DeviceID: USB\VID_239A&PID_8032&MI_02\7&256F071&0&0002


        // Board ID
        // * Adafruit CircuitPython 7.2.3 on 2022 - 03 - 16; Adafruit ItsyBitsy M4 Express with samd51g19
        // * Board ID:itsybitsy_m4_express
        // * Scan Results - Data:
        // * Port: COM20 // VID: VID_239A, PID: PID_802C, MI: MI_02, Addl: 6&B566A03&0&0002
        // *       Raw Name: USB Serial Device (COM20)
        // *       Raw DeviceID: USB\VID_239A&PID_802C&MI_02\6&B566A03&0&0002
        // * Scan Results - Console:
        // * Port: COM10 // VID: VID_239A, PID: PID_802C, MI: MI_00, Addl: 6&B566A03&0&0000
        // *       Raw Name: USB Serial Device (COM10)
        // *       Raw DeviceID: USB\VID_239A&PID_802C&MI_00\6&B566A03&0&0000

        // Board ID
        // * Adafruit CircuitPython 7.2.3 on 2022-03-16; Adafruit Feather M4 Express with samd51j19
        // * Board ID:feather_m4_express
        // * Scan Results - Data:
        // * Port: COM21 // VID: VID_239A, PID: PID_8026, MI: MI_02, Addl: 6&2E1D05AC&0&0002
        // *       Raw Name: USB Serial Device (COM21)
        // *       Raw DeviceID: USB\VID_239A&PID_8026&MI_02\6&2E1D05AC&0&0002
        // * Scan Results - Console:
        // * Port: COM6 // VID: VID_239A, PID: PID_8026, MI: MI_00, Addl: 6&2E1D05AC&0&0000
        // *       Raw Name: USB Serial Device (COM6)
        // *       Raw DeviceID: USB\VID_239A&PID_8026&MI_00\6&2E1D05AC&0&0000

        // Board ID
        // * Adafruit CircuitPython 7.2.3 on 2022-03-16; Adafruit Trinket M0 with samd21e18
        // * Board ID:trinket_m0
        // * Scan Results - Data:
        // * Port: COM29 // VID: VID_239A, PID: PID_801F, MI: MI_02, Addl: 7&32FD1556&0&0002
        // *       Raw Name: USB Serial Device (COM29)
        // *       Raw DeviceID: USB\VID_239A&PID_801F&MI_02\7&32FD1556&0&0002
        // * Scan Results - Console:
        // * Port: COM28 // VID: VID_239A, PID: PID_801F, MI: MI_00, Addl: 7&32FD1556&0&0000
        // *       Raw Name: USB Serial Device (COM28)
        // *       Raw DeviceID: USB\VID_239A&PID_801F&MI_00\7&32FD1556&0&0000


        /*

Serial Port Scan:


         */



        // Board ID
        // * Adafruit CircuitPython 7.2.3 on 2022-03-16; TinyS2 with ESP32S2
        // * Board ID:unexpectedmaker_tinys2
        // * Scan Results - Console:
        // * Port: COM25 // VID: VID_303A, PID: PID_8002, MI: MI_00, Addl: 6&2F83AEC5&0&0000
        // *       Raw Name: USB Serial Device (COM25)
        // *       Raw DeviceID: USB\VID_303A&PID_8002&MI_00\6&2F83AEC5&0&0000
        // * Seems to be something wrong with the USB_CDC mode - no data serial is showing up...

        // Board ID
        // * Adafruit ItsyBitsy 32u4 5V 16Mhz -- NOT A CIRCUIT PYTHON BOARD
        // * Scan Results - Arduino USB
        // * Port: COM15 // VID: VID_239A, PID: PID_000E, MI: MI_00, Addl: 7&1C4AEE92&0&0000
        // *       Raw Name: USB Serial Device (COM15)
        // *       Raw DeviceID: USB\VID_239A&PID_000E&MI_00\7&1C4AEE92&0&0000

        // Board ID
        // * Adafruit ESP32 HUZZAH Feather -- NOT A CIRCUIT PYTHON BOARD
        // * Raw Serial Data: (Not detected by this manager class)
        // *         Name: Silicon Labs CP210x USB to UART Bridge (COM22)
        // *         DeviceID: USB\VID_10C4&PID_EA60\0232A46B

        #endregion

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
        var portInfos = SerialPortInfo.GetPortInformation();
        Logger.Info($"Serial Port Scan:");

        if(portInfos.Count > 0)
        {
            foreach (SerialPortInfo portInfo in portInfos)
            {
                Logger.Info($"  Port: {portInfo}");
                Logger.Info($"        Raw Name: {portInfo.Name}");
                Logger.Info($"        Raw DeviceID: {portInfo.DeviceID}");
            }
        } else
        {
            SerialPortInfo.GetPortInformation(true);
        }
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