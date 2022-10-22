import { BehaviorSubject, combineLatest, map } from "rxjs";
import * as THREE from "three";
import { CelestialObject } from "./celestial-object";
import { DefaultBackgroundImage } from "./ssg.settings.backgrounds";
import { Utils } from "./utils";

export const GRID_TYPE_RECTANGULAR = "Rectangular";
export const GRID_TYPE_POLAR = "Polar";
export const GRID_TYPE_NONE = "None";

export class SSGSettings {
    private static _Instance = new SSGSettings();
    public static get Instance() {
        return SSGSettings._Instance;
    }

    // Make the constructor private to signal that SSGRxSettings is a singleton
    private constructor() {
    }

    public SystemRoot = new BehaviorSubject<CelestialObject | undefined>(undefined);
    public SystemRoot$ = this.SystemRoot.asObservable();

    public AmbientLightColorSubject$ = new BehaviorSubject("#404040");
    public get AmbientLightColorSubject() {
        return this.AmbientLightColorSubject$.value;
    } public set AmbientLightColorSubject(value) {
        this.AmbientLightColorSubject$.next(value);
    }

    public AmbientLightIntensity$ = new BehaviorSubject(1);
    public get AmbientLightIntensity() {
        return this.AmbientLightIntensity$.value;
    } public set AmbientLightIntensity(value) {
        this.AmbientLightIntensity$.next(value);
    }

    public OrbitalColor$ = new BehaviorSubject("#00ffff");
    public get OrbitalColor() {
        return this.OrbitalColor$.value;
    } public set OrbitalColor(value) {
        this.OrbitalColor$.next(value);
    }

    public IncludeDirectionalLight$ = new BehaviorSubject(false);
    public get IncludeDirectionalLight() {
        return this.IncludeDirectionalLight$.value;
    } public set IncludeDirectionalLight(value) {
        this.IncludeDirectionalLight$.next(value);
    }

    public DirectionalLightColor$ = new BehaviorSubject("#000000");
    public get DirectionalLightColor() {
        return this.DirectionalLightColor$.value;
    } public set DirectionalLightColor(value) {
        this.DirectionalLightColor$.next(value);
    }

    public DirectionalLightIntensity$ = new BehaviorSubject(0);
    public get DirectionalLightIntensity() {
        return this.DirectionalLightIntensity$.value;
    } public set DirectionalLightIntensity(value) {
        this.DirectionalLightIntensity$.next(value);
    }

    public DirectionalLightPosition$ = new BehaviorSubject(new THREE.Vector3(0, 0, 0));
    public get DirectionalLightPosition() {
        return this.DirectionalLightPosition$.value;
    } public set DirectionalLightPosition(value) {
        this.DirectionalLightPosition$.next(value);
    }

    public FieldOfViewDegrees$ = new BehaviorSubject(10);
    public get FieldOfViewDegrees() {
        return this.FieldOfViewDegrees$.value;
    } public set FieldOfViewDegrees(value) {
        this.FieldOfViewDegrees$.next(value);
    }

    public ViewAngleXDegrees$ = new BehaviorSubject(-80);
    public get ViewAngleXDegrees() {
        return this.ViewAngleXDegrees$.value;
    } public set ViewAngleXDegrees(value) {
        this.ViewAngleXDegrees$.next(value);
    }

    public ViewAngleYDegrees$ = new BehaviorSubject(0);
    public get ViewAngleYDegrees() {
        return this.ViewAngleYDegrees$.value;
    } public set ViewAngleYDegrees(value) {
        this.ViewAngleYDegrees$.next(value);
    }

    public ViewAngleZDegrees$ = new BehaviorSubject(0);
    public get ViewAngleZDegrees() {
        return this.ViewAngleZDegrees$.value;
    } public set ViewAngleZDegrees(value) {
        this.ViewAngleZDegrees$.next(value);
    }


    public Animate$ = new BehaviorSubject(true);
    public get Animate() {
        return this.Animate$.value;
    } public set Animate(value) {
        this.Animate$.next(value);
    }

    public AnimationSpeed$ = new BehaviorSubject(0.00003);
    public get AnimationSpeed() {
        return this.AnimationSpeed$.value;
    } public set AnimationSpeed(value) {
        this.AnimationSpeed$.next(value);
    }

    public MaxAnimationSpeedScale$ = new BehaviorSubject(10e8);
    public get MaxAnimationSpeedScale() {
        return this.MaxAnimationSpeedScale$.value;
    } public set MaxAnimationSpeedScale(value) {
        this.MaxAnimationSpeedScale$.next(value);
    }

    public AnimationTimeScale$ = combineLatest([this.AnimationSpeed$, this.MaxAnimationSpeedScale$]).pipe(
        map(([animSpeed, maxSpeedScale]) => {
            const clampedSpeed = Utils.Clamp(animSpeed, -1, 1);
            // Use a quadratic easing function, but allow the sign of the clampedSpeed through
            return clampedSpeed * Math.abs(clampedSpeed) * maxSpeedScale;
        })
    );

    public AnimationTimeScaleHuman$ = this.AnimationTimeScale$.pipe(
        map(timeScale => Utils.FloatEQ(timeScale, 0) ? "paused" : `${Utils.HumanTime(timeScale)} per second`)
    );

    public GridType$ = new BehaviorSubject(GRID_TYPE_POLAR);
    public get GridType() {
        return this.GridType$.value;
    } public set GridType(value) {
        this.GridType$.next(value);
    }

    public GridSizeFactor$ = new BehaviorSubject(1.1);
    public get GridSizeFactor() {
        return this.GridSizeFactor$.value;
    } public set GridSizeFactor(value) {
        this.GridSizeFactor$.next(value);
    }

    public GridMajorDivisions$ = new BehaviorSubject(4);
    public get GridMajorDivisions() {
        return this.GridMajorDivisions$.value;
    } public set GridMajorDivisions(value) {
        this.GridMajorDivisions$.next(value);
    }

    public GridMajorColor$ = new BehaviorSubject("#004000");
    public get GridMajorColor() {
        return this.GridMajorColor$.value;
    } public set GridMajorColor(value) {
        this.GridMajorColor$.next(value);
    }

    public GridMinorDivisions$ = new BehaviorSubject(36);
    public get GridMinorDivisions() {
        return this.GridMinorDivisions$.value;
    } public set GridMinorDivisions(value) {
        this.GridMinorDivisions$.next(value);
    }

    public GridMinorColor$ = new BehaviorSubject("#003000");
    public get GridMinorColor() {
        return this.GridMinorColor$.value;
    } public set GridMinorColor(value) {
        this.GridMinorColor$.next(value);
    }

    public PlanetScale$ = new BehaviorSubject(1500);
    public get PlanetScale() {
        return this.PlanetScale$.value;
    } public set PlanetScale(value) {
        this.PlanetScale$.next(value);
    }

    public StarScale$ = new BehaviorSubject(50);
    public get StarScale() {
        return this.StarScale$.value;
    } public set StarScale(value) {
        this.StarScale$.next(value);
    }

    public Zoom$ = new BehaviorSubject(1);
    public get Zoom() {
        return this.Zoom$.value;
    } public set Zoom(value) {
        this.Zoom$.next(value);
    }

    public ResetOrbitControls$ = new BehaviorSubject(false);
    public get ResetOrbitControls() {
        return this.ResetOrbitControls$.value;
    } public set ResetOrbitControls(value) {
        this.ResetOrbitControls$.next(value);
    }

    public DownloadImage$ = new BehaviorSubject(false);
    public get DownloadImage() {
        return this.DownloadImage$.value;
    } public set DownloadImage(value) {
        this.DownloadImage$.next(value);
    }

    public LookAt$ = new BehaviorSubject<string | undefined>(undefined);
    public get LookAt() {
        return this.LookAt$.value;
    } public set LookAt(value) {
        this.LookAt$.next(value);
    }

    public BackgroundImage$ = new BehaviorSubject(DefaultBackgroundImage);
    public get BackgroundImage() {
        return this.BackgroundImage$.value;
    } public set BackgroundImage(value) {
        this.BackgroundImage$.next(value);
    }

    updateFromJson(partialObj?: Partial<SSGSettings>) {
        if (partialObj) {
            Object.assign(this, partialObj);
        }
    }
}

export const GlobalSettings = SSGSettings.Instance;