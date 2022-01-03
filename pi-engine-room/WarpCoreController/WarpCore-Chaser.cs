namespace WarpCoreController;

public class Chaser
{
    public static int NextChaserId = 0;

    public int ID { get; }
    public Vector3 Position { get; set; }
    public Vector3 Velocity { get; set; }
    public double Expiration { get; set; }

    public Chaser()
    {
        ID = NextChaserId++;
    }

    public void Update(double elapsedSeconds)
    {
        double newX = (Position.X + Velocity.X * elapsedSeconds) % WarpCore.WarpCoreSegmentCount;
        if (newX < 0) { newX += WarpCore.WarpCoreSegmentCount; }

        double newY = (Position.Y + Velocity.Y * elapsedSeconds) % WarpCore.WarpCoreSegmentLength;
        if (newY < 0) { newY += WarpCore.WarpCoreSegmentLength; }

        Position = new Vector3(newX, newY, 0);
    }

    public override string ToString()
    {
        return $"CH({ID}): P: {Position} - V: {Velocity} - Exp: {Expiration:N3}";
    }
}

public class WarpCoreChaser : IAnimationEffect
{
    private const int MAX_CHASERS = 100;

    public string Name => "WarpCore - Chaser";
    public string Description => "A high-contrast 'spark' that moves against the direction of the fog";
    public int RenderOrder => 300;

    private double PowerLevel;
    private double PowerLevelControlValue()
    {
        return PowerLevel;
    }

    // Speed is expressed in pixels/second
    private readonly DependentDouble MinSpeedX;
    private readonly DependentDouble SpeedXStart;
    private readonly DependentDouble SpeedXEnd;
    private readonly DependentRange ChaserSpeedX;

    private readonly DependentDouble MinSpeedY;
    private readonly DependentDouble SpeedYStart;
    private readonly DependentDouble SpeedYEnd;
    private readonly DependentRange ChaserSpeedY;

    private readonly DependentDouble LifetimeStart;
    private readonly DependentDouble LifetimeEnd;
    private readonly DependentRange ChaserLifetime;  // In seconds
    private readonly DependentDouble ChaserFreq;  // Seconds to the next chaser

    private readonly DependentDouble Hue;
    private readonly DependentDouble Sat;
    private readonly DependentDouble Val;
    private readonly HSVColorByDependent ChaserColor;

    private readonly List<Chaser> Chasers = new();

    private Chaser? diagChaser = null;

    void CreateNewChaser()
    {
        if (Chasers.Count >= MAX_CHASERS)
        {
            return;
        }

        double chaserX = Rand.LinearInt(0, WarpCore.WarpCoreSegmentCount);
        double chaserY = Rand.LinearInt(0, WarpCore.WarpCoreSegmentLength);

        double velX = 0;
        while (Math.Abs(velX) < MinSpeedX.Value)
        {
            velX = ChaserSpeedX.Value;
        }

        double velY = 0;
        while (Math.Abs(velY) < MinSpeedY.Value)
        {
            velY = ChaserSpeedY.Value;
        }

        Chaser chaser = new Chaser
        {
            Position = new Vector3(chaserX, chaserY, 0),
            Velocity = new Vector3(velX, velY, 0),
            Expiration = lastSimTime + ChaserLifetime.Value
        };

        Chasers.Add(chaser);

        lastChaserTime = lastSimTime;

        if (diagChaser == null) { diagChaser = chaser; }
        UpdateNextChaser();
    }

    void UpdateNextChaser()
    {
        nextChaserTime = lastChaserTime + ChaserFreq.Value;
    }

    private readonly CoreConfiguration Config;

    public WarpCoreChaser(CoreConfiguration config)
    {
        Config = config;
        
        //MinSpeedX = new(() => Rand.Linear(), 5, 10);
        //SpeedXStart = new(() => Rand.Linear(), -20, 20);
        //SpeedXEnd = new(() => Rand.Linear(), -60, 60);
        //ChaserSpeedX = new(PowerLevelControlValue, SpeedXStart, SpeedXEnd);

        MinSpeedX = new(() => 0, 0, 0);
        SpeedXStart = new(() => 0, 0, 0);
        SpeedXEnd = new(() => 0, 0, 0);
        ChaserSpeedX = new(PowerLevelControlValue, SpeedXStart, SpeedXEnd);

        MinSpeedY = new(() => Rand.Linear(), 30, 50);
        SpeedYStart = new(() => Rand.Linear(), -80, 80);
        SpeedYEnd = new(() => Rand.Linear(), -120, 120);
        ChaserSpeedY = new(PowerLevelControlValue, SpeedYStart, SpeedYEnd);

        LifetimeStart = new(() => Rand.Linear(), 4, 8);
        LifetimeEnd = new(() => Rand.Linear(), 2, 5);
        ChaserLifetime = new(PowerLevelControlValue, LifetimeStart, LifetimeEnd);

        ChaserFreq = new(PowerLevelControlValue, 3.0, 1.0);

        Hue = new(PowerLevelControlValue, HSVColor.HUE_GREEN, HSVColor.HUE_GREEN);
        Sat = new(PowerLevelControlValue, 1.0, 1.0);
        Val = new(PowerLevelControlValue, 1.0, 1.0);
        ChaserColor = new(Hue, Sat, Val);
    }

    double lastSimTime = 0;
    double lastChaserTime = 0;
    double lastPowerLevel = 0;
    double nextChaserTime = 0;

    public void Render(double powerLevel, double simElapsedTime, List<HSVColor> Pixels, bool showDiags = false)
    {
        double elapsedSeconds = simElapsedTime - lastSimTime;
        lastSimTime = simElapsedTime;

        PowerLevel = powerLevel;

        Chasers.RemoveAll(ch => ch.Expiration < simElapsedTime);

        if (diagChaser?.Expiration < simElapsedTime)
        {
            diagChaser = null;
        }

        if (powerLevel != lastPowerLevel)
        {
            UpdateNextChaser();
            lastPowerLevel = powerLevel;
        }

        if (simElapsedTime > nextChaserTime)
        {
            CreateNewChaser();
        }

        foreach (var chaser in Chasers)
        {
            chaser.Update(elapsedSeconds);

            int chaserX = (int)chaser.Position.X;
            int chaserY = (int)chaser.Position.Y;
            int pixelIndex = WarpCore.GetPixelIndex(chaserX, chaserY);

            if (pixelIndex < 0 || pixelIndex >= WarpCore.WarpCorePixelCount)
            {
                Logger.Error($"WarpCoreChaser: chaser {chaser.Position}, V: {chaser.Velocity} resulted in pixIndex: {pixelIndex}");
                continue;
            }

            Pixels[pixelIndex] = ChaserColor.Value;
        }

        //if (showDiags && diagChaser != null)
        //{
        //    Logger.Info($"WarpCoreChaser({simElapsedTime:N2}): Chaser count: {Chasers.Count}, {diagChaser}");
        //}
    }
}
