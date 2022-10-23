/* eslint-disable */

import _ from 'lodash';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

import blackBackground from '../images/black.png';

import * as PP from 'postprocessing';

import { CelestialObject } from './celestial-object';
// import { OrbitControls } from './OrbitControls';
import { Logger, SSGSystemFilter } from './logger';
import {
    GRID_TYPE_RECTANGULAR,
    GRID_TYPE_NONE,
    GRID_TYPE_POLAR,
    SSGOldSettings,
} from './zzz.settings';
import { Utils } from './utils';
import { Orbiter } from './orbiter';
import { SettingsManager } from './zzz.settings.manager';
import { Constants } from './constants';
import { THREEUtils } from './utils.three';

const DEFAULT_FOV = 70;
const DEFAULT_ASPECT = 1.61;
const DEFAULT_ORBITAL_COLOR = '#999999';

// I modeled all the planetary data in actual units, but those numbers are huge, and hard to track while debugging.
// Scale everything down to 'smallish' numbers internally.
const CoordsScale = Constants.OneAU;

export class SSGOldRenderer {
    // private ssgSettings: SSGSettings = null!;

    private canvasElement: HTMLElement = null!;
    private systemTimeElement: HTMLElement = null!;

    private canvasWidth: number = null!;
    private canvasHeight: number = null!;
    private canvasAspect: number = null!;

    private systemScene: THREE.Scene;
    private gridScene: THREE.Scene;
    private camera: THREE.PerspectiveCamera;
    private ambientLight: THREE.AmbientLight;
    private directionalLight: THREE.DirectionalLight;
    private orbitControls: OrbitControls = null!;
    private renderer: THREE.WebGLRenderer;
    private systemGroup: THREE.Object3D = null!;
    private orbiters: Orbiter[] = [];
    private gridGroup: THREE.Object3D = null!;
    private loader: THREE.TextureLoader;
    private lastBGUrl?: string;
    private lookAtTarget?: THREE.Group;
    private composer: PP.EffectComposer = null!;
    private textureEffect: PP.TextureEffect = null!;
    private backgroundAdjustEffect: PP.BrightnessContrastEffect = null!;

    private solarSystem: CelestialObject = null!;
    private actualStartTime?: number;
    private lastActualTime?: number;
    private simTime?: number;

    constructor() {
        this.systemScene = new THREE.Scene();
        this.gridScene = new THREE.Scene();
        this.systemScene.name = 'SSG-root';
        this.ambientLight = new THREE.AmbientLight();
        this.systemScene.add(this.ambientLight);
        this.directionalLight = new THREE.DirectionalLight();
        this.camera = new THREE.PerspectiveCamera(DEFAULT_FOV, DEFAULT_ASPECT);
        this.renderer = new THREE.WebGLRenderer({
            powerPreference: 'high-performance',
            antialias: false,
            stencil: false,
            depth: false,
        });
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap; // default THREE.PCFShadowMap

        this.loader = new THREE.TextureLoader();
    }

    private safeGetElement(elementId: string): HTMLElement {
        const checkElement = document.getElementById(elementId);

        if (!checkElement) {
            throw new Error(
                `SSG element Id '${elementId}' did not select any DOM element`
            );
        }

        return checkElement;
    }

    public initialize(canvasDivId: string, systemTimeDivId: string) {
        this.canvasElement = this.safeGetElement(canvasDivId);
        this.systemTimeElement = this.safeGetElement(systemTimeDivId);

        this.canvasWidth = this.canvasElement.offsetWidth;
        this.canvasHeight = this.canvasElement.offsetHeight;
        this.canvasAspect = this.canvasWidth / this.canvasHeight;

        const rect = this.canvasElement.getBoundingClientRect();

        Logger.info(
            SSGSystemFilter.Initialization,
            'Initializing SSG render with:'
        );
        Logger.info(
            SSGSystemFilter.Initialization,
            `    window @(${rect.left}, ${rect.top}), size: (${this.canvasWidth} x ${this.canvasHeight}), aspect: ${this.canvasAspect}`
        );

        this.camera.aspect = this.canvasAspect;
        this.camera.updateProjectionMatrix();

        // We want the grid to render behind everything else.  We will manage the renderers clearing manually to achieve this.
        this.renderer.autoClear = false;
        this.renderer.setSize(this.canvasWidth, this.canvasHeight);

        this.composer = new PP.EffectComposer(this.renderer);
        this.composer.addPass(new PP.ClearPass());
        const defaultTexture = this.loader.load(blackBackground);
        this.textureEffect = new PP.TextureEffect({
            texture: defaultTexture,
        });
        this.composer.addPass(
            new PP.EffectPass(this.camera, this.textureEffect)
        );

        this.backgroundAdjustEffect = new PP.BrightnessContrastEffect();
        this.composer.addPass(
            new PP.EffectPass(this.camera, this.backgroundAdjustEffect)
        );

        const gridRenderPass = new PP.RenderPass(this.gridScene, this.camera);
        this.composer.addPass(gridRenderPass);
        gridRenderPass.clearPass.enabled = false;
        gridRenderPass.ignoreBackground = true;
        this.composer.addPass(new PP.ClearPass(false, true, false));
        const sceneRenderPass = new PP.RenderPass(
            this.systemScene,
            this.camera
        );
        sceneRenderPass.clearPass.enabled = false;
        sceneRenderPass.ignoreBackground = true;
        this.composer.addPass(sceneRenderPass);

        this.composer.addPass(
            new PP.EffectPass(
                this.camera,
                new PP.ColorDepthEffect({
                    bits: 32,
                })
            )
        );

        // this.composer.addPass(new PP.EffectPass(this.camera, new PP.DotScreenEffect({
        //     scale: 1
        // })));
        // this.composer.addPass(new PP.EffectPass(this.camera, new PP.HueSaturationEffect({
        //     saturation: -1
        // })));

        this.orbitControls = new OrbitControls(
            this.camera,
            this.renderer.domElement
        );

        this.canvasElement.appendChild(this.renderer.domElement);

        this.getNextAnimationFrame();
    }

    public render(solarSystem: CelestialObject, newSettings: SSGOldSettings) {
        this.solarSystem = _.cloneDeep(solarSystem);

        Logger.info(
            SSGSystemFilter.RenderSettings,
            'SSG.render: System: ',
            this.solarSystem
        );

        SettingsManager.clearSettingsSubscriptions();

        this.actualStartTime = this.lastActualTime = this.simTime = undefined;

        if (this.systemGroup) {
            this.systemScene.remove(this.systemGroup);
        }
        if (this.gridGroup) {
            this.gridScene.remove(this.gridGroup);
        }

        SettingsManager.subscribeSettings(async (settings: SSGOldSettings) => {
            this.lookAtTarget = undefined;
            this.camera.fov = settings.FieldOfViewDegrees;
            this.camera.updateProjectionMatrix();

            if (settings.BackgroundImage && settings.BackgroundImage.URL) {
                if (settings.BackgroundImage.URL.startsWith('#')) {
                    this.gridScene.background = new THREE.Color(
                        settings.BackgroundImage.URL
                    );
                    return;
                }

                // this.gridScene.background = this.loader.load(settings.BackgroundImage.URL);

                if (this.lastBGUrl != settings.BackgroundImage.URL) {
                    this.lastBGUrl = settings.BackgroundImage.URL;
                    this.loader.load(
                        settings.BackgroundImage.URL,
                        (texture) => {
                            Logger.info(
                                SSGSystemFilter.RenderSettings,
                                `SSG.render: Loaded background image: ${settings.BackgroundImage?.Description}`
                            );
                            this.textureEffect.texture = texture;
                        }
                    );
                }

                this.backgroundAdjustEffect.brightness =
                    settings.BackgroundImage.Brightness ?? 0;
                this.backgroundAdjustEffect.contrast =
                    settings.BackgroundImage.Contrast ?? 0;
            }
        });

        Logger.info(
            SSGSystemFilter.RenderSettings,
            'SSG.render: Settings: ',
            newSettings
        );

        SettingsManager.subscribeSettings((settings: SSGOldSettings) => {
            this.ambientLight.color = new THREE.Color(
                settings.AmbientLightColor
            );
        });

        SettingsManager.subscribeSettings((settings: SSGOldSettings) => {
            // It is safe to remove a child that you don't have, but not safe to add a child twice.  Remove the
            // light here before adding it so that I don't have to track whether the light has been added or not.
            this.systemScene.remove(this.directionalLight);

            if (settings.IncludeDirectionalLight) {
                this.systemScene.add(this.directionalLight);
                this.directionalLight.color = new THREE.Color(
                    settings.DirectionalLightColor
                );
                this.directionalLight.intensity =
                    settings.DirectionalLightIntensity;
                THREEUtils.SetPosition(
                    this.directionalLight,
                    settings.DirectionalLightPosition
                );
            }
        });

        this.orbiters = [];
        this.systemGroup = this.buildSolarSystem(this.solarSystem);
        this.gridGroup = new THREE.Group();
        this.gridGroup.name = 'SSG-system-grid';

        SettingsManager.subscribeSettings((settings: SSGOldSettings) => {
            while (this.gridGroup.children.length > 0) {
                this.gridGroup.remove(this.gridGroup.children[0]);
            }

            if (!settings.GridType || settings.GridType === GRID_TYPE_NONE) {
                return;
            }

            const boundingBox = new THREE.Box3();
            boundingBox.setFromObject(this.systemGroup);

            const gridSize =
                Math.max(
                    boundingBox.max.x - boundingBox.min.x,
                    boundingBox.max.y - boundingBox.min.y
                ) * settings.GridSizeFactor;

            let gridMesh;

            if (settings.GridType == GRID_TYPE_RECTANGULAR) {
                gridMesh = THREEUtils.ZZZBuildGrid(
                    gridSize,
                    settings.GridMajorDivisions,
                    settings.GridMajorColor,
                    settings.GridMinorColor
                );
            }

            if (settings.GridType == GRID_TYPE_POLAR) {
                gridMesh = THREEUtils.ZZZBuildPolarGrid(
                    gridSize / 2,
                    settings.GridMinorDivisions,
                    settings.GridMajorDivisions,
                    64,
                    settings.GridMajorColor,
                    settings.GridMinorColor
                );
            }

            if (gridMesh) {
                this.gridGroup.add(gridMesh);
            }
        });

        SettingsManager.subscribeSettings((settings: SSGOldSettings) => {
            // It is easier to rotate the top-level sceneGroup than to try and reposition the camera. Unfortunately I don't
            // understand 3D math well enough to get the rotation I want in one go, but separate rotations seem to work well
            // enough.

            this.gridGroup.setRotationFromAxisAngle(
                new THREE.Vector3(0, 0, 1),
                Utils.DegreesToRadians(settings.ViewAngleZDegrees)
            );
            this.gridGroup.setRotationFromAxisAngle(
                new THREE.Vector3(0, 1, 0),
                Utils.DegreesToRadians(settings.ViewAngleYDegrees)
            );
            this.gridGroup.setRotationFromAxisAngle(
                new THREE.Vector3(1, 0, 0),
                Utils.DegreesToRadians(settings.ViewAngleXDegrees)
            );

            this.systemGroup.setRotationFromAxisAngle(
                new THREE.Vector3(0, 0, 1),
                Utils.DegreesToRadians(settings.ViewAngleZDegrees)
            );
            this.systemGroup.setRotationFromAxisAngle(
                new THREE.Vector3(0, 1, 0),
                Utils.DegreesToRadians(settings.ViewAngleYDegrees)
            );
            this.systemGroup.setRotationFromAxisAngle(
                new THREE.Vector3(1, 0, 0),
                Utils.DegreesToRadians(settings.ViewAngleXDegrees)
            );
        });

        this.systemScene.add(this.systemGroup);
        this.gridScene.add(this.gridGroup);

        Logger.info(
            SSGSystemFilter.ModelBuilding,
            'Ready to fix camera to scene'
        );

        // We need all the changes to the scene pushed before fitting the camera, so publish here
        SettingsManager.publishSettings(newSettings);

        if (newSettings.ResetOrbitControls) {
            console.log('Resetting orbital controls!');
            this.orbitControls.reset();
            newSettings.ResetOrbitControls = false;
        }

        // Fit the camera before applying zoom, otherwise the camera will be fit to the zoomed scene, which is no good
        this.fitCameraToObject();

        SettingsManager.subscribeSettings((settings: SSGOldSettings) => {
            this.gridGroup.scale.x = settings.Zoom;
            this.gridGroup.scale.y = settings.Zoom;
            this.gridGroup.scale.z = settings.Zoom;

            this.systemGroup.scale.x = settings.Zoom;
            this.systemGroup.scale.y = settings.Zoom;
            this.systemGroup.scale.z = settings.Zoom;
        });

        // And publish once more to get the zoom updated
        SettingsManager.publishSettings(newSettings);

        Logger.info(
            SSGSystemFilter.RenderDiagnostics,
            'SSG System: ',
            this.systemGroup
        );
        Logger.info(
            SSGSystemFilter.RenderDiagnostics,
            'SSG Scene: ',
            this.systemScene
        );
        Logger.info(
            SSGSystemFilter.RenderDiagnostics,
            'SSG Grid: ',
            this.gridGroup
        );
        Logger.info(
            SSGSystemFilter.RenderDiagnostics,
            'SSG Camera: ',
            this.camera
        );

        if (Logger.wouldLog(SSGSystemFilter.ExportDiagnostics)) {
            Logger.info(
                SSGSystemFilter.ExportDiagnostics,
                'Scene.JSON export: ',
                JSON.stringify(this.systemScene.toJSON())
            );
        }
    }

    public updateSettings(settingsJson: string) {
        const newSettings = new SSGOldSettings(JSON.parse(settingsJson));

        Logger.info(
            SSGSystemFilter.RenderSettings,
            'updateSettings: Settings: ',
            newSettings
        );

        if (newSettings.ResetOrbitControls) {
            console.log('Resetting orbital controls!');
            this.orbitControls.reset();
            newSettings.ResetOrbitControls = false;
        }

        SettingsManager.publishSettings(newSettings);
    }

    private getNextAnimationFrame() {
        requestAnimationFrame((animationTime: DOMHighResTimeStamp) => {
            this.updateAnimation(animationTime);
        });
    }

    private nextTimeDiags = 0;

    private updateAnimation(actualMillis: number) {
        let showDiags = false;

        const actualTime = actualMillis / 1000;

        if (this.actualStartTime === undefined) {
            this.actualStartTime = actualTime;
        }

        if (this.lastActualTime === undefined) {
            this.lastActualTime = actualTime;
        }

        if (this.simTime === undefined) {
            this.simTime = 0;
        }

        let speedScale = 0;

        if (Utils.FloatNE(SettingsManager.CurrentSettings.AnimationSpeed, 0)) {
            speedScale = SettingsManager.CurrentSettings.AnimationTimeScale;
        }

        const actualSimTime = actualTime - this.actualStartTime;
        const actualElapsedSeconds = actualTime - this.lastActualTime;
        this.lastActualTime = actualTime;
        const simElapsedSeconds = actualElapsedSeconds * speedScale;
        this.simTime += simElapsedSeconds;

        if (this.systemTimeElement) {
            this.systemTimeElement.innerText =
                'System Time: ' + Utils.HumanTime(this.simTime);
        }

        if (Date.now() > this.nextTimeDiags) {
            showDiags = true;
            let diagsString = `Anim: SpeedScale: ${SettingsManager.CurrentSettings.AnimationTimeScale}`;
            diagsString += ` (${SettingsManager.CurrentSettings.AnimationTimeScaleHuman})`;
            diagsString += `, Clock: Actual: ${Utils.HumanTime(
                actualSimTime
            )}, Sim: ${Utils.HumanTime(this.simTime)}`;
            diagsString += `, Frame: Actual: ${Utils.HumanTime(
                actualElapsedSeconds
            )}, Sim: ${Utils.HumanTime(simElapsedSeconds)}`;
            Logger.info(SSGSystemFilter.TimingDiagnostics, diagsString);
            this.nextTimeDiags = Date.now() + 1000;
        }

        for (const nextOrbiter of this.orbiters) {
            nextOrbiter.updatePosition(simElapsedSeconds);
        }

        if (this.lookAtTarget) {
            const lookAtVec = new THREE.Vector3();
            this.lookAtTarget.getWorldPosition(lookAtVec);
            if (this.orbitControls) {
                // set camera to rotate around the target
                this.orbitControls.target = lookAtVec;
                this.orbitControls.update();
            }
            // this.camera.lookAt(lookAtVec);
            // this.camera.updateProjectionMatrix();

            if (showDiags) {
                Logger.info(
                    SSGSystemFilter.Always,
                    `Look At: ${THREEUtils.DumpVec(lookAtVec)}`
                );
            }
        }

        // // Clear buffers
        // this.renderer.clear();
        // this.renderer.render(this.gridScene, this.camera);
        // // clear depth buffer
        // this.renderer.clearDepth();
        // this.renderer.render(this.systemScene, this.camera);

        this.composer.render();

        if (SettingsManager.CurrentSettings.DownloadImage) {
            SettingsManager.CurrentSettings.DownloadImage = false;
            this.renderer.domElement.toBlob((imageBlob) => {
                if (imageBlob) {
                    Utils.DownloadFileFromBlob('system-image.png', imageBlob);
                }
            });
        }

        this.getNextAnimationFrame();
    }

    private fitCameraToObject() {
        const offset = 1.05;

        const boundingBox = new THREE.Box3();

        // get bounding box of object - this will be used to setup controls and camera
        boundingBox.setFromObject(this.systemScene);

        Logger.info(
            SSGSystemFilter.RenderDiagnostics,
            `fitCamera: Object boundingBox: min: ${THREEUtils.DumpVec(
                boundingBox.min
            )}, max: ${THREEUtils.DumpVec(boundingBox.max)}`
        );

        const center = new THREE.Vector3();
        const size = new THREE.Vector3();

        boundingBox.getCenter(center);
        boundingBox.getSize(size);

        Logger.info(
            SSGSystemFilter.RenderDiagnostics,
            `fitCamera: Object boundingBox: center: ${THREEUtils.DumpVec(
                center
            )}, size: ${THREEUtils.DumpVec(size)}`
        );

        // get the max side of the bounding box (fits to width OR height as needed )
        const fov = this.camera.fov * (Math.PI / 180);

        const ySize = Math.max(size.y, size.x / this.canvasAspect);

        let cameraYDistance = Math.abs(ySize / 2 / Math.tan(fov / 2));
        cameraYDistance *= offset; // zoom out a little so that objects don't fill the screen

        const cameraDistance = cameraYDistance;

        const minZ = boundingBox.min.z;
        const cameraToFarEdge =
            minZ < 0 ? -minZ + cameraDistance : cameraDistance - minZ;

        Logger.info(
            SSGSystemFilter.RenderDiagnostics,
            `New camera params: Z: ${cameraDistance}, FAR: ${
                cameraToFarEdge * 3
            }`
        );

        this.camera.position.z = cameraDistance;
        this.camera.far = cameraToFarEdge * 3;
        this.camera.updateProjectionMatrix();

        if (this.orbitControls) {
            // prevent camera from zooming out far enough to create far plane cutoff
            this.orbitControls.maxDistance = cameraToFarEdge * 2;
            this.orbitControls.saveState();

            // set camera to rotate around the target
            const lookAtVec = new THREE.Vector3(0, 0, 0);
            if (this.lookAtTarget) {
                this.lookAtTarget.getWorldPosition(lookAtVec);
            }
            this.orbitControls.target = lookAtVec;
            const lookAtName = this.lookAtTarget?.name ?? 'center';
            Logger.info(
                SSGSystemFilter.Always,
                `Look at: ${lookAtName} (${THREEUtils.DumpVec(
                    this.orbitControls.target
                )})`
            );

            this.orbitControls.update();
        }
    }

    private buildSolarSystem(rootObject: CelestialObject): THREE.Group {
        const sceneGroup = new THREE.Group();
        sceneGroup.name = `${rootObject.Name}-root`;

        const majorAxis = rootObject.OrbitalSemiMajorAxis / CoordsScale;
        const minorAxis = rootObject.OrbitalSemiMinorAxis / CoordsScale;
        const perigee = rootObject.OrbitalPerigee / CoordsScale;

        const objectGroup = new THREE.Group();
        objectGroup.name = `${rootObject.Name}-obj-geom`;

        if (majorAxis > 0) {
            const orbitCurve = THREEUtils.BuildOrbitalEllipse(
                0,
                0,
                majorAxis,
                minorAxis
            );

            if (rootObject.OrbitColor !== 'none') {
                const orbitObject = THREEUtils.BuildOrbitalMesh(
                    0,
                    0,
                    0,
                    orbitCurve,
                    rootObject.OrbitColor ?? DEFAULT_ORBITAL_COLOR
                );
                orbitObject.name = `${rootObject.Name}-orbit-geom`;
                sceneGroup.add(orbitObject);
            }

            if (objectGroup) {
                const planetOrbiter = new Orbiter(
                    objectGroup,
                    orbitCurve,
                    rootObject.InitialOrbitalAngle,
                    rootObject.OrbitalVelocity
                );
                planetOrbiter.updatePosition(0);
                this.orbiters.push(planetOrbiter);
            }
        }

        SettingsManager.subscribeSettings((settings: SSGOldSettings) => {
            if (rootObject.Name == settings.LookAt) {
                this.lookAtTarget = objectGroup;
                Logger.info(
                    SSGSystemFilter.RenderSettings,
                    `Looking At '${settings.LookAt}'`
                );
            }

            if (rootObject.Obj3D) {
                objectGroup.remove(rootObject.Obj3D);
                rootObject.Obj3D = undefined;
            }

            if (rootObject.ObjectRadius > 0) {
                let planetaryRadius = rootObject.ObjectRadius / CoordsScale;

                if (rootObject.IsStar) {
                    planetaryRadius *= settings.StarScale;
                    rootObject.Obj3D = THREEUtils.BuildStar(
                        0,
                        0,
                        0,
                        planetaryRadius,
                        rootObject.ObjectColor
                    );
                } else {
                    planetaryRadius *= settings.PlanetScale;
                    rootObject.Obj3D = THREEUtils.BuildPlanet(
                        0,
                        0,
                        0,
                        planetaryRadius,
                        rootObject.ObjectColor
                    );
                }

                Logger.info(
                    SSGSystemFilter.ModelBuilding,
                    `Building '${rootObject.Name}' with radius ${planetaryRadius} and orbit: ${majorAxis}/${minorAxis}`
                );
            } else {
                const ringInnerRadius = rootObject.RingInnerRadius ?? 0;
                const ringWidth = rootObject.RingWidth ?? 0.5;
                const ringThickness = 0.001;
                const ringDensity = Math.max(
                    Math.min(rootObject.RingDensity ?? 0.001, 1),
                    0
                );
                const ringColor = rootObject.RingColor ?? 'none';

                if (
                    ringInnerRadius > 0 &&
                    ringColor != 'none' &&
                    rootObject.ParentObject
                ) {
                    // If the parent object is a planet, make it cast shadows so the rings look correct.
                    if (
                        rootObject.ParentObject &&
                        !rootObject.ParentObject.IsStar &&
                        rootObject.ParentObject.Obj3D
                    ) {
                        // eslint-disable-next-line @typescript-eslint/no-explicit-any
                        (rootObject.ParentObject.Obj3D as any).castShadow =
                            true; //default is false
                    }

                    let planetaryRadius =
                        rootObject.ParentObject.ObjectRadius *
                        (rootObject.ParentObject.IsStar
                            ? settings.StarScale
                            : settings.PlanetScale);
                    planetaryRadius /= CoordsScale;

                    const ringGeomInnerRadius =
                        ringInnerRadius * planetaryRadius;
                    const ringGeomWidth = ringWidth * planetaryRadius;
                    const ringGeomOuterRadius =
                        ringGeomInnerRadius + ringGeomWidth;
                    const ringGeomThickness = ringGeomWidth * ringThickness;

                    Logger.info(
                        SSGSystemFilter.ModelBuilding,
                        `Building '${rootObject.Name}' ring system with radius ${ringInnerRadius}, width: ${ringWidth}, thickness: ${ringThickness}`
                    );
                    Logger.info(
                        SSGSystemFilter.ModelBuilding,
                        `    effective ring dimensions: inner ${ringGeomInnerRadius}, width: ${ringGeomWidth}, outer: ${ringGeomOuterRadius}, thick: ${ringGeomThickness}`
                    );

                    const extrudeSettings = {
                        curveSegments: 32,
                        depth: ringGeomThickness,
                        bevelEnabled: false,
                    };

                    const outerRing = new THREE.Shape().absarc(
                        0,
                        0,
                        ringGeomOuterRadius,
                        0,
                        Math.PI * 2,
                        false
                    );

                    const holePath = new THREE.Path().absarc(
                        0,
                        0,
                        ringGeomInnerRadius,
                        0,
                        Math.PI * 2,
                        true
                    );

                    outerRing.holes.push(holePath);

                    const ringGeometry = new THREE.ExtrudeGeometry(
                        outerRing,
                        extrudeSettings
                    );
                    // const ringMaterial = THREEUtils.planetMaterial(ringColor)
                    const ringMaterial = this.ringMaterialTextured(
                        ringColor,
                        ringDensity
                    );
                    const edgeMaterial = new THREE.MeshLambertMaterial({
                        color: '#000000',
                    });

                    const ringMesh = new THREE.Mesh(ringGeometry, [
                        ringMaterial,
                        edgeMaterial,
                    ]);
                    ringMesh.receiveShadow = true;
                    THREEUtils.SetPosition(
                        ringMesh,
                        0,
                        0,
                        -ringGeomThickness / 2
                    );

                    rootObject.Obj3D = ringMesh;
                }
            }

            if (rootObject.Obj3D) {
                objectGroup.add(rootObject.Obj3D);
            }
        });

        sceneGroup.add(objectGroup);

        if (perigee != 0) {
            sceneGroup.position.x = perigee;
        }

        if (rootObject.PhaseAngle != 0) {
            sceneGroup.rotation.order = 'ZYX';
            sceneGroup.rotation.z = Utils.DegreesToRadians(
                rootObject.PhaseAngle
            );
        }

        if (rootObject.OrbitalInclination != 0) {
            sceneGroup.rotation.y = Utils.DegreesToRadians(
                rootObject.OrbitalInclination
            );
        }

        for (const childObj of rootObject.ChildObjects) {
            const childGroup = this.buildSolarSystem(childObj);
            objectGroup.add(childGroup);
        }

        return sceneGroup;
    }

    private ringMaterialTextured(ringColor: string, density = 0.1) {
        const width = 512;
        const height = 512;

        const size = width * height;
        const byteSize = size * 4;
        const data = new Uint8Array(byteSize);

        let stride = 0;

        while (stride < byteSize) {
            const c = Math.random() < density ? 255 : 0;
            data[stride++] = c;
            data[stride++] = c;
            data[stride++] = c;
            data[stride++] = 255;
        }
        /*
                let chunkCount = size * density;
        
                for (let chunk = 0; chunk < chunkCount; chunk++) {
                    const x = Math.random() * width;
                    const y = Math.random() * height;
                    const radius = (Math.random() * 0.5 + 0.5) * chunkSize;
        
                    let stride = y * width * 4 + x * 4;
        
                    for (let dy = 0; dy < radius; dy++) {
                        for (let dx = 0; dx < radius * 4; dx++) {
                            if (stride >= byteSize) {
                                stride -= byteSize;
                            }
                            data[stride++] = 255;
                        }
                        stride += width * 4;
                    }
        
                }
        */
        // used the buffer to create a DataTexture

        const texture = new THREE.DataTexture(data, width, height);
        texture.needsUpdate = true;

        // // create a texture loader.
        // const textureLoader = new THREE.TextureLoader();

        // // load a texture
        // const texture = textureLoader.load(
        //     'images/ring-texture.png',
        // );

        texture.wrapS = THREE.RepeatWrapping;
        texture.wrapT = THREE.RepeatWrapping;
        // texture.repeat.set(4, 4);

        // create a "standard" material using
        // return new THREE.MeshStandardMaterial({ color: 'purple' });
        // return new THREE.MeshStandardMaterial({ alphaMap: texture, color: ringColor, transparent: true });
        return new THREE.MeshLambertMaterial({
            alphaMap: texture,
            color: ringColor,
            transparent: true,
        });
        //return new THREE.MeshLambertMaterial({ color: 'purple' });
    }
}
