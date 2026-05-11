using System.Text.RegularExpressions;

namespace Helpers
{
    public class DependentDouble : IDependentVariable<double>
    {
        public const string LOW_VALUE_GROUP = "lowValue";
        public const string HIGH_VALUE_GROUP = "highValue";
        public const string DEP_DOUBLE_REGEX = @"^(?'" + LOW_VALUE_GROUP + @"'[\-\+]?\d+(?:\.\d+)?)(?:\s*(?'" + HIGH_VALUE_GROUP + @"'[\-\+]?\d+(?:\.\d+)?))?$";

        public DependentVariableType VariableType => DependentVariableType.Double;
        public string ConfigRegex => DEP_DOUBLE_REGEX;
        public string ConfigDescription => "&plusmn;nn.nn (Constant Value)<br>&plusmn;nn.nn nn.nn (&lt;Low Value&gt; &lt;High Value&gt;)";

        private Func<double> ControlValueSource { get; set; }

        public double ControlValue => ControlValueSource();

        public double ValueAtStart { get; }
        public double ValueAtEnd { get; }
        public EasingFunction DependentEasing { get; }

        public double Value => Utils.Lerp(ValueAtStart, ValueAtEnd, Easings.Interpolate(ControlValue, DependentEasing));

        public DependentDouble(Func<double> controlValue, double valueAtStart, double valueAtEnd, EasingFunction dependentEasing
            = EasingFunction.Linear)
        {
            ControlValueSource = controlValue;
            DependentEasing = dependentEasing;

            ValueAtStart = valueAtStart;
            ValueAtEnd = valueAtEnd;
        }
    }
}
