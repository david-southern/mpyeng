import { Logger, SSGSystemFilter } from './logger';
import { Utils } from './utils';
import { GlobalSettings } from './settings';
import { firstValueFrom, Subject } from 'rxjs';

export class SSGSimTimeManager {
    private static _Instance = new SSGSimTimeManager();
    public static get Instance() {
        return SSGSimTimeManager._Instance;
    }

    private TickSubject = new Subject<number>();
    public Tick$ = this.TickSubject.asObservable();

    private constructor() {
        // Make the constructor private to signal that SSGSimTimeManager is a singleton
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
            speedScale = await firstValueFrom(
                GlobalSettings.AnimationTimeScale$
            );
        }

        this._actualElapsedSeconds = this._actualTime - this.lastActualTime;
        this.lastActualTime = this._actualTime;
        this._simElapsedSeconds = this._actualElapsedSeconds * speedScale;
        this._simTime += this._simElapsedSeconds;

        if (this.SHOW_DIAGS && Date.now() > this.nextDiags) {
            const diagScale = await firstValueFrom(
                GlobalSettings.AnimationTimeScaleHuman$
            );
            Logger.info(
                SSGSystemFilter.TimingDiagnostics,
                `SimTimeMgr: Time Scale: ${diagScale}`
            );
            Logger.info(
                SSGSystemFilter.TimingDiagnostics,
                `  Clock: Actual: ${Utils.HumanTime(this._actualTime)}`
            );
            Logger.info(
                SSGSystemFilter.TimingDiagnostics,
                `            Sim: ${Utils.HumanTime(this._simTime)}`
            );
            Logger.info(
                SSGSystemFilter.TimingDiagnostics,
                `  Frame: Actual: ${Utils.HumanTime(
                    this._actualElapsedSeconds
                )}`
            );
            Logger.info(
                SSGSystemFilter.TimingDiagnostics,
                `            Sim: ${Utils.HumanTime(this._simElapsedSeconds)}`
            );
            this.nextDiags = Date.now() + this.ANIMATION_DIAGS_FREQ_MS;
        }

        this.TickSubject.next(actualMillis);
    }
}

export const SimTimeManager = SSGSimTimeManager.Instance;
