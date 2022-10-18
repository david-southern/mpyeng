import * as THREE from 'three';
import { BackgroundImageData, BackgroundImages } from './ssg.settings.backgrounds';
import { Utils } from './utils';

export const GRID_TYPE_RECTANGULAR = 'Rectangular';
export const GRID_TYPE_POLAR = 'Polar';
export const GRID_TYPE_NONE = 'None';

export class SSGOldSettings {
    public AmbientLightColor = "#404040";
    public AmbientLightIntensity = 1;

    public OrbitalColor = "#00ffff";

    public IncludeDirectionalLight = false;
    public DirectionalLightColor = "#000000";
    public DirectionalLightIntensity = 0;
    public DirectionalLightPosition = new THREE.Vector3(0, 0, 0);

    public FieldOfViewDegrees = 10;

    public ViewAngleXDegrees = -80;
    public ViewAngleYDegrees = 0;
    public ViewAngleZDegrees = 0;

    public Animate = true;
    public AnimationSpeed = 0;

    public MaxAnimationSpeedScale = 10e8;

    public get AnimationTimeScale(): number {
        const clampedSpeed = Utils.clamp(this.AnimationSpeed, -1, 1);

        // Use a quadratic easing function, but allow the sign of the clampedSpeed through
        return clampedSpeed * Math.abs(clampedSpeed) * this.MaxAnimationSpeedScale;
    }

    // A human-readable representation of the AnimationTimeScale
    public get AnimationTimeScaleHuman(): string {
        return Utils.FloatEQ(this.AnimationTimeScale, 0) ? "paused" : `${Utils.humanTime(this.AnimationTimeScale)} per second`;
    }

    public GridType = GRID_TYPE_POLAR;
    public GridSizeFactor = 1.1;
    public GridMajorDivisions = 4;
    public GridMajorColor = '#004000';
    public GridMinorDivisions = 36;
    public GridMinorColor = '#003000';

    public PlanetScale = 1500;
    public StarScale = 50;

    public Zoom = 1;

    public ResetOrbitControls = false;
    public DownloadImage = false;
    public LookAt?: string;

    public BackgroundImage?: BackgroundImageData;

    constructor(partialObj: Partial<SSGOldSettings>) {
        if (partialObj) {
            Object.assign(this, partialObj);
        }
    }
};

// Export this so I don't have to null=check things everywhere
export const EmptySettings = new SSGOldSettings({
    BackgroundImage: BackgroundImages[4]
});