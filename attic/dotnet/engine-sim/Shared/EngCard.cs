namespace Shared;

public class EngCard
{
    public static readonly Dictionary<int, EngCard> AllCards = new();

    static EngCard()
    {
        static void AddCard(int id, string name, int power)
            => AllCards.Add(id, new EngCard(id, name, power));

        AddCard(1, "Shields", 70);
        AddCard(2, "Bio", 20);
        AddCard(3, "Phasers", 50);
        AddCard(4, "Warp", 100);
    }

    public static EngCard? GetCard(int id)
    {
        AllCards.TryGetValue(id, out EngCard? retval);
        return retval;
    }

    public int ID { get; set; }
    public string Name { get; set; }
    public float Voltage { get; set; }
    public int Power { get; set; }

    public EngCard(int id, string name, int power)
    {
        ID = id;
        Name = name;
        Power = power;
    }

    public override string ToString()
    {
        return $"{Name}({Power})";
    }
}
