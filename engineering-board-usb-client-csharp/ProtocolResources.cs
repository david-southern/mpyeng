using System.Text;

namespace EngBoard;

public abstract class EngBoardResource
{
    public string Name { get; set; } = string.Empty;
}

public class EnginePower : EngBoardResource
{
    public int MaxPower { get; set; }
    public int PowerUsage { get; set; }
}

public class TransformerPower : EngBoardResource
{
    public int MaxPower { get; set; }
    public int PowerUsage { get; set; }
}

public class SystemPower : EngBoardResource
{
    public int Power { get; set; }
    public int CardCount { get; set; }
}