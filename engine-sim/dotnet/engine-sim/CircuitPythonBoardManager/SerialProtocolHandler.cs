using System.IO.Ports;
using System.Text;

namespace CircuitPythonInterface;

public class ReaderColorDto
{
    public int ReaderIndex { get; set; }
    public int R { get; set; }
    public int G { get; set; }
    public int B { get; set; }
}

public class PowerDisplayDto
{
    public int DisplayIndex { get; set; }
    public int Value { get; set; }
}

public class SerialProtocolHandler : IDisposable
{
    public static int DEFAULT_BAUD_RATE { get; set; } = 9600;

    public const string SER_PROTO_RESPONSE_DELIMITER = ":";

    public const string SER_PROTO_INIT_HEADER = "SP_INIT";
    public const string SER_PROTO_INIT_RESPONSE = "SP_READY";
    public const string SER_PROTO_OK = "SP_OK";
    public const string SER_PROTO_ERR = "SP_ERR;";
    public const string SER_PROTO_CARDS_QUERY = "SP_CRD_Q";
    public const string SER_PROTO_CARDS_RESPONSE = "SP_CRD_R";
    public const string SER_PROTO_SET_READER_COLOR = "SP_RDR_RGB";
    public const string SER_PROTO_SET_DISPLAY_VALUE = "SP_DSP_VAL";

    private readonly object CommunicationLock = new();

    public readonly string PortName;
    public readonly string BoardName;
    private readonly SerialPort port;
    private bool IsValid = false;

    public SerialProtocolHandler(string portName, string boardName)
    {
        PortName = portName;
        BoardName = boardName;

        port = new SerialPort(portName, DEFAULT_BAUD_RATE, Parity.None, 8, StopBits.One)
        {
            ReadTimeout = 500,
            WriteTimeout = 500,
            Encoding = Encoding.UTF8,
            DtrEnable = true,
        };

        port.Open();
    }

    public bool IsConnected => port.IsOpen && IsValid;

    private void ResetPort()
    {
        // Make sure there is no pending data from other (possibly failed) transactions
        port.DiscardInBuffer();
        port.DiscardOutBuffer();
    }

    public bool EstablishConnection()
    {
        if (port == null) { return false; }

        lock (CommunicationLock)
        {
            try
            {
                ResetPort();

                port.WriteLine(SER_PROTO_INIT_HEADER);
                string response = port.ReadLine();

                if (response != SER_PROTO_INIT_RESPONSE)
                {
                    Logger.Error($"{this} is not a SerProto client: Invalid init response: {response}");
                    return false;
                }

                IsValid = true;
                return true;
            }
            catch (TimeoutException)
            {
                Logger.Error($"{this} is not a SerProto client: Timeout during EstablishConnection");
            }
            catch (Exception ex)
            {
                Logger.Error(ex, $"{this} is not a SerProto client: Unknown exception EstablishConnection");
            }

            return false;
        }
    }

    public List<EngCard> QueryCards()
    {
        List<EngCard> retval = new();

        lock (CommunicationLock)
        {
            try
            {
                ResetPort();
                port.WriteLine(SER_PROTO_CARDS_QUERY);
                string response = port.ReadLine();

                string[] responseParts = response.Split(SER_PROTO_RESPONSE_DELIMITER);

                if (responseParts.Length != 2 || responseParts[0] != SER_PROTO_CARDS_RESPONSE)
                {
                    Logger.Error($"SerProto {PortName}({BoardName}): Invalid card query response: {response}");
                    return retval;
                }

                List<int>? cardIds = JsonConvert.DeserializeObject<List<int>>(responseParts[1]);

                if (cardIds == null)
                {
                    Logger.Error($"{this}: Invalid card query response fromat: {response}");
                    return retval;
                }

                retval = cardIds.Select(id => EngCard.GetCard(id)).Where(card => card != null).ToList()!;
            }
            catch (TimeoutException)
            {
                Logger.Error($"SerProto {PortName}({BoardName}): Timeout during card query");
            }

            return retval;
        }
    }

    public string SetReaderColor(List<ReaderColorDto> data)
    {
        lock (CommunicationLock)
        {
            try
            {
                ResetPort();

                string request = SER_PROTO_SET_READER_COLOR + SER_PROTO_RESPONSE_DELIMITER
                    + JsonConvert.SerializeObject(data);
                port.WriteLine(request);
                string response = port.ReadLine();

                if (response != SER_PROTO_OK && !response.StartsWith(SER_PROTO_ERR))
                {
                    Logger.Error($"{this}: Invalid set reader color response: {response}");
                    return SER_PROTO_ERR;
                }

                return response;
            }
            catch (TimeoutException)
            {
                Logger.Error($"{this}: Timeout during reader color set");
                return SER_PROTO_ERR + ":Timeout";
            }
        }
    }

    public string SetPowerDisplay(List<PowerDisplayDto> data)
    {
        lock (CommunicationLock)
        {
            try
            {
                ResetPort();

                string request = SER_PROTO_SET_DISPLAY_VALUE + SER_PROTO_RESPONSE_DELIMITER
                    + JsonConvert.SerializeObject(data);
                port.WriteLine(request);
                string response = port.ReadLine();

                if (response != SER_PROTO_OK && !response.StartsWith(SER_PROTO_ERR))
                {
                    Logger.Error($"{this}: Invalid set power display response: {response}");
                    return SER_PROTO_ERR;
                }

                return response;
            }
            catch (TimeoutException)
            {
                Logger.Error($"{this}: Timeout during power display set");
                return SER_PROTO_ERR + ":Timeout";
            }
        }
    }

    public override string ToString()
    {
        return $"SerProto:{PortName}({BoardName})";
    }

    private bool AlreadyDisposed;

    protected virtual void Dispose(bool disposing)
    {
        Logger.Info($"{this}: Disposing");
        if (!AlreadyDisposed)
        {
            if (disposing)
            {
                IsValid = false;
                if (port.IsOpen)
                {
                    Logger.Info($"{this}: Closing SerialPort");
                    port.Close();
                }
                Logger.Info($"{this}: Disposing SerialPort");
                port.Dispose();
            }

            AlreadyDisposed = true;
        }
    }

    public void Dispose()
    {
        // Do not change this code. Put cleanup code in 'Dispose(bool disposing)' method
        Dispose(disposing: true);
        GC.SuppressFinalize(this);
    }
}