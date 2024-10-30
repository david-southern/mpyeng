namespace Helpers
{
    public class HSVColorByDependent
    {
        public IDependentVariable<double> Hue { get; }
        public IDependentVariable<double> Saturation { get; }
        public IDependentVariable<double> ColorValue { get; }

        public HSVColor Value => new(Hue.Value, Saturation.Value, ColorValue.Value);

        public HSVColorByDependent(IDependentVariable<double> hue, IDependentVariable<double> saturation, IDependentVariable<double> colorValue)
        {
            Hue = hue;
            Saturation = saturation;
            ColorValue = colorValue;
        }
    }

    public class DependentHSVColor : IDependentVariable<HSVColor>
    {
        public DependentVariableType VariableType => DependentVariableType.HSVColor;

        private Func<double> ControlValueSource { get; set; }

        public double ControlValue => ControlValueSource();

        public HSVColorByDependent ValueAtStart { get; }
        public HSVColorByDependent ValueAtEnd { get; }
        public EasingFunction DependentEasing { get; }

        public HSVColor Value => Utils.Lerp(ValueAtStart.Value, ValueAtEnd.Value, Easings.Interpolate(ControlValue, DependentEasing));

        public DependentHSVColor(Func<double> controlValue, HSVColorByDependent valueAtStart, HSVColorByDependent valueAtEnd,
            EasingFunction dependentEasing = EasingFunction.Linear)
        {
            ControlValueSource = controlValue;
            DependentEasing = dependentEasing;

            ValueAtStart = valueAtStart;
            ValueAtEnd = valueAtEnd;
        }
    }

}
