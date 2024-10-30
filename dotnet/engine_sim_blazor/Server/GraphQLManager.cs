using GraphQL;
using GraphQL.Client.Abstractions;

namespace engine_sim.Server;

public static class GraphQLQueries
{
    public static GraphQLRequest AllFlights()
    {
        return new GraphQLRequest
        {
            Query = @"
                query ThoriumFlight
                {
                    flights 
                    {
                        id
                        name
                        running 
                        simulators 
                        {
                            id
                            name
                            template
                        }
                    }
                }"
        };
    }


    public static GraphQLRequest Reactors(Guid simulatorId)
    {
        return new GraphQLRequest
        {
            Query = @"
            query ReactorStatus($simId: ID)
            { 
	            reactors(simulatorId: $simId)
	            {
		            id
                    name 
                    model 
                    batteryChargeLevel
                    efficiency
                    powerOutput 
                    leftWingPower
                    rightWingPower 
	            }
            }",
            Variables = new
            {
                simId = simulatorId.ToString()
            }
        };
    }
}

public class GraphQLSubscriptionManager : IDisposable
{
    public static readonly Dictionary<Guid, IDisposable> Subscriptions = new();
    private readonly ILogger<GraphQLSubscriptionManager> Logger;

    public GraphQLSubscriptionManager(ILogger<GraphQLSubscriptionManager> logger)
    {
        Logger = logger;
    }

    private bool AlreadyDisposed;

    protected virtual void Dispose(bool disposing)
    {
        Logger.Info($"{this}: Disposing");
        if (!AlreadyDisposed)
        {
            if (disposing)
            {
                foreach (var subKVP in Subscriptions)
                {
                    subKVP.Value.Dispose();
                }
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


public class GraphQLConsumer
{
    private readonly IGraphQLClient _client;
    private readonly ILogger<GraphQLConsumer> Logger;

    public GraphQLConsumer(IGraphQLClient client, ILogger<GraphQLConsumer> logger)
    {
        _client = client;
        Logger = logger;
    }

    public async Task<FlightsResponse> GetAllFlights()
    {
        FlightsResponse retval = new();

        GraphQLResponse<FlightsResponse>? response = 
            await _client.SendQueryAsync<FlightsResponse>(GraphQLQueries.AllFlights());

        if (response == null)
        {
            retval.ErrorMessage = "No response to Thorium Flight query";
        }
        else
        {
            if (response.Errors?.Any() ?? false)
            {
                retval.ErrorMessage = "Thorium Flight Query Error: "
                    + string.Join(", ", response.Errors
                        .Select(err => $"{(err.Path.HasValue() ? err.Path + ": " : "")}{err.Message}"));
            }

            if (response.Data?.ErrorMessage != null)
            {
                retval.ErrorMessage += (retval.ErrorMessage == null ? "Thorium Flight Query Data Error: " : ", ")
                    + response.Data.ErrorMessage;
            }

            if (response.Data?.Flights != null)
            {
                retval.Flights = response.Data.Flights;
            }
        }

        return retval;
    }

    public async Task<ReactorsResponse> GetAllReactors(Guid simulatorId)
    {
        ReactorsResponse retval = new();

        GraphQLResponse<ReactorsResponse>? response =
            await _client.SendQueryAsync<ReactorsResponse>(GraphQLQueries.Reactors(simulatorId));

        if (response == null)
        {
            retval.ErrorMessage = "No response to Thorium Reactor query";
        }
        else
        {
            if (response.Errors?.Any() ?? false)
            {
                retval.ErrorMessage = "Thorium Reactor Query Error: "
                    + string.Join(", ", response.Errors
                        .Select(err => $"{(err.Path.HasValue() ? err.Path + ": " : "")}{err.Message}"));
            }

            if (response.Data?.ErrorMessage != null)
            {
                retval.ErrorMessage += (retval.ErrorMessage == null ? "Thorium Reactor Query Data Error: " : ", ")
                    + response.Data.ErrorMessage;
            }

            if (response.Data?.Reactors != null)
            {
                retval.Reactors = response.Data.Reactors;
            }
        }

        return retval;
    }

    public void SubscribeReactor(Guid simulatorId)
    {
        if (GraphQLSubscriptionManager.Subscriptions.TryGetValue(simulatorId, out IDisposable? subscription))
        {
            return;
        }

        IObservable<GraphQLResponse<ReactorsResponse>> subscriptionStream
            = _client.CreateSubscriptionStream<ReactorsResponse>(GraphQLQueries.Reactors(simulatorId));

        subscription = subscriptionStream.Subscribe(response =>
        {
            if (response.Data.Reactors.Count > 0)
            {
                Reactor changed = response.Data.Reactors[0];
                Logger.Info($"Reactor: {changed.Name}: Power: {changed.EffectivePower}, " +
                    $"Left: {changed.EffectiveLeftWingPower}, Right: {changed.EffectiveRightWingPower}");
            }
        });

        GraphQLSubscriptionManager.Subscriptions.Add(simulatorId, subscription);
    }
}
