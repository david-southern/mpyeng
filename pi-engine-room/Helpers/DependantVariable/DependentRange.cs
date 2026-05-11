namespace Helpers
{
    // This dependent variable takes two DependentDoulbes as inputs, and interpolates between their dependent values
    // against the range's controlValue.
    //
    // The use case is to get a range of possible values where the range changes against the control variable.
    // Specifically, something like the Saturation parameter of the warp core fog effect. At power level zero we want
    // the saturation to range from 0.7 to 1.0 to give a range of light to full-color blues, but at power level 1 we
    // want the saturation to range from 0.0 to 0.4 so as the get a range of pure white to very light blue.
    //
    // We can accomplish this be specifying a DependentRange with a control value set from the core's PowerLevel, while
    // the range's valueAtStart and valueAtEnd would be DependentDoubles that use a simplex noise source as their
    // control value.
    public class DependentRange : IDependentVariable<double>
    {
        public DependentVariableType VariableType => DependentVariableType.Range;

        private Func<double> ControlValueSource { get; set; }

        public double ControlValue => ControlValueSource();

        public DependentDouble ValueAtStart { get; }
        public DependentDouble ValueAtEnd { get; }
        public EasingFunction DependentEasing { get; }

        public double Value => Utils.Lerp(ValueAtStart.Value, ValueAtEnd.Value, Easings.Interpolate(ControlValue, DependentEasing));

        public DependentRange(Func<double> controlValue, DependentDouble valueAtStart, DependentDouble valueAtEnd,
            EasingFunction dependentEasing
            = EasingFunction.Linear)
        {
            ControlValueSource = controlValue;
            DependentEasing = dependentEasing;

            ValueAtStart = valueAtStart;
            ValueAtEnd = valueAtEnd;
        }
    }
}
