using System.Net.Http.Json;

namespace Helpers;

public class ApiHelper
{
    private readonly HttpClient _httpClient;

    public ApiHelper(HttpClient httpClient)
    {
        _httpClient = httpClient;
    }

    public async Task<FlightsResponse> GetFlights()
    {
        Logger.Info($"Calling GetFlights API");
        FlightsResponse retval = await _httpClient
            .GetFromJsonAsync<FlightsResponse>(Constants.API.FLIGHT_ENDPOINT) ?? new FlightsResponse();
        Logger.Info($"GetFlights API Result: {retval.SafeJson()}");
        return retval;
    }

    public async Task<ReactorsResponse> GetReactors(Guid simulatorId)
    {
        Logger.Info($"API: Calling GetReactors({simulatorId})");
        ReactorsResponse retval = await _httpClient
            .GetFromJsonAsync<ReactorsResponse>(Constants.API.REACTOR_URL(simulatorId)) ?? new ReactorsResponse();
        Logger.Info($"GetReactors API Result: {retval.SafeJson()}");
        return retval;
    }

    public async Task<string> UpdatePowerDisplays(List<PowerDisplay> powerDisplays)
    {
        Logger.Info($"Calling UpdatePowerDisplays API with: {string.Join(", ", powerDisplays.Select(pd => pd.ToString()))}");
        HttpResponseMessage result = await _httpClient.PostAsJsonAsync(Constants.API.ENDPOINT_POWER_DISPLAY, powerDisplays.ToArray());
        string retval = $"HTTP Result: {result.StatusCode}:{result.ReasonPhrase}";
        Logger.Info($"API Result: {retval}");
        return retval;
    }
}

