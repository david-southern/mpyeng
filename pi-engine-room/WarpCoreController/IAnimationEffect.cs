using Helpers;

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PiController
{
    public interface IAnimationEffect
    {
        string Name { get; }
        string Description { get; }
        int RenderOrder { get; }
        void Render(double powerLevel, List<HSVColor> Pixels, bool showDiags = false);
    }
}
