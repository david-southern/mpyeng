import { BehaviorSubject } from 'rxjs';
import * as THREE from 'three';
import { Utils } from './utils';

export const COLOR_NONE = 'none';

export class CelestialObject {
    ParentObject?: CelestialObject;
    ParentName?: string;
    ChildObjects: CelestialObject[] = [];
    ChildDepth = 0;
    SystemOrder = 0;

    public Name$ = new BehaviorSubject(COLOR_NONE);
    public get Name() {
        return this.Name$.value;
    }
    public set Name(value) {
        this.Name$.next(value);
    }

    public IsSelected$ = new BehaviorSubject(false);
    public get IsSelected() {
        return this.IsSelected$.value;
    }
    public set IsSelected(value) {
        this.IsSelected$.next(value);
    }

    public IsStar$ = new BehaviorSubject(false);
    public get IsStar() {
        return this.IsStar$.value;
    }
    public set IsStar(value) {
        this.IsStar$.next(value);
    }

    public OrbitalSemiMajorAxis$ = new BehaviorSubject(0);
    public get OrbitalSemiMajorAxis() {
        return this.OrbitalSemiMajorAxis$.value;
    }
    public set OrbitalSemiMajorAxis(value) {
        this.OrbitalSemiMajorAxis$.next(value);
    }

    public OrbitalSemiMinorAxis$ = new BehaviorSubject(0);
    public get OrbitalSemiMinorAxis() {
        return this.OrbitalSemiMinorAxis$.value;
    }
    public set OrbitalSemiMinorAxis(value) {
        this.OrbitalSemiMinorAxis$.next(value);
    }

    public OrbitalPerigee$ = new BehaviorSubject(0);
    public get OrbitalPerigee() {
        return this.OrbitalPerigee$.value;
    }
    public set OrbitalPerigee(value) {
        this.OrbitalPerigee$.next(value);
    }

    public OrbitalVelocity$ = new BehaviorSubject(0);
    public get OrbitalVelocity() {
        return this.OrbitalVelocity$.value;
    }
    public set OrbitalVelocity(value) {
        this.OrbitalVelocity$.next(value);
    }

    public InitialOrbitalAngle$ = new BehaviorSubject(0);
    public get InitialOrbitalAngle() {
        return this.InitialOrbitalAngle$.value;
    }
    public set InitialOrbitalAngle(value) {
        this.InitialOrbitalAngle$.next(value);
    }

    public ObjectRadius$ = new BehaviorSubject(0);
    public get ObjectRadius() {
        return this.ObjectRadius$.value;
    }
    public set ObjectRadius(value) {
        this.ObjectRadius$.next(value);
    }

    public ObjectColor$ = new BehaviorSubject(COLOR_NONE);
    public get ObjectColor() {
        return this.ObjectColor$.value;
    }
    public set ObjectColor(value) {
        this.ObjectColor$.next(value);
    }

    public OrbitColor$ = new BehaviorSubject(COLOR_NONE);
    public get OrbitColor() {
        return this.OrbitColor$.value;
    }
    public set OrbitColor(value) {
        this.OrbitColor$.next(value);
    }

    public OrbitalInclination$ = new BehaviorSubject(0);
    public get OrbitalInclination() {
        return this.OrbitalInclination$.value;
    }
    public set OrbitalInclination(value) {
        this.OrbitalInclination$.next(Utils.Clamp(value, -90, 90));
    }

    public PhaseAngle$ = new BehaviorSubject(0);
    public get PhaseAngle() {
        return this.PhaseAngle$.value;
    }
    public set PhaseAngle(value) {
        this.PhaseAngle$.next(Utils.ClampDegrees(value));
    }

    public RingInnerRadius$ = new BehaviorSubject(0);
    public get RingInnerRadius() {
        return this.RingInnerRadius$.value;
    }
    public set RingInnerRadius(value) {
        this.RingInnerRadius$.next(value);
    }

    public RingWidth$ = new BehaviorSubject(0);
    public get RingWidth() {
        return this.RingWidth$.value;
    }
    public set RingWidth(value) {
        this.RingWidth$.next(value);
    }

    public RingDensity$ = new BehaviorSubject(0);
    public get RingDensity() {
        return this.RingDensity$.value;
    }
    public set RingDensity(value) {
        this.RingDensity$.next(value);
    }

    public RingColor$ = new BehaviorSubject(COLOR_NONE);
    public get RingColor() {
        return this.RingColor$.value;
    }
    public set RingColor(value) {
        this.RingColor$.next(value);
    }

    Obj3D?: THREE.Object3D;

    constructor(partialObj?: Partial<CelestialObject>) {
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
