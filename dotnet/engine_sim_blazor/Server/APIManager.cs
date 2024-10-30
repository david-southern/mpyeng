using GraphQL;
using GraphQL.Client.Abstractions;

namespace engine_sim.Server;

public static class APIManager
{
    public static void MapAPIEndpoints(this WebApplication app)
    {
        app.MapGet(Constants.API.FLIGHT_ENDPOINT, async (GraphQLConsumer _gql) =>
        {
            return await _gql.GetAllFlights();
        });

        app.MapGet($"{Constants.API.REACTOR_ENDPOINT}/{{simulatorId}}",
            async (Guid simulatorId, GraphQLConsumer _gql) =>
            {
                _gql.SubscribeReactor(simulatorId);

                return await _gql.GetAllReactors(simulatorId);
            });

        app.MapPost(Constants.API.ENDPOINT_POWER_DISPLAY, (PowerDisplay[] powerDisplays) =>
        {
            if (powerDisplays == null || !powerDisplays.Any())
            {
                Logger.Error("UpdatePowerDisplays called with no data");
                return null;
            }

            return CommsManager.UpdatePowerDisplays(new List<PowerDisplay>(powerDisplays));
        });
    }
}
