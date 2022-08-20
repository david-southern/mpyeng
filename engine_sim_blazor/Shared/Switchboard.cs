namespace engine_sim.Shared;

public class SwitchboardConn
{
    public string From { get; set; } = "";
    public string To { get; set; } = "";

    public SwitchboardConn(string from, string to)
    {
        From = from;
        To = to;
    }

    public override string ToString()
    {
        return $"{From}=>{To}";
    }
}

public class Switchboard
{
    public List<SwitchboardConn> Connections { get; set; } = new();

    public Switchboard(List<SwitchboardConn> connections)
    {
        Connections = connections;
    }

    public override string ToString()
    {
        return $"{string.Join(", ", Connections.Select(c => c.ToString()))}";
    }
}
