namespace engine_sim.Shared;

public class PowerGrid
{
    public bool LargeGrid { get; set; }
    public int GridIndex { get; set; }
    public List<int> LevelPct { get; set; } = new();


    public override string ToString()
    {
        return $"PowerGrid({GridIndex}): Large: {LargeGrid}";
    }
}

