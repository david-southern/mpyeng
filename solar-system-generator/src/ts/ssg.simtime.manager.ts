import _ from "lodash";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls";

import blackBackground from "../images/black.png";

import * as PP from "postprocessing";

import { CelestialObject } from "./celestial-object";
// import { OrbitControls } from './OrbitControls';
import { Logger, SSGSystemFilter } from "./ssg.logger";
import { GRID_TYPE_RECTANGULAR, GRID_TYPE_NONE, GRID_TYPE_POLAR, SSGOldSettings, EmptySettings } from "./ssg.zzz.settings";
import { Utils } from "./utils";
import { Orbiter } from "./ssg.orbiter";
import { SettingsManager } from "./ssg.settings.manager";
import { GlobalSettings, SSGSettings } from "./ssg.settings";
import { firstValueFrom, Subject } from "rxjs";

const DEFAULT_FOV = 70;
const DEFAULT_ASPECT = 1.61;
const DEFAULT_ORBITAL_COLOR = "#999999";

export class SSGSimTimeManager {
    private static _Instance = new SSGSimTimeManager();
    public static get Instance() {
        return SSGSimTimeManager._Instance;
    }

    private TickSubject = new Subject<number>();
    public Tick$ = this.TickSubject.asObservable();

    // Make the constructor private to signal that SSGSimTimeManager is a singleton
    private constructor() {
    }

    private actualStartTime = 0;
    private lastActualTime = 0;

    private _actualTime = 0;
    public get ActualTime() {
        return this._actualTime;
    }

    private _actualElapsedSeconds = 0;
    public get LastFrameActualElapsedSeconds() {
        return this._actualElapsedSeconds;
    }

    private _simTime = 0;
    public get SimTime() {
        return this._simTime;
    }

    private _simElapsedSeconds = 0;
    public get LastFrameSimElapsedSeconds() {
        return this._simElapsedSeconds;
    }

    private ANIMATION_DIAGS_FREQ_MS = 5000;
    private SHOW_DIAGS = false;
    private nextDiags = 0;

    public async UpdateSimTime(actualMillis: number) {
        this._actualTime = actualMillis / 1000;

        let speedScale = 0;

        if (Utils.FloatNE(GlobalSettings.AnimationSpeed, 0)) {
            speedScale = await firstValueFrom(GlobalSettings.AnimationTimeScale$);
        }

        const actualSimTime = (this._actualTime - this.actualStartTime);
        this._actualElapsedSeconds = this._actualTime - this.lastActualTime;
        this.lastActualTime = this._actualTime;
        this._simElapsedSeconds = this._actualElapsedSeconds * speedScale;
        this._simTime += this._simElapsedSeconds;

        if (this.SHOW_DIAGS && Date.now() > this.nextDiags) {
            const diagScale = await firstValueFrom(GlobalSettings.AnimationTimeScaleHuman$);
            Logger.info(SSGSystemFilter.TimingDiagnostics, `SimTimeMgr: Time Scale: ${diagScale}`);
            Logger.info(SSGSystemFilter.TimingDiagnostics, `  Clock: Actual: ${Utils.HumanTime(this._actualTime)}`);
            Logger.info(SSGSystemFilter.TimingDiagnostics, `            Sim: ${Utils.HumanTime(this._simTime)}`);
            Logger.info(SSGSystemFilter.TimingDiagnostics, `  Frame: Actual: ${Utils.HumanTime(this._actualElapsedSeconds)}`);
            Logger.info(SSGSystemFilter.TimingDiagnostics, `            Sim: ${Utils.HumanTime(this._simElapsedSeconds)}`);
            this.nextDiags = Date.now() + this.ANIMATION_DIAGS_FREQ_MS;
        }

        this.TickSubject.next(actualMillis);
    }
}

export const SimTimeManager = SSGSimTimeManager.Instance;