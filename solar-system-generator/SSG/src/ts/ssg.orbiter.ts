import * as THREE from 'three';
import { Utils } from './ssg.utils';

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
        Utils.setPosition(this.threeObject, objectPosition.x, objectPosition.y, 0);
    }
}