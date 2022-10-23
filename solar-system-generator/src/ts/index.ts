import { CelestialObject } from "./celestial-object";
import { Sol } from "./solar-system";
import { Logger, SSGSystemFilter } from "./ssg.logger";
import { SSGRenderer } from "./ssg.renderer";
import GUI from "lil-gui";

import { GlobalSettings } from "./ssg.settings";

export const Renderer = new SSGRenderer();


function LoadPremade(system: CelestialObject)
{
    Logger.info(SSGSystemFilter.Always, `Loading premade solar system: ${system.Name}`);
}

LoadPremade(Sol());

GlobalSettings.MaxAnimationSpeedScale = 10;

class Controller
{
    public pauseAnimation()
    {
        GlobalSettings.AnimationSpeed = 0;
    }
}

const controller = new Controller();

const gui = new GUI();

gui.add(GlobalSettings, "AnimationSpeed", -1, 1, 0.0001);
gui.add(controller, "pauseAnimation");
