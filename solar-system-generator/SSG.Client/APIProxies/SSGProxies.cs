using Microsoft.Extensions.Options;

using Newtonsoft.Json.Serialization;

namespace SSG.APIProxies;

public partial class SolarSystemProxy
{

    private readonly HttpClient client;

    private readonly JsonSerializerSettings? jsonSerializerSettings;

    public SolarSystemProxy(HttpClient client, JsonSerializerSettings? jsonSerializerSettings = null)
    {
        if (client == null)
            throw new ArgumentNullException(nameof(client), "Null HttpClient.");

        if (client.BaseAddress == null)
            throw new ArgumentNullException(nameof(client), "HttpClient has no BaseAddress");

        this.client = client;
        this.jsonSerializerSettings = jsonSerializerSettings ?? new JsonSerializerSettings
        {
            PreserveReferencesHandling = PreserveReferencesHandling.Objects,
            ReferenceLoopHandling = ReferenceLoopHandling.Ignore,
            ContractResolver = new DefaultContractResolver { NamingStrategy = new DefaultNamingStrategy() }
        };
    }

    public async Task<CelestialObject?> GetSolarSystem()
    {
        string requestUri = "api/solar-system";
        using HttpRequestMessage httpRequestMessage = new HttpRequestMessage(HttpMethod.Get, requestUri);
        HttpResponseMessage responseMessage = await client.SendAsync(httpRequestMessage);
        try
        {
            responseMessage.EnsureSuccessStatusCode();
            Stream stream = await responseMessage.Content.ReadAsStreamAsync();
            using JsonReader jsonReader = new JsonTextReader(new StreamReader(stream));
            JsonSerializer serializer = JsonSerializer.Create(jsonSerializerSettings);
            return serializer.Deserialize<CelestialObject>(jsonReader);
        }
        finally
        {
            responseMessage.Dispose();
        }
    }
}
