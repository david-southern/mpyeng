namespace Helpers
{
    public enum DependentVariableType
    {
        Unknown,
        Double,
        Range,
        HSVColor,
        Vector3
    }

    public interface IDependentVariable<T>
    {
        public DependentVariableType VariableType { get; }

        public double ControlValue { get; }
        public EasingFunction DependentEasing { get; }
        public T Value { get; }
    }
}
