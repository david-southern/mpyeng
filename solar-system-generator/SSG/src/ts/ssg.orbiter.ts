import * as THREE from 'three';
import { Utils } from './utils';
import { THREEUtils } from './utils.three';

export class Orbiter {
    constructor(
        public threeObject: THREE.Object3D,
        public orbitCurve: THREE.EllipseCurve,
        public initialAngle: number,
        public angVelDegPerSecond: number,
    ) {
        this.currentAngle = initialAngle;
    }

    private currentAngle: number;

    public updatePosition(elapsedSeconds: number) {
        this.currentAngle += (this.angVelDegPerSecond * elapsedSeconds);
        this.currentAngle = Utils.clampDegrees(this.currentAngle);

        const objectPosition = new THREE.Vector2();
        this.orbitCurve.getPointAt(this.currentAngle / 360, objectPosition);
        THREEUtils.setPosition(this.threeObject, objectPosition.x, objectPosition.y, 0);
    }
}