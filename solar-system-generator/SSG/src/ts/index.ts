import * as _ from 'lodash';
import { CelestialObject } from './celestial-object';
import { Sol } from './solar-system';
import { Logger, SSGSystemFilter } from './ssg.logger';

import { SSGRenderer } from "./ssg.renderer";
import { EmptySettings } from './ssg.settings';

export const Renderer = new SSGRenderer();

function LoadPremade(premade: CelestialObject)
{
    const system = _.cloneDeep(premade);
    Logger.info(SSGSystemFilter.Always, `Loading premade solar system: ${system.Name}`);
    Renderer.render(system, EmptySettings);
}

Renderer.initialize("system-canvas", "system-time");
LoadPremade(Sol)
