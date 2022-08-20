namespace engine_sim.Shared;

public partial class Flight
{
    public Guid Id { get; set; }
    public string Name { get; set; } = null!;
    public bool Running { get; set; }
    public List<Simulator>? Simulators { get; set; }

    public Simulator? Simulator
    {
        get
        {
            return Simulators?.FirstOrDefault();
        }
    }
}

public partial class Mission
{
    public string Name { get; set; } = null!;
}

public partial class Simulator
{
    public Guid Id { get; set; }
    public string Name { get; set; } = null!;
    public bool Template { get; set; }
    public List<Mission>? Missions { get; set; }


    public Mission? Mission
    {
        get
        {
            return Missions?.FirstOrDefault();
        }
    }
}

public partial class Reactor
{
    public Guid Id { get; set; }
    public string Name { get; set; } = null!;
    public string Model { get; set; } = null!;
    public double BatteryChargeLevel { get; set; }
    public double Efficiency { get; set; }
    public long PowerOutput { get; set; }
    public long LeftWingPower { get; set; }
    public long RightWingPower { get; set; }

    public long EffectivePower
    {
        get
        {
            return (long)(PowerOutput * Efficiency);
        }
    }

    public long EffectiveLeftWingPower
    {
        get
        {
            double requestedPower = LeftWingPower + RightWingPower;

            if(EffectivePower > requestedPower)
            {
                return LeftWingPower;
            } else
            {
                return (EffectivePower * LeftWingPower) / (LeftWingPower + RightWingPower);
            }
        }
    }
    public long EffectiveRightWingPower
    {
        get
        {
            double requestedPower = LeftWingPower + RightWingPower;

            if (EffectivePower > requestedPower)
            {
                return RightWingPower;
            }
            else
            {
                return (EffectivePower * RightWingPower) / (LeftWingPower + RightWingPower);
            }
        }
    }

}

public class ThoriumResponse
{
    public string? ErrorMessage { get; set; }
}

public class FlightsResponse : ThoriumResponse
{
    public List<Flight> Flights { get; set; } = new List<Flight>();
}

public class ReactorsResponse : ThoriumResponse
{
    public List<Reactor> Reactors { get; set; } = new List<Reactor>();
}


