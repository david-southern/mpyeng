namespace engine_sim.Shared;

public static class Constants
{
    public static class API
    {
        public const string ENDPOINT_POWER_DISPLAY = "/api/power-display";
        public const string FLIGHT_ENDPOINT = "/api/flight";
        public const string REACTOR_ENDPOINT = "/api/reactor";

        public static string REACTOR_URL(Guid simulatorId) {
            return $"{REACTOR_ENDPOINT}/{simulatorId}";
        }
        
    }
}
