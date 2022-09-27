import * as THREE from 'three';

import { CelestialObject } from './celestial-object';
import { Utils } from './ssg.utils';

export const GRID_TYPE_GRID = 'Grid';
export const GRID_TYPE_POLAR = 'Polar';
export const GRID_TYPE_NONE = 'None';

export class SSGSettings {
    public AmbientLightColor = "#404040";
    public OrbitalColor = "#ffff00";
    public IncludeDirectionalLight = false;

    // We want a perspective view so that we get a sense of 'nearer/farther', but we also want our planets to be apparent
    // spheres.  If the camera is too close, then we get fisheye distortion of the scene.  Instead put the camera way far
    // away, and use a very narrow FOV to get the right look.
    public FieldOfViewDegrees = 10;

    public ViewCameraDistance = 9000;
    public ViewAngleXDegrees = -80;
    public ViewAngleYDegrees = 0;
    public ViewAngleZDegrees = 0;

    public AnimateZSpeed = 0.001;

    public GridType = GRID_TYPE_NONE;

    /**
     * The max visible width of the renderer's view frustrum.
     */
    public WorldViewWidth = 1200;

    /**
     * The amount to scale the final solar system representation so it is visible in the renderer's view frustrum.
     */
    public SystemScale = 1;

    /**
     * The amount to scale planets over their 'actual' size so that they are visible on an orbital scale.
     */
    public PlanetScale = 50;

    /**
     * The amount to scale planets over their 'actual' size so that they are visible on an orbital scale.
     */
    public StarScale = 50;

    public Zoom = 1;
};

const DefaultSSGSettings = new SSGSettings();

export class SSGRenderer {
    private ssgSettings: SSGSettings = null!;

    private canvasElement: HTMLElement = null!;
    private canvasWidth: number = null!;
    private canvasHeight: number = null!;

    private scene: THREE.Scene = null!;
    private camera: THREE.PerspectiveCamera = null!;
    private renderer = new THREE.WebGLRenderer();
    private viewZRot: THREE.Group = null!;
    private viewYRot: THREE.Group = null!;
    private viewXRot: THREE.Group = null!;

    private solarSystem: CelestialObject = null!;
    private animating = false;

    public initialize(canvasDivId: string, settings?: SSGSettings) {
        const checkCanvas = document.getElementById(canvasDivId);

        if (!checkCanvas) {
            console.error(`SSG Canvas Div Id '${canvasDivId}' did not select any DOM element`);
            return;
        }

        this.ssgSettings = settings ?? DefaultSSGSettings;

        this.canvasElement = checkCanvas;

        this.canvasWidth = this.canvasElement.offsetWidth;
        this.canvasHeight = this.canvasElement.offsetHeight;
        const canvasAspect = this.canvasWidth / this.canvasHeight;

        var rect = this.canvasElement.getBoundingClientRect();

        console.log(`Initializing SSG render with:`);
        console.log(`    window @(${rect.top}, ${rect.left}), size: (${this.canvasWidth} x ${this.canvasHeight}), aspect: ${canvasAspect}`);
        console.log(`    fov ${this.ssgSettings.FieldOfViewDegrees}, near: ${this.ssgSettings.ViewCameraDistance / 100}, far: ${this.ssgSettings.ViewCameraDistance * 2}`);

        this.camera = new THREE.PerspectiveCamera(this.ssgSettings.FieldOfViewDegrees, canvasAspect,
            this.ssgSettings.ViewCameraDistance / 100, this.ssgSettings.ViewCameraDistance * 2);

        this.renderer.setSize(this.canvasWidth, this.canvasHeight);
        this.canvasElement.appendChild(this.renderer.domElement);
    }

    public render(solarSystemJson: string, settingsJson?: string) {
        const solarSystemPartial = JSON.parse(solarSystemJson);

        this.solarSystem = new CelestialObject(solarSystemPartial);

        this.ssgSettings = DefaultSSGSettings;

        if (settingsJson) {
            this.ssgSettings = JSON.parse(settingsJson);
        }

        console.log("Render Solar System: ", this.solarSystem);
        console.log("  with settings: ", this.ssgSettings);

        this.scene = new THREE.Scene();
        this.scene.add(new THREE.AmbientLight(this.ssgSettings.AmbientLightColor));

        if (this.ssgSettings.IncludeDirectionalLight) {
            const directionalLight = new THREE.DirectionalLight('#ffffff', 1);
            Utils.setPosition(directionalLight, 1, 1, 0);
            this.scene.add(directionalLight);
        }

        const testSystem = false;

        let systemGroup;

        if (testSystem) {
            console.log(`Building test scene`);
            systemGroup = this.buildTestScene();
        }
        else {
            const systemRadius = this.calculateSystemRadius(this.solarSystem);
            console.log(`Max systemRadius: ${systemRadius}`);

            this.ssgSettings.SystemScale = this.ssgSettings.WorldViewWidth / systemRadius;

            console.log(`SystemScale factor: ${this.ssgSettings.SystemScale}`);

            systemGroup = this.buildSolarSystem(this.solarSystem);
        }

        // It is easier to rotate the top-level sceneGroup than to try and reposition the camera. Unfortunately I don't
        // understand 3D math well enough to get the rotation I want in one go, but separate rotations seem to work well
        // enough.
        this.viewZRot = new THREE.Group();
        this.viewZRot.add(systemGroup);
        this.viewZRot.rotation.z = Utils.degreesToRadians(this.ssgSettings.ViewAngleZDegrees);

        this.viewYRot = new THREE.Group();
        this.viewYRot.add(this.viewZRot);
        this.viewYRot.rotation.y = Utils.degreesToRadians(this.ssgSettings.ViewAngleYDegrees);

        this.viewXRot = new THREE.Group();
        this.viewXRot.add(this.viewYRot);
        this.viewXRot.rotation.x = Utils.degreesToRadians(this.ssgSettings.ViewAngleXDegrees);

        this.viewXRot.scale.x = this.ssgSettings.Zoom;
        this.viewXRot.scale.y = this.ssgSettings.Zoom;
        this.viewXRot.scale.z = this.ssgSettings.Zoom;

        this.scene.add(this.viewXRot);

        this.camera.position.z = this.ssgSettings.ViewCameraDistance;

        this.updateRender();
    }

    private updateRender() {
        //this.startAnimation(() => {
        //    this.stopAnimation();
        //});
        this.startAnimation(() => {
            this.viewZRot.rotation.z += this.ssgSettings.AnimateZSpeed;
        });
    }

    private startAnimation(updateScene?: () => void) {
        if (this.animating) {
            return;
        }
        this.animating = true;

        const animate = () => {
            if (this.animating) {
                requestAnimationFrame(animate);
            }

            if (updateScene) {
                updateScene();
            }

            this.renderer.render(this.scene, this.camera);
        }

        animate();
    }

    private stopAnimation() {
        this.animating = false;
    }

    private calculateSystemRadius(rootObject: CelestialObject): number {
        let maxRadius = 0;

        for (const childObj of rootObject.ChildObjects) {
            maxRadius = Math.max(maxRadius, this.calculateSystemRadius(childObj))
        }

        return maxRadius + rootObject.OrbitalSemiMajorAxis;
    }

    private buildSolarSystem(rootObject: CelestialObject): THREE.Group {
        const sceneGroup = new THREE.Group();

        let planetaryRadius = rootObject.ObjectRadius * this.ssgSettings.SystemScale;
        const majorAxis = rootObject.OrbitalSemiMajorAxis * this.ssgSettings.SystemScale;
        const minorAxis = rootObject.OrbitalSemiMinorAxis * this.ssgSettings.SystemScale;

        console.log(`Building '${rootObject.Name}' with radius ${planetaryRadius} and orbit: ${majorAxis}/${minorAxis}`);

        let objectGroup = new THREE.Group();

        if (planetaryRadius > 0) {
            if (rootObject.IsStar) {
                planetaryRadius *= this.ssgSettings.StarScale;
                objectGroup.add(Utils.buildStar(0, 0, 0, planetaryRadius, rootObject.BaseColor));
            }
            else {
                planetaryRadius *= this.ssgSettings.PlanetScale;
                objectGroup.add(Utils.buildPlanet(0, 0, 0, planetaryRadius, rootObject.BaseColor));
            }

            sceneGroup.add(objectGroup);
        }

        if (rootObject.OrbitalSemiMajorAxis > 0) {
            if (objectGroup) {
                Utils.setPosition(objectGroup, majorAxis, 0, 0);
            }

            const orbitObject = Utils.buildEllipse(0, 0, 0, majorAxis, minorAxis,
                this.ssgSettings.OrbitalColor, 0);

            sceneGroup.add(orbitObject);
        }

        if (rootObject.PhaseAngle != 0) {
            sceneGroup.rotation.order = "ZYX";
            sceneGroup.rotation.z = Utils.degreesToRadians(rootObject.PhaseAngle);
        }

        if (rootObject.OrbitalInclination != 0) {
            sceneGroup.rotation.y = Utils.degreesToRadians(rootObject.OrbitalInclination);
        }

        for (const childObj of rootObject.ChildObjects) {
            const childGroup = this.buildSolarSystem(childObj);
            objectGroup.add(childGroup);
        }

        return sceneGroup;
    }

    private buildTestScene(): THREE.Group {
        const sceneGroup = new THREE.Group();
        const origin = Utils.buildPlanet(0, 0, 0, 50, '#ffff00');
        sceneGroup.add(origin);

        // const grid = Utils.buildGrid(4, 8, '#0000dd', '#000077');
        // const polarGrid = Utils.buildPolarGrid(300, 16, 6, 64, '#000077', '#000055');

        const redMaj = 600;
        const redMin = 550;

        const greenMaj = 1200;
        const greenMin = 1000;

        const blueMaj = 500;

        sceneGroup.add(
            Utils.buildPlanet(redMaj, 0, 0, 30, '#ff0000'),
            Utils.buildPlanet(-redMaj, 0, 0, 30, '#770000'),
            Utils.buildEllipse(0, 0, 0, redMaj, redMin, '#ff0000'),
            Utils.buildPlanet(0, greenMin, 0, 30, '#00ff00'),
            Utils.buildPlanet(0, -greenMin, 0, 30, '#007700'),
            Utils.buildEllipse(0, 0, 0, greenMaj, greenMin, '#00ff00'),
            Utils.buildPlanet(0, 0, blueMaj, 30, '#0000ff'),
            Utils.buildPlanet(0, 0, -blueMaj, 30, '#000077'),
        );

        return sceneGroup;
    }
}

console.log('TS Interop starting up!');
