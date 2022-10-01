using Blazored.LocalStorage;
using Flurl;
using Flurl.Http;

public class SSGAPIClient
{
    private const string SYSTEM_LIST_KEY = "SSG.SystemList";

    private readonly ConfigurationService config;
    private readonly ILocalStorageService localStorage;

    public SSGAPIClient(ConfigurationService _config, ILocalStorageService _localStorage)
    {
        config = _config;
        localStorage = _localStorage;
    }

    private bool serverConnected = true;

    public async Task<CelestialObject[]> ListSolarSystems()
    {
        if (serverConnected)
        {
            try
            {
                return await config.ServerBaseAddress
                    .AppendPathSegment("/api/solar-system")
                    .GetJsonAsync<CelestialObject[]>();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Exception: {ex.Message}");
                serverConnected = false;
            }
        }

        // Try the browser's local storage instead
        string systemJSON = await localStorage.GetItemAsync<string>(SYSTEM_LIST_KEY) ?? "[]";
        List<CelestialObject> retval = JsonConvert.DeserializeObject<List<CelestialObject>>(systemJSON) ?? new();
        if(!retval.Any(co => co.Name == MockSolarSystemData.Sol.Name))
        {
            retval.Add(MockSolarSystemData.Sol);
        }
        if (!retval.Any(co => co.Name == MockSolarSystemData.CygnusX1.Name))
        {
            retval.Add(MockSolarSystemData.CygnusX1);
        }

        return retval.ToArray();
    }

    public async Task<CelestialObject?> LoadSolarSystem(string systemName)
    {
        if (serverConnected)
        {
            try
            {
                return await config.ServerBaseAddress
                    .AppendPathSegment("/api/solar-system")
                    .SetQueryParam("systemName", systemName)
                    .GetJsonAsync<CelestialObject?>();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Exception: {ex.Message}");
                serverConnected = false;
            }
        }

        var systemList = await ListSolarSystems();
        return systemList.FirstOrDefault(co => co.Name == systemName);
    }

    public async Task<bool> SaveSolarSystem(CelestialObject system)
    {
        if (serverConnected)
        {
            try
            {
                var result = await config.ServerBaseAddress
                    .AppendPathSegment("/api/solar-system")
                    .PostJsonAsync(system);

                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Exception: {ex.Message}");
                serverConnected = false;
            }
        }

        // Try the browser's local storage instead
        List<CelestialObject> systemList = new (await ListSolarSystems());

        systemList.RemoveAll(co => co.Name == system.Name);
        systemList.Add(system);

        await localStorage.SetItemAsync(SYSTEM_LIST_KEY, JsonConvert.SerializeObject(systemList));
        return true;
    }
}
