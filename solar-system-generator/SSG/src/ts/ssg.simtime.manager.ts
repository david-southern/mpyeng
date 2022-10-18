import _ from 'lodash';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls'

import blackBackground from '../images/black.png';

import * as PP from 'postprocessing';

import { CelestialObject } from './celestial-object';
// import { OrbitControls } from './OrbitControls';
import { Logger, SSGSystemFilter } from './ssg.logger';
import { GRID_TYPE_RECTANGULAR, GRID_TYPE_NONE, GRID_TYPE_POLAR, SSGOldSettings, EmptySettings } from './ssg.zzz.settings';
import { Utils } from './utils';
import { Orbiter } from './ssg.orbiter';
import { SettingsManager } from './ssg.settings.manager';
import { SSGSettings } from './ssg.settings';
import { firstValueFrom } from 'rxjs';

const DEFAULT_FOV = 70;
const DEFAULT_ASPECT = 1.61;
const DEFAULT_ORBITAL_COLOR = '#999999';

export class SSGSimTimeManager {
    private static _SimTimeManager = new SSGSimTimeManager();
    public static get SimTimeManager() {
        return SSGSimTimeManager._SimTimeManager;
    }

    // Make the constructor private to signal that SSGSimTimeManager is a singleton
    private constructor() {
    }

    private settings: SSGSettings = SSGSettings.GlobalSettings;

    private actualStartTime: number = null!;
    private lastActualTime: number = null!;
    private _actualTime: number = null!;
    public get ActualTime() {
        return this._actualTime;
    }

    private _actualElapsedSeconds: number = null!;
    public get LastFrameActualElapsedSeconds() {
        return this._actualElapsedSeconds;
    }

    private _simTime: number = null!;
    public get SimTime() {
        return this._simTime;
    }

    private _simElapsedSeconds: number = null!;
    public get LastFrameSimElapsedSeconds() {
        return this._simElapsedSeconds;
    }

    private showTimeDiags = false;
    private nextTimeDiags = 0;

    public async UpdateSimTime(actualMillis: number) {
        this._actualTime = actualMillis / 1000;

        this.checkInitialization();

        let speedScale = 0;

        if (Utils.FloatNE(this.settings.AnimationSpeed.value, 0)) {
            speedScale = await firstValueFrom(this.settings.AnimationTimeScale$);
        }

        const actualSimTime = (this._actualTime - this.actualStartTime);
        this._actualElapsedSeconds = this._actualTime - this.lastActualTime;
        this.lastActualTime = this._actualTime;
        this._simElapsedSeconds = this._actualElapsedSeconds * speedScale;
        this._simTime += this._simElapsedSeconds;

        if (this.showTimeDiags && Date.now() > this.nextTimeDiags) {
            let diagsString = `Anim: SpeedScale: ${speedScale}`;
            diagsString += ` (${await firstValueFrom(this.settings.AnimationTimeScaleHuman$)})`;
            diagsString += `, Clock: Actual: ${Utils.humanTime(actualSimTime)}, Sim: ${Utils.humanTime(this._simTime)}`;
            diagsString += `, Frame: Actual: ${Utils.humanTime(this._actualElapsedSeconds)}, Sim: ${Utils.humanTime(this._simElapsedSeconds)}`;
            Logger.info(SSGSystemFilter.TimingDiagnostics, diagsString);
            this.nextTimeDiags = Date.now() + 1000;
        }
    }

    private checkInitialization() {
        if (this.actualStartTime === undefined) {
            this.actualStartTime = this._actualTime;
        }

        if (this.lastActualTime === undefined) {
            this.lastActualTime = this._actualTime;
        }

        if (this._simTime === undefined) {
            this._simTime = 0;
        }
    }
}
