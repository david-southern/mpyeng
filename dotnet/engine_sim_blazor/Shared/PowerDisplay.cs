namespace engine_sim.Shared;

public class PowerDisplay
{
    public int DisplayIndex { get; set; }
    public int Value { get; set; }

    public override string ToString()
    {
        return $"PowerDisplay({DisplayIndex}): {Value}";
    }
}
