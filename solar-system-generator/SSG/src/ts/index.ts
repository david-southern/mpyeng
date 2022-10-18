import * as _ from 'lodash';
import { CelestialObject } from './celestial-object';
import { Sol } from './solar-system';
import { Logger, SSGSystemFilter } from './ssg.logger';
import { SSGRenderer } from './ssg.renderer';
import GUI from 'lil-gui';

import { EmptySettings } from './ssg.zzz.settings';
import { SSGSettings } from './ssg.settings';

export const Renderer = new SSGRenderer("system-canvas", "system-time");

function LoadPremade(premade: CelestialObject) {
    const system = _.cloneDeep(premade);
    Logger.info(SSGSystemFilter.Always, `Loading premade solar system: ${system.Name}`);
}

// LoadPremade(Sol)

SSGSettings.GlobalSettings.MaxAnimationSpeedScale.next(10);

class Controller {
    private m_speed = 0.0003;
    public get speed():number {
        return this.m_speed;
    }
    public set speed(value: number) {
        this.m_speed = value;
        SSGSettings.GlobalSettings.AnimationSpeed.next(value);
    }

    public pauseAnimation() {
        alert('hi');
    }
}

const controller = new Controller();

const gui = new GUI();

gui.add(controller, 'speed', -1, 1, 0.0001);
gui.add(controller, 'pauseAnimation');
