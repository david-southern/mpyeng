using System.IO.Ports;
using System.Text;
using EngBoard;
using Helpers;

namespace CircuitPythonInterface;

public class SerialProtocolHandler : IDisposable
{
    public static int DEFAULT_BAUD_RATE { get; set; } = 9600;

    public const string SER_PROTO_RESPONSE_DELIMITER = "|";
    public const string SER_PROTO_QUERY = "_QUERY";
    public const string SER_PROTO_RESPONSE = "_RESPONSE";
    public const string SER_PROTO_SET = "_SET";

    public const string SER_PROTO_INIT_HEADER = "SP_INIT";
    public const string SER_PROTO_INIT_RESPONSE = "SP_READY";
    public const string SER_PROTO_OK = "SP_OK";
    public const string SER_PROTO_ERR = "SP_ERR;";
    public const string SER_PROTO_ENGINE_POWER = "SP_ENG_POWER";
    public const string SER_PROTO_TRANSFORMER_POWER = "SP_TRANS_POWER";
    public const string SER_PROTO_SYSTEM_POWER = "SP_SYS_POWER";

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
                    Log.Error($"{this} is not a SerProto client: Invalid init response: {response}");
                    return false;
                }

                IsValid = true;
                return true;
            }
            catch (TimeoutException)
            {
                Log.Error($"{this} is not a SerProto client: Timeout during EstablishConnection");
            }
            catch (Exception ex)
            {
                Log.Error(ex, $"{this} is not a SerProto client: Unknown exception EstablishConnection");
            }

            return false;
        }
    }

    public List<EnginePower> QueryEnginePower()
    {
        Log.Information($"Sending QueryEnginePower");
        return QueryList<EnginePower>(SER_PROTO_ENGINE_POWER);
    }

    public List<TransformerPower> QueryTransformerPower()
    {
        Log.Information($"Sending QueryTransformerPower");
        return QueryList<TransformerPower>(SER_PROTO_TRANSFORMER_POWER);
    }

    public List<SystemPower> QuerySystemPower()
    {
        Log.Information($"Sending QuerySystemPower");
        return QueryList<SystemPower>(SER_PROTO_SYSTEM_POWER);
    }

    private List<T> QueryList<T>(string protocolToken) where T : EngBoardResource
    {
        List<T> EmptyResult = [];

        lock (CommunicationLock)
        {
            try
            {
                ResetPort();
                string protocolCommand = protocolToken + SER_PROTO_QUERY;

                Log.Debug($"QueryList: Sending: {protocolCommand}");
                port.WriteLine(protocolCommand);
                string response = port.ReadLine();
                Log.Debug($"QueryList: Received: {response}");

                string[] responseParts = response.Split(SER_PROTO_RESPONSE_DELIMITER);

                if (responseParts.Length != 2 || responseParts[0] != protocolToken + SER_PROTO_RESPONSE)
                {
                    Log.Error($"SerProto {PortName}({BoardName}): Invalid query list response: {response}");
                    return EmptyResult;
                }

                try {
                    return JsonConvert.DeserializeObject<List<T>>(responseParts[1]) ?? EmptyResult;
                } catch (Exception ex) {
                    Log.Error(ex, $"SerProto {PortName}({BoardName}): Invalid query list response format: {response}: {ex.Message}");
                    return EmptyResult;
                }   
            }
            catch (TimeoutException)
            {
                Log.Error($"SerProto {PortName}({BoardName}): Timeout during query list");
            }

            return EmptyResult;
        }
    }

    public string SetEnginePower(List<EnginePower> data)
    {
        return SetList(SER_PROTO_ENGINE_POWER, data);
    }

    public string SetTransformerPower(List<TransformerPower> data)
    {
        return SetList(SER_PROTO_TRANSFORMER_POWER, data);
    }

    public string SetSystemPower(List<SystemPower> data)
    {
        return SetList(SER_PROTO_SYSTEM_POWER, data);
    }

    public string SetList<T>(string protocolToken, List<T> data) where T : EngBoardResource
    {
        lock (CommunicationLock)
        {
            try
            {
                ResetPort();

                string request = protocolToken + SER_PROTO_SET + SER_PROTO_RESPONSE_DELIMITER
                    + JsonConvert.SerializeObject(data);
                port.WriteLine(request);
                string response = port.ReadLine();

                if (response != SER_PROTO_OK && !response.StartsWith(SER_PROTO_ERR))
                {
                    Log.Error($"{this}: Invalid set list response: {response}");
                    return SER_PROTO_ERR;
                }

                return response;
            }
            catch (TimeoutException)
            {
                Log.Error($"{this}: Timeout during set list");
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
        Log.Information($"{this}: Disposing");
        if (!AlreadyDisposed)
        {
            if (disposing)
            {
                IsValid = false;
                if (port.IsOpen)
                {
                    Log.Information($"{this}: Closing SerialPort");
                    port.Close();
                }
                Log.Information($"{this}: Disposing SerialPort");
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