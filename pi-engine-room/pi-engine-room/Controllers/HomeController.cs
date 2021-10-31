using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;

using pi_engine_room.Models;

using PiController;

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.Linq;
using System.Threading.Tasks;

namespace pi_engine_room.Controllers
{
    public class HomeController : Controller
    {
        private readonly WarpCore Core = WarpCore.Instance;

        public HomeController()
        {
        }

        public IActionResult Index()
        {
            WarpCoreViewModel model = new();
            return View("Index", model);
        }

        [HttpPost]
        public IActionResult StripColor(WarpCoreViewModel model)
        {
            Logger.Info($"Setting strip color to: {model.CurrentColor}");
            Core.TargetColor = model.CurrentColor;

            return Index();
        }

        [HttpPost]
        public IActionResult PowerLevel(WarpCoreViewModel model)
        {
            Logger.Info($"Setting power level to: {model.PowerLevel}");
            Core.PowerLevel = model.PowerLevel;

            return Index();
        }

        [HttpPost]
        public IActionResult UpdateParams(WarpCoreViewModel model)
        {
            Logger.Info($"Updating core params:");

            foreach (var effect in model.AnimationEffects)
            {
                foreach (var effectParam in effect.Parameters)
                {
                    Logger.Info($"    {effect.Name}.{effectParam.Name}: {effectParam.Value}");
                }
            }

            return Index();
        }



        [ResponseCache(Duration = 0, Location = ResponseCacheLocation.None, NoStore = true)]
        public IActionResult Error()
        {
            return View(new ErrorViewModel { RequestId = Activity.Current?.Id ?? HttpContext.TraceIdentifier });
        }
    }
}
