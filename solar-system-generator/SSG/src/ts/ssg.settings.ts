import { BehaviorSubject, combineLatest, map } from 'rxjs';
import * as THREE from 'three';
import { DefaultBackgroundImage } from './ssg.settings.backgrounds';
import { Utils } from './utils';

export const GRID_TYPE_RECTANGULAR = 'Rectangular';
export const GRID_TYPE_POLAR = 'Polar';
export const GRID_TYPE_NONE = 'None';

export class SSGSettings {
    private static _GlobalSettings = new SSGSettings();
    public static get GlobalSettings() {
        return SSGSettings._GlobalSettings;
    }

    // Make the constructor private to signal that SSGRxSettings is a singleton
    private constructor() {
    }

    public AmbientLightColorSubject = new BehaviorSubject("#404040");
    public AmbientLightIntensity = new BehaviorSubject(1);

    public OrbitalColor = new BehaviorSubject("#00ffff");

    public IncludeDirectionalLight = new BehaviorSubject(false);
    public DirectionalLightColor = new BehaviorSubject("#000000");
    public DirectionalLightIntensity = new BehaviorSubject(0);
    public DirectionalLightPosition = new BehaviorSubject(new THREE.Vector3(0, 0, 0));

    public FieldOfViewDegrees = new BehaviorSubject(10);

    public ViewAngleXDegrees = new BehaviorSubject(-80);
    public ViewAngleYDegrees = new BehaviorSubject(0);
    public ViewAngleZDegrees = new BehaviorSubject(0);

    public Animate = new BehaviorSubject(true);
    public AnimationSpeed = new BehaviorSubject(0.00003);

    public MaxAnimationSpeedScale = new BehaviorSubject(10e8);

    public AnimationTimeScale$ = combineLatest([this.AnimationSpeed, this.MaxAnimationSpeedScale]).pipe(
        map(([animSpeed, maxSpeedScale]) => {
            const clampedSpeed = Utils.clamp(animSpeed, -1, 1);
            // Use a quadratic easing function, but allow the sign of the clampedSpeed through
            return clampedSpeed * Math.abs(clampedSpeed) * maxSpeedScale;
        })
    );

    public AnimationTimeScaleHuman$ = this.AnimationTimeScale$.pipe(
        map(timeScale => Utils.FloatEQ(timeScale, 0) ? "paused" : `${Utils.humanTime(timeScale)} per second`)
    );

    public GridType = new BehaviorSubject(GRID_TYPE_POLAR);
    public GridSizeFactor = new BehaviorSubject(1.1);
    public GridMajorDivisions = new BehaviorSubject(4);
    public GridMajorColor = new BehaviorSubject('#004000');
    public GridMinorDivisions = new BehaviorSubject(36);
    public GridMinorColor = new BehaviorSubject('#003000');

    public PlanetScale = new BehaviorSubject(1500);
    public StarScale = new BehaviorSubject(50);

    public Zoom = new BehaviorSubject(1);

    public ResetOrbitControls = new BehaviorSubject(false);
    public DownloadImage = new BehaviorSubject(false);
    public LookAt = new BehaviorSubject<string | undefined>(undefined);

    public BackgroundImage = new BehaviorSubject(DefaultBackgroundImage);

    updateFromJson(partialObj?: Partial<SSGSettings>) {
        if (partialObj) {
            Object.assign(this, partialObj);
        }
    }
}
