import _ from 'lodash';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls'

import * as PP from 'postprocessing';

import { Logger, SSGSystemFilter } from './ssg.logger';
import { Utils } from './utils';
import { SSGSimTimeManager } from './ssg.simtime.manager';
import { SSGSettings } from './ssg.settings';
import { DefaultBackgroundImage } from './ssg.settings.backgrounds';
import { firstValueFrom } from 'rxjs';
import { THREEUtils } from './utils.three';

const DEFAULT_FOV = 30;
const DEFAULT_ASPECT = 1.61;

export class SSGRenderer {
    private settings = SSGSettings.GlobalSettings;
    private timeManager = SSGSimTimeManager.SimTimeManager;

    private canvasElement: HTMLElement;
    private systemTimeElement: HTMLElement;

    private canvasWidth: number;
    private canvasHeight: number;
    private canvasAspect: number;

    private systemScene: THREE.Scene;
    private gridScene: THREE.Scene;
    private camera: THREE.PerspectiveCamera;
    private ambientLight: THREE.AmbientLight;
    private directionalLight: THREE.DirectionalLight;
    private orbitControls: OrbitControls;
    private renderer: THREE.WebGLRenderer;
    private loader: THREE.TextureLoader;
    private lastBGUrl?: string;
    private lookAtTarget?: THREE.Group;
    private composer: PP.EffectComposer;
    private textureEffect: PP.TextureEffect;
    private backgroundAdjustEffect: PP.BrightnessContrastEffect;

    private cubeMesh: THREE.Mesh;

    private safeGetElement(elementId: string): HTMLElement {
        const checkElement = document.getElementById(elementId);

        if (!checkElement) {
            throw new Error(`SSG element Id '${elementId}' did not select any DOM element`);
        }

        return checkElement;
    }

    public constructor(canvasDivId: string, systemTimeDivId: string) {
        this.canvasElement = this.safeGetElement(canvasDivId);
        this.systemTimeElement = this.safeGetElement(systemTimeDivId);

        this.canvasWidth = this.canvasElement.offsetWidth;
        this.canvasHeight = this.canvasElement.offsetHeight;
        this.canvasAspect = this.canvasWidth / this.canvasHeight;

        var rect = this.canvasElement.getBoundingClientRect();

        Logger.info(SSGSystemFilter.Initialization, `Initializing SSG render with:`);
        Logger.info(SSGSystemFilter.Initialization, `    window @(${rect.left}, ${rect.top}), size: (${this.canvasWidth} x ${this.canvasHeight}), aspect: ${this.canvasAspect}`);

        this.systemScene = new THREE.Scene();
        this.systemScene.name = 'SSG-root';

        this.gridScene = new THREE.Scene();

        this.ambientLight = new THREE.AmbientLight('white', 0.4);
        this.systemScene.add(this.ambientLight);

        this.directionalLight = new THREE.DirectionalLight('white', 0.5);
        THREEUtils.setPosition(this.directionalLight, new THREE.Vector3(1, 2, 3));
        this.systemScene.add(this.directionalLight);

        const otherLight = new THREE.DirectionalLight('white', 0.2);
        THREEUtils.setPosition(otherLight, new THREE.Vector3(-1, -2, -3));
        this.systemScene.add(otherLight);

        this.camera = new THREE.PerspectiveCamera(DEFAULT_FOV, DEFAULT_ASPECT);

        this.renderer = new THREE.WebGLRenderer({
            powerPreference: "high-performance",
            antialias: false,
            stencil: false,
            depth: false
        });
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap; // default THREE.PCFShadowMap

        this.loader = new THREE.TextureLoader();

        this.camera.aspect = this.canvasAspect;
        this.camera.updateProjectionMatrix();

        const geometry = new THREE.BoxGeometry(200, 200, 200);
        const material = new THREE.MeshLambertMaterial({ color: '#33ff33' });

        this.cubeMesh = new THREE.Mesh(geometry, material);

        this.systemScene.add(this.cubeMesh)

        // We want the grid to render behind everything else.  We will manage the renderers clearing manually to achieve this.
        this.renderer.autoClear = false;
        this.renderer.setSize(this.canvasWidth, this.canvasHeight);

        this.composer = new PP.EffectComposer(this.renderer);
        this.composer.addPass(new PP.ClearPass());
        const defaultTexture = this.loader.load(DefaultBackgroundImage.URL);
        this.textureEffect = new PP.TextureEffect({
            texture: defaultTexture
        });
        this.composer.addPass(new PP.EffectPass(this.camera, this.textureEffect));

        this.backgroundAdjustEffect = new PP.BrightnessContrastEffect();
        this.composer.addPass(new PP.EffectPass(this.camera, this.backgroundAdjustEffect));

        const gridRenderPass = new PP.RenderPass(this.gridScene, this.camera);
        this.composer.addPass(gridRenderPass);
        gridRenderPass.clearPass.enabled = false;
        gridRenderPass.ignoreBackground = true;
        this.composer.addPass(new PP.ClearPass(false, true, false));
        const sceneRenderPass = new PP.RenderPass(this.systemScene, this.camera);
        sceneRenderPass.clearPass.enabled = false;
        sceneRenderPass.ignoreBackground = true;
        this.composer.addPass(sceneRenderPass);

        this.composer.addPass(new PP.EffectPass(this.camera, new PP.ColorDepthEffect({ bits: 32 })));

        this.orbitControls = new OrbitControls(this.camera, this.renderer.domElement);

        this.canvasElement.appendChild(this.renderer.domElement);

        THREEUtils.fitCameraToObject(this.systemScene, this.camera, this.canvasAspect, this.orbitControls);

        this.getNextAnimationFrame();
    }

    private getNextAnimationFrame() {
        requestAnimationFrame((animationTime: DOMHighResTimeStamp) => { this.updateAnimation(animationTime); });
    }

    private ANIMATION_DIAGS_FREQ_MS = 5000;
    private SHOW_ANIMATION_DIAGS = false;
    private nextAnimDiags = 0;

    private async updateAnimation(actualMillis: number) {
        await this.timeManager.UpdateSimTime(actualMillis);

        if (this.SHOW_ANIMATION_DIAGS && Date.now() > this.nextAnimDiags) {
            Logger.info(SSGSystemFilter.TimingDiagnostics, `UpdateAnimation: Time Scale: ${await firstValueFrom(this.settings.AnimationTimeScaleHuman$)}`);
            Logger.info(SSGSystemFilter.TimingDiagnostics, `  Clock: Actual: ${Utils.humanTime(this.timeManager.ActualTime)}`);
            Logger.info(SSGSystemFilter.TimingDiagnostics, `            Sim: ${Utils.humanTime(this.timeManager.SimTime)}`);
            Logger.info(SSGSystemFilter.TimingDiagnostics, `  Frame: Actual: ${Utils.humanTime(this.timeManager.LastFrameActualElapsedSeconds)}`);
            Logger.info(SSGSystemFilter.TimingDiagnostics, `            Sim: ${Utils.humanTime(this.timeManager.LastFrameSimElapsedSeconds)}`);
            this.nextAnimDiags = Date.now() + this.ANIMATION_DIAGS_FREQ_MS;
        }

        if (this.lookAtTarget) {
            const lookAtVec = new THREE.Vector3();
            this.lookAtTarget.getWorldPosition(lookAtVec);
            if (this.orbitControls) {
                // set camera to rotate around the target
                this.orbitControls.target = lookAtVec;
                this.orbitControls.update();
            }
        }

        if (this.systemTimeElement) {
            this.systemTimeElement.innerText = 'System Time: ' + Utils.humanTime(this.timeManager.SimTime);
        }

        const rotationDegreesPerSecond = 90;

        const rotationAngle = Utils.clampDegrees(rotationDegreesPerSecond * this.timeManager.SimTime);

        // this.cubeMesh.setRotationFromAxisAngle(new THREE.Vector3(0.2, 0.4, 1).normalize(),
        //     Utils.degreesToRadians(rotationAngle));
        this.cubeMesh.setRotationFromAxisAngle(new THREE.Vector3(0, 1, 0).normalize(),
            Utils.degreesToRadians(rotationAngle));

        // this.cubeMesh.rotateOnAxis(new THREE.Vector3(0.2, 0.4, 1),
        //     Utils.degreesToRadians(rotationDegreesPerSecond) * this.timeManager.LastFrameSimElapsedSeconds);

        this.composer.render();

        this.getNextAnimationFrame();
    }
}
