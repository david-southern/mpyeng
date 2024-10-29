namespace Helpers;

public class Vector3ByDependent
{
    public IDependentVariable<double> X { get; }
    public IDependentVariable<double> Y { get; }
    public IDependentVariable<double> Z { get; }

    public Vector3 Value => new(X.Value, Y.Value, Z.Value);

    public Vector3ByDependent(IDependentVariable<double> x, IDependentVariable<double> y, IDependentVariable<double> z)
    {
        X = x;
        Y = y;
        Z = z;
    }
}

public class DependentVector3 : IDependentVariable<Vector3>
{
    public DependentVariableType VariableType => DependentVariableType.Vector3;

    private Func<double> ControlValueSource { get; set; }

    public double ControlValue => ControlValueSource();

    public Vector3ByDependent ValueAtStart { get; }
    public Vector3ByDependent ValueAtEnd { get; }
    public EasingFunction DependentEasing { get; }

    public Vector3 Value => Utils.Lerp(ValueAtStart.Value, ValueAtEnd.Value, Easings.Interpolate(ControlValue, DependentEasing));

    public DependentVector3(Func<double> controlValue, Vector3ByDependent valueAtStart, Vector3ByDependent valueAtEnd,
        EasingFunction dependentEasing = EasingFunction.Linear)
    {
        ControlValueSource = controlValue;
        DependentEasing = dependentEasing;

        ValueAtStart = valueAtStart;
        ValueAtEnd = valueAtEnd;
    }
}
