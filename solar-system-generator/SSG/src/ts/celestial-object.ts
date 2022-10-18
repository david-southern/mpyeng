import * as THREE from 'three';
import { Utils } from './utils';

export class CelestialObject {
    Name?: string;

    ParentObject?: CelestialObject;
    ParentName?: string;
    ChildObjects: CelestialObject[] = [];
    ChildDepth: number = 0;
    SystemOrder: number = 0;

    IsSelected: boolean = false;

    IsStar: boolean = false;
    OrbitalSemiMajorAxis: number = 0;
    OrbitalSemiMinorAxis: number = 0;
    OrbitalPerigee: number = 0;
    OrbitalVelocity: number = 0;
    InitialOrbitalAngle: number = 0;
    ObjectRadius: number = 0;
    ObjectColor: string = null!;
    OrbitColor: string = null!;

    private m_OrbitalInclination: number = 0;
    get OrbitalInclination(): number {
        return this.m_OrbitalInclination;
    }
    set OrbitalInclination(value: number) {
        this.m_OrbitalInclination = Utils.clamp(value, -90, 90);
    }

    private m_PhaseAngle: number = 0;
    get PhaseAngle(): number {
        return this.m_PhaseAngle;
    }
    set PhaseAngle(value: number) {
        this.m_PhaseAngle = Utils.clampDegrees(value);
    }

    RingInnerRadius?: number;
    RingWidth?: number;
    RingDensity?: number;
    RingColor?: string;

    Obj3D?: THREE.Object3D;

    constructor(partialObj: Partial<CelestialObject>) {
        if (partialObj) {
            Object.assign(this, partialObj);
            this.ChildObjects = [];

            if (partialObj.ChildObjects && partialObj.ChildObjects.length > 0) {
                for (const childPartial of partialObj.ChildObjects) {
                    if (!(childPartial instanceof CelestialObject)) {
                        const childObject = new CelestialObject(childPartial);
                        childObject.ParentObject = this;
                        childObject.ParentName = this.Name;
                        childObject.SystemOrder = this.ChildObjects.length;
                        this.ChildObjects.push(childObject);
                    }
                }
            }

            if (this.ParentObject) {
                this.SystemOrder = this.ParentObject.ChildObjects.length;
                this.ParentObject.ChildObjects.push(this);
                this.ParentName = this.ParentObject.Name;
                this.ChildDepth = this.ParentObject.ChildDepth + 1;
            } else {
                this.ChildDepth = 0;
            }
        }
    }
}
