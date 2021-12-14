namespace WarpCoreController;

public interface IAnimationEffect
{
    string Name { get; }
    string Description { get; }
    int RenderOrder { get; }
    void Render(double powerLevel, double simElapsedTime, List<HSVColor> Pixels, bool showDiags = false);
}
