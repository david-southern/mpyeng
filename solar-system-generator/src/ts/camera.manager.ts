import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

import { CanvasManager } from './canvas.manager';
import { SceneManager } from './scene.manager';
import { GlobalSettings } from './settings';
import { THREEUtils } from './utils.three';

const DEFAULT_FOV = 30;
const DEFAULT_ASPECT = 1.61;

export class SSGCameraManager {
    private static _Instance = new SSGCameraManager();
    public static get Instance() {
        return SSGCameraManager._Instance;
    }

    // Make the constructor private to signal that SSGRxSettings is a singleton
    private constructor() {
        this.camera = new THREE.PerspectiveCamera(DEFAULT_FOV, DEFAULT_ASPECT);

        this.camera.aspect = CanvasManager.CanvasAspect;
        this.camera.updateProjectionMatrix();

        GlobalSettings.LookAt$.subscribe(
            (target) => (this.lookAtTarget = SceneManager.FindObject(target))
        );
    }

    public SetRenderElement(renderElement: HTMLElement) {
        this.orbitControls = new OrbitControls(this.camera, renderElement);
    }

    private camera: THREE.PerspectiveCamera;
    public get Camera() {
        return this.camera;
    }

    private orbitControls?: OrbitControls;
    private lookAtTarget?: THREE.Object3D;

    public UpdateCamera() {
        if (this.lookAtTarget) {
            const lookAtVec = new THREE.Vector3();
            this.lookAtTarget.getWorldPosition(lookAtVec);
            if (this.orbitControls) {
                // set camera to rotate around the target
                this.orbitControls.target = lookAtVec;
                this.orbitControls.update();
            }
        }
    }

    private FitCameraToScene(scene: THREE.Scene) {
        THREEUtils.FitCameraToObject(
            scene,
            this.camera,
            CanvasManager.CanvasAspect,
            this.orbitControls
        );
    }
}

export const CameraManager = SSGCameraManager.Instance;
