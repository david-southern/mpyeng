namespace engine_sim.Shared;

public class CardReader
{
    public int ReaderIndex { get; set; }
    public int R { get; set; }
    public int G { get; set; }
    public int B { get; set; }


    public override string ToString()
    {
        return $"CardReader({ReaderIndex}): RGB: ({R},{G},{B})";
    }
}
