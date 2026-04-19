using System.IO;
using System.Net.Sockets;
using System.Text;
using EngBoard;
using Helpers;

namespace CircuitPythonInterface;

public class TcpProtocolHandler : IDisposable
{
    public const string SER_PROTO_RESPONSE_DELIMITER = "|";
    public const string SER_PROTO_QUERY = "_QUERY";
    public const string SER_PROTO_RESPONSE = "_RESPONSE";
    public const string SER_PROTO_SET = "_SET";

    public const string SER_PROTO_INIT_HEADER = "SP_INIT";
    public const string SER_PROTO_INIT_RESPONSE = "SP_READY";
    public const string SER_PROTO_OK = "SP_OK";
    public const string SER_PROTO_ERR = "SP_ERR";
    public const string SER_PROTO_ENGINE_POWER = "SP_ENG_POWER";
    public const string SER_PROTO_TRANSFORMER_POWER = "SP_TRANS_POWER";
    public const string SER_PROTO_SYSTEM_POWER = "SP_SYS_POWER";

    private static readonly int TimeoutMs = 3000;

    private readonly object CommunicationLock = new();

    public readonly string IPAddress;
    public readonly int Port;
    public readonly string BoardName;
    public string ConnectionId => $"{IPAddress}:{Port}";

    private readonly TcpClient _client;
    private StreamReader? _reader;
    private StreamWriter? _writer;
    private bool IsValid = false;

    public TcpProtocolHandler(string ipAddress, int port, string boardName)
    {
        IPAddress = ipAddress;
        Port = port;
        BoardName = boardName;

        _client = new TcpClient();
        _client.ReceiveTimeout = TimeoutMs;
        _client.SendTimeout = TimeoutMs;
        _client.Connect(ipAddress, port);

        var stream = _client.GetStream();
        _reader = new StreamReader(stream, Encoding.UTF8);
        _writer = new StreamWriter(stream, new UTF8Encoding(false))
        {
            AutoFlush = true,
            NewLine = "\n",
        };
    }

    public bool IsConnected => _client.Connected && IsValid;

    public bool EstablishConnection()
    {
        lock (CommunicationLock)
        {
            try
            {
                _writer!.WriteLine(SER_PROTO_INIT_HEADER);
                string? response = _reader!.ReadLine();

                if (response != SER_PROTO_INIT_RESPONSE)
                {
                    Log.Error($"{this}: Invalid init response: {response}");
                    return false;
                }

                IsValid = true;
                return true;
            }
            catch (IOException ex)
            {
                Log.Error($"{this}: IO error during EstablishConnection: {ex.Message}");
            }
            catch (Exception ex)
            {
                Log.Error(ex, $"{this}: Unknown exception during EstablishConnection");
            }

            return false;
        }
    }

    public List<EnginePower> QueryEnginePower()
    {
        Log.Information("Sending QueryEnginePower");
        return QueryList<EnginePower>(SER_PROTO_ENGINE_POWER);
    }

    public List<TransformerPower> QueryTransformerPower()
    {
        Log.Information("Sending QueryTransformerPower");
        return QueryList<TransformerPower>(SER_PROTO_TRANSFORMER_POWER);
    }

    public List<SystemPower> QuerySystemPower()
    {
        Log.Information("Sending QuerySystemPower");
        return QueryList<SystemPower>(SER_PROTO_SYSTEM_POWER);
    }

    private List<T> QueryList<T>(string protocolToken)
        where T : EngBoardResource
    {
        List<T> emptyResult = [];

        lock (CommunicationLock)
        {
            try
            {
                string protocolCommand = protocolToken + SER_PROTO_QUERY;
                Log.Debug($"QueryList: Sending: {protocolCommand}");
                _writer!.WriteLine(protocolCommand);
                string? response = _reader!.ReadLine();
                Log.Debug($"QueryList: Received: {response}");

                if (response == null)
                {
                    Log.Error($"{this}: Connection closed during query list");
                    return emptyResult;
                }

                string[] responseParts = response.Split(SER_PROTO_RESPONSE_DELIMITER);

                if (
                    responseParts.Length != 2
                    || responseParts[0] != protocolToken + SER_PROTO_RESPONSE
                )
                {
                    Log.Error($"{this}: Invalid query list response: {response}");
                    return emptyResult;
                }

                try
                {
                    return JsonConvert.DeserializeObject<List<T>>(responseParts[1]) ?? emptyResult;
                }
                catch (Exception ex)
                {
                    Log.Error(
                        ex,
                        $"{this}: Invalid query list response format: {response}: {ex.Message}"
                    );
                    return emptyResult;
                }
            }
            catch (IOException ex)
            {
                Log.Error($"{this}: IO error during query list: {ex.Message}");
            }

            return emptyResult;
        }
    }

    public string SetEnginePower(List<EnginePower> data) => SetList(SER_PROTO_ENGINE_POWER, data);

    public string SetTransformerPower(List<TransformerPower> data) =>
        SetList(SER_PROTO_TRANSFORMER_POWER, data);

    public string SetSystemPower(List<SystemPower> data) => SetList(SER_PROTO_SYSTEM_POWER, data);

    public string SetList<T>(string protocolToken, List<T> data)
        where T : EngBoardResource
    {
        lock (CommunicationLock)
        {
            try
            {
                string request =
                    protocolToken
                    + SER_PROTO_SET
                    + SER_PROTO_RESPONSE_DELIMITER
                    + JsonConvert
                        .SerializeObject(data)
                        .Replace("|", string.Empty)
                        .Replace("\r", string.Empty)
                        .Replace("\n", string.Empty);
                _writer!.WriteLine(request);
                string? response = _reader!.ReadLine();

                if (response == null)
                {
                    Log.Error($"{this}: Connection closed during set list");
                    return SER_PROTO_ERR;
                }

                if (response != SER_PROTO_OK && !response.StartsWith(SER_PROTO_ERR))
                {
                    Log.Error($"{this}: Invalid set list response: {response}");
                    return SER_PROTO_ERR;
                }

                return response;
            }
            catch (IOException ex)
            {
                Log.Error($"{this}: IO error during set list: {ex.Message}");
                return SER_PROTO_ERR + ":IO";
            }
        }
    }

    public override string ToString() => $"TcpProto:{ConnectionId}({BoardName})";

    private bool AlreadyDisposed;

    protected virtual void Dispose(bool disposing)
    {
        Log.Information($"{this}: Disposing");
        if (!AlreadyDisposed)
        {
            if (disposing)
            {
                IsValid = false;
                _reader?.Dispose();
                _writer?.Dispose();
                _client.Close();
                _client.Dispose();
            }

            AlreadyDisposed = true;
        }
    }

    public void Dispose()
    {
        Dispose(disposing: true);
        GC.SuppressFinalize(this);
    }
}
