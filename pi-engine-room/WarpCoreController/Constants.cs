global using System;
global using System.Collections.Generic;
global using System.Linq;
global using System.Text;
global using System.Threading.Tasks;

global using Helpers;


namespace PiController
{
    public static class Constants
    {
        public static class AnimParams
        {
            public const string ParamGroupScale = "Noise Scale";
            public const string ParamGroupSpeed = "Noise Speed";
            public const string ParamGroupColor = "For Color";

            public const string ParamX = "X";
            public const string ParamY = "Y";
            public const string ParamZ = "Z";

            public const string ParamHue = "Hue";
            public const string ParamSat = "Sat";
            public const string ParamVal = "Val";

            public static string ParamUnits(string paramGroup, string paramName)
            {
                switch (paramGroup)
                {
                case ParamGroupScale: return "Sample Space coordinate delta per LED";
                case ParamGroupSpeed: return "Seconds per Noise Scale";
                case ParamGroupColor:
                    switch (paramName)
                    {
                    case ParamHue: return "HSVColor Hue [0-360]";
                    case ParamSat: return "HSVColor Saturation % [0-100]";
                    case ParamVal: return "HSVColor Value % [0-100]";
                    }
                    break;
                }

                return "";
            }

            public static string ParamDescription(string paramGroup, string paramName)
            {
                switch (paramGroup)
                {
                case ParamGroupScale:
                    return "How 'tightly' should the noise function be sampled for each pixel. " +
                        "Smaller numbers will result in slower color change from one pixel the the next, and thus larger patches of colors " +
                        "with more gradual color change from one patch to the next.  Larger values will result in smaller patches and more " +
                        "abrupt color change from one patch to the next.";

                case ParamGroupSpeed: 
                    return "How quickly the noise origin moves through the noise field.  Lower values " +
                        "will result in the fog color patches changing more slowly, while higher values will change the patches more quickly.";

                case ParamGroupColor:
                    switch (paramName)
                    {
                    case ParamHue: 
                        return "The base hue of the fog - in the HSV color model, a color's Hue is modeled as an angle, ranging from 0-360 degrees.  " +
                            "Notable hue values: 0/360=Red, 60=Yellow, 120=Green, 180=Cyan, 240=Blue, 300=Magenta " +
                            "- <a href='https://en.wikipedia.org/wiki/HSL_and_HSV'>Wikipedia HSV</a>";
                    case ParamSat: 
                        return "The saturation of the fog - an indication of how intense the Hue is.  " +
                            "A saturation of 0% is pure white, while a saturation of 100% is pure color " +
                            "- <a href='https://en.wikipedia.org/wiki/HSL_and_HSV'>Wikipedia HSV</a>";
                    case ParamVal: 
                        return "The value of the fog - an indication of how bright the color is.  " +
                            "A value of 0% is pure black, while a value of 100% is full color (hue/sat) " +
                            "- <a href='https://en.wikipedia.org/wiki/HSL_and_HSV'>Wikipedia HSV</a>";
                    }
                    break;
                }

                return "";
            }
        }
    }
}
