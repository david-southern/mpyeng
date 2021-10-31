using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PiController
{
    public class AnimationParameter
    {
        public string Name { get; }
        public string Description { get; }
        public double Value { get; set; }

        public AnimationParameter(string name, string description, double value)
        {
            Name = name;
            Description = description;
            Value = value;
        }
    }

    public interface IAnimationEffect
    {
        string Name { get; }
        string Description { get; }
        List<AnimationParameter> Parameters { get; }
        int RenderOrder { get; }
        void Render(List<PixelColor> Pixels, bool showDiags = false);
    }
}
