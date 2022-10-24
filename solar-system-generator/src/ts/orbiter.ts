import * as THREE from 'three';
import { Utils } from './utils';
import { THREEUtils } from './utils.three';

export class Orbiter {
    constructor(public threeObject: THREE.Object3D, public orbitCurve: THREE.EllipseCurve) {}

    private currentAngle = 0;
    public angVelDegPerSecond = 0;

    public set initialAngle(value: number) {
        this.currentAngle = value;
    }

    public updatePosition(elapsedSeconds: number) {
        this.currentAngle += this.angVelDegPerSecond * elapsedSeconds;
        this.currentAngle = Utils.ClampDegrees(this.currentAngle);

        const objectPosition = new THREE.Vector2();
        this.orbitCurve.getPointAt(this.currentAngle / 360, objectPosition);
        THREEUtils.SetPosition(this.threeObject, objectPosition.x, objectPosition.y, 0);
    }
}
