using System.Collections.Generic;
using System.Drawing;
using Microsoft.AspNetCore.Mvc.Rendering;

using PiController;

namespace pi_engine_room.Models
{
    public class WarpCoreViewModel
    {
        public static List<SelectListItem> AvailableColors { get; } = new List<SelectListItem>
        {
            new SelectListItem { Value = ColorTranslator.ToHtml(Color.Black), Text = "Black" },
            new SelectListItem { Value = ColorTranslator.ToHtml(Color.Red), Text = "Red" },
            new SelectListItem { Value = ColorTranslator.ToHtml(Color.Green), Text = "Green" },
            new SelectListItem { Value = ColorTranslator.ToHtml(Color.Blue), Text = "Blue" },
            new SelectListItem { Value = ColorTranslator.ToHtml(Color.White), Text = "White" },
        };

        public WarpCoreViewModel()
        {
            PowerLevel = WarpCore.Instance.PowerLevel;
            CurrentColor = WarpCore.Instance.TargetColor;
            AnimationEffects = WarpCore.Instance.AnimationEffects;
        }

        public double PowerLevel { get; set; } = 0;
        public string? CurrentColor { get; set; } = ColorTranslator.ToHtml(Color.Black);
        public List<IAnimationEffect> AnimationEffects { get; }
    }
}
