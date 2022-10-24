import _ from 'lodash';

import { BehaviorSubject, combineLatest, Subject, takeUntil } from 'rxjs';
import { distinctUntilChanged, tap } from 'rxjs/operators';
import * as THREE from 'three';
import { CelestialObject } from './celestial-object';
import { Constants } from './constants';
import { Logger, SSGSystemFilter } from './logger';
import { Orbiter } from './orbiter';
import { GlobalSettings, GRID_TYPE_NONE, GRID_TYPE_POLAR, GRID_TYPE_RECTANGULAR } from './settings';
import { Utils } from './utils';
import { THREEUtils } from './utils.three';

export class SSGSceneManager {
    private static _Instance = new SSGSceneManager();
    public static get Instance() {
        return SSGSceneManager._Instance;
    }

    public SceneUpdated$ = new BehaviorSubject<THREE.Scene>(new THREE.Scene());

    // Make the constructor private to signal that SSGRxSettings is a singleton
    private constructor() {
        Logger.info(SSGSystemFilter.ModelBuilding, 'Constructing SceneManager');
        this.systemScene = new THREE.Scene();
        this.systemScene.name = 'SSG-root';
        this.systemScene.add(this.systemContent);
        this.systemContent.name = 'SSG-root-content';

        this.gridScene = new THREE.Scene();
        this.gridScene.name = 'Grid-root';
        this.gridScene.add(this.gridContent);
        this.gridContent.name = 'SSG-system-grid-content';

        this.ambientLight = new THREE.AmbientLight();
        this.systemScene.add(this.ambientLight);

        this.directionalLight = new THREE.DirectionalLight();
        this.systemScene.add(this.directionalLight);

        GlobalSettings.SystemRoot$.pipe(takeUntil(this.unsubscribe)).subscribe((rootObject) =>
            this.RenderSystem(rootObject)
        );

        Logger.info(SSGSystemFilter.ModelBuilding, 'Subscribing to Grid Updates');

        combineLatest([
            this.SceneUpdated$,
            GlobalSettings.GridType$,
            GlobalSettings.GridSizeFactor$,
            GlobalSettings.GridMajorDivisions$,
            GlobalSettings.GridMinorDivisions$,
            GlobalSettings.GridMajorColor$,
            GlobalSettings.GridMinorColor$,
        ])
            .pipe(takeUntil(this.unsubscribe))
            .subscribe(
                ([sceneUpdated, gridType, gridSizeFactor, majorDivisions, minorDivisions, majorColor, minorColor]) => {
                    this.RenderGrid(
                        sceneUpdated,
                        gridType,
                        gridSizeFactor,
                        majorDivisions,
                        minorDivisions,
                        majorColor,
                        minorColor
                    );
                }
            );
    }

    public Destroy() {
        this.unsubscribe.next();
        this.unsubscribe.complete();
    }

    private unsubscribe = new Subject<void>();

    public lastSceneUpdate = 0;

    private systemScene: THREE.Scene;
    public get SystemScene() {
        return this.systemScene;
    }

    private gridScene: THREE.Scene;
    public get GridScene() {
        return this.gridScene;
    }

    private systemContent = new THREE.Group();
    private gridContent = new THREE.Group();

    private orbiters: Orbiter[] = [];

    private ambientLight: THREE.AmbientLight;
    private directionalLight: THREE.DirectionalLight;

    private RenderSystem(rootObject?: CelestialObject) {
        try {
            Logger.info(
                SSGSystemFilter.RenderDiagnostics,
                `Starting RenderSystem - rootObject: ${rootObject?.Name ?? '<none>'}`
            );

            this.systemContent.clear();

            if (!rootObject) {
                return;
            }

            this.orbiters = [];
            const systemRoot = this.RenderCelestialObject(rootObject);
            this.systemContent.add(systemRoot);

            this.lastSceneUpdate = Date.now();

            Logger.info(SSGSystemFilter.RenderDiagnostics, 'SSG Scene: ', this.systemScene);
        } finally {
            this.SceneUpdated$.next(this.systemScene);
        }
    }

    RenderCelestialObject(rootObject: CelestialObject) {
        const rootGroup = rootObject.OwnedObject3D(Constants.RootGroup, THREE.Group, `${rootObject.Name}-root`);
        rootGroup.rotation.order = 'ZYX';

        const orbitGroup = rootObject.OwnedObject(Constants.OrbitGroup, () => {
            const orbitGroup = new THREE.Group();
            orbitGroup.name = `${rootObject.Name}-orbit`;
            rootGroup.add(orbitGroup);
            return orbitGroup;
        });

        const orbitCurve = rootObject.OwnedObject(Constants.OrbitCurve, () => {
            return new THREE.EllipseCurve(0, 0, 1, 1, 0, Math.PI * 2, false, 0);
        });

        const bodyGroup = rootObject.OwnedObject(Constants.BodyGroup, () => {
            const bodyGroup = new THREE.Group();
            bodyGroup.name = `${rootObject.Name}-body`;
            return bodyGroup;
        });

        const bodyOrbiter = rootObject.OwnedObject(Constants.Orbiter, () => {
            const bodyOrbiter = new Orbiter(bodyGroup, orbitCurve);
            this.orbiters.push(bodyOrbiter);
            return bodyOrbiter;
        });

        const ringGroup = rootObject.OwnedObject(Constants.RingGroup, () => {
            const ringGroup = new THREE.Group();
            ringGroup.name = `${rootObject.Name}-rings`;
            return ringGroup;
        });

        rootObject.OwnedObject(Constants.PerigeeSubscriber, () => {
            return rootObject.OrbitalPerigee$.pipe(takeUntil(this.unsubscribe), distinctUntilChanged()).subscribe(
                (orbitPerigee) => {
                    rootGroup.position.x = orbitPerigee / Constants.CoordsScale;
                }
            );
        });

        rootObject.OwnedObject(Constants.PhaseAngleSubscriber, () => {
            return rootObject.PhaseAngle$.pipe(takeUntil(this.unsubscribe), distinctUntilChanged()).subscribe(
                (phaseAngle) => {
                    rootGroup.rotation.z = Utils.DegreesToRadians(phaseAngle);
                }
            );
        });

        rootObject.OwnedObject(Constants.InclinationSubscriber, () => {
            return rootObject.OrbitalInclination$.pipe(takeUntil(this.unsubscribe), distinctUntilChanged()).subscribe(
                (inclinationAngle) => {
                    rootGroup.rotation.y = Utils.DegreesToRadians(inclinationAngle);
                }
            );
        });

        rootObject.OwnedObject(Constants.OrbitSubscriber, () => {
            return combineLatest([
                rootObject.OrbitalSemiMajorAxis$,
                rootObject.OrbitalSemiMinorAxis$,
                rootObject.OrbitColor$,
            ])
                .pipe(
                    takeUntil(this.unsubscribe),
                    distinctUntilChanged((prev, curr) => _.isEqual(prev, curr))
                )
                .subscribe(([semiMajorAxis, semiMinorAxis, orbitColor]) => {
                    const majorAxis = semiMajorAxis / Constants.CoordsScale;

                    if (Utils.FloatLE(majorAxis, 0) || orbitColor == Constants.COLOR_NONE) {
                        orbitGroup.removeFromParent();
                        return;
                    }

                    const minorAxis = semiMinorAxis / Constants.CoordsScale;

                    orbitGroup.clear();

                    orbitCurve.xRadius = majorAxis;
                    orbitCurve.yRadius = minorAxis;

                    rootObject.RemoveOwnedObject(Constants.OrbitMesh);

                    const orbitMesh = rootObject.OwnedObject(Constants.OrbitMesh, () => {
                        const points = orbitCurve.getPoints(250);
                        const geometry = new THREE.BufferGeometry().setFromPoints(points);
                        const ellipse = new THREE.Line(
                            geometry,
                            new THREE.LineBasicMaterial({ color: orbitColor ?? Constants.DEFAULT_ORBITAL_COLOR })
                        );
                        ellipse.name = `${rootObject.Name}-orbit-geom`;
                        return ellipse;
                    });

                    orbitGroup.add(orbitMesh);

                    Logger.info(
                        SSGSystemFilter.ModelBuilding,
                        `Building '${rootObject.Name}' orbit: ${majorAxis}/${minorAxis}`
                    );
                });
        });

        rootObject.OwnedObject(Constants.BodySubscriber, () => {
            return combineLatest([
                rootObject.ObjectRadius$,
                rootObject.ObjectColor$,
                rootObject.IsStar$,
                GlobalSettings.StarScale$,
                GlobalSettings.PlanetScale$,
            ])
                .pipe(
                    takeUntil(this.unsubscribe),
                    distinctUntilChanged((prev, curr) => _.isEqual(prev, curr))
                )
                .subscribe(([objectRadius, objectColor, isStar, starScale, planetScale]) => {
                    let bodyRadius = objectRadius / Constants.CoordsScale;

                    if (Utils.FloatLE(bodyRadius, 0)) {
                        bodyGroup.removeFromParent();
                        return;
                    }

                    bodyGroup.clear();
                    rootGroup.add(bodyGroup);

                    if (isStar) {
                        bodyRadius *= starScale;

                        const pointLight = new THREE.PointLight(objectColor, 1);
                        bodyGroup.add(pointLight);
                        pointLight.castShadow = true;
                        pointLight.shadow.mapSize.width = 512; // default
                        pointLight.shadow.mapSize.height = 512; // default
                        pointLight.shadow.camera.near = 0.5; // default
                        pointLight.shadow.camera.far = 500; // default

                        const geometry = new THREE.SphereGeometry(bodyRadius, 32, 16);
                        const sphere = new THREE.Mesh(geometry, new THREE.MeshBasicMaterial({ color: objectColor }));
                        sphere.castShadow = true;

                        bodyGroup.add(sphere);
                    } else {
                        bodyRadius *= planetScale;
                        const geometry = new THREE.SphereGeometry(bodyRadius, 32, 16);
                        const sphere = new THREE.Mesh(geometry, new THREE.MeshLambertMaterial({ color: objectColor }));
                        bodyGroup.add(sphere);
                    }

                    Logger.info(
                        SSGSystemFilter.ModelBuilding,
                        `Building '${rootObject.Name}' with radius ${bodyRadius}`
                    );
                });
        });

        rootObject.OwnedObject(Constants.OrbiterInitialPositionSubscriber, () => {
            return rootObject.InitialOrbitalAngle$.pipe(
                takeUntil(this.unsubscribe),
                distinctUntilChanged(),
                tap((initialOrbitalAngle) => {
                    bodyOrbiter.initialAngle = initialOrbitalAngle;
                })
            );
        });

        rootObject.OwnedObject(Constants.OrbiterVelocitySubscriber, () => {
            return rootObject.OrbitalVelocity$.pipe(
                takeUntil(this.unsubscribe),
                distinctUntilChanged(),
                tap((orbitalVelocity) => {
                    bodyOrbiter.angVelDegPerSecond = orbitalVelocity;
                })
            );
        });

        rootObject.OwnedObject(Constants.RingSubscriber, () => {
            return combineLatest([
                rootObject.RingInnerRadius$,
                rootObject.RingWidth$,
                rootObject.RingDensity$,
                rootObject.RingColor$,
            ]).pipe(
                takeUntil(this.unsubscribe),
                distinctUntilChanged((prev, curr) => _.isEqual(prev, curr)),
                tap(([ringInnerRadius, ringWidth, ringDensity, ringColor]) => {
                    if (
                        Utils.FloatLE(ringInnerRadius, 0) ||
                        ringColor === Constants.COLOR_NONE ||
                        !rootObject.ParentObject
                    ) {
                        ringGroup.removeFromParent();
                        return;
                    }

                    rootGroup.add(ringGroup);
                    ringGroup.clear();

                    const ringThickness = 0.001;
                    ringDensity = Math.max(Math.min(ringDensity || 0.001, 1), 0);

                    const ringGeomInnerRadius = ringInnerRadius / Constants.CoordsScale;
                    const ringGeomWidth = ringWidth / Constants.CoordsScale;
                    const ringGeomOuterRadius = ringGeomInnerRadius + ringGeomWidth;
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

                    const outerRing = new THREE.Shape().absarc(0, 0, ringGeomOuterRadius, 0, Math.PI * 2, false);
                    const holePath = new THREE.Path().absarc(0, 0, ringGeomInnerRadius, 0, Math.PI * 2, true);
                    outerRing.holes.push(holePath);

                    const ringGeometry = new THREE.ExtrudeGeometry(outerRing, extrudeSettings);
                    const ringMaterial = THREEUtils.RingMaterialTextured(ringColor, ringDensity);
                    const edgeMaterial = new THREE.MeshLambertMaterial({ color: '#000000' });

                    const ringMesh = new THREE.Mesh(ringGeometry, [ringMaterial, edgeMaterial]);
                    ringMesh.receiveShadow = true;
                    THREEUtils.SetPosition(ringMesh, 0, 0, -ringGeomThickness / 2);

                    ringGroup.add(ringMesh);
                })
            );
        });

        /*

        for (const childObj of rootObject.ChildObjects) {
            const childGroup = this.buildSolarSystem(childObj);
            objectGroup.add(childGroup);
        }
*/
        return rootGroup;
    }

    private RenderGrid(
        sceneUpdated: THREE.Scene,
        gridType: string,
        gridSizeFactor: number,
        majorDivisions: number,
        minorDivisions: number,
        majorColor: string,
        minorColor: string
    ) {
        Logger.info(SSGSystemFilter.RenderDiagnostics, `Starting RenderGrid - gridType: ${gridType}`);

        this.gridContent.clear();

        if (!gridType || gridType == GRID_TYPE_NONE) {
            return;
        }

        const boundingBox = new THREE.Box3();
        boundingBox.setFromObject(this.systemScene);

        const gridSize =
            Math.max(boundingBox.max.x - boundingBox.min.x, boundingBox.max.y - boundingBox.min.y) * gridSizeFactor;

        if (!Number.isFinite(gridSize) || gridSize < 0) {
            return;
        }

        Logger.info(
            SSGSystemFilter.RenderDiagnostics,
            `Rendering ${gridType} grid with size ${gridSize}, factor: ${gridSizeFactor}`
        );

        let gridMesh: THREE.GridHelper | THREE.PolarGridHelper | undefined;

        if (gridType == GRID_TYPE_RECTANGULAR) {
            gridMesh = new THREE.GridHelper(gridSize, majorDivisions, majorColor, minorColor);
            gridMesh.rotation.x = Utils.DegreesToRadians(90);
            gridMesh.renderOrder = -1;
        }

        if (gridType == GRID_TYPE_POLAR) {
            gridMesh = new THREE.PolarGridHelper(
                gridSize / 2,
                minorDivisions,
                majorDivisions,
                64,
                majorColor,
                minorColor
            );
            gridMesh.rotation.x = Utils.DegreesToRadians(90);
            gridMesh.renderOrder = -1;
        }

        if (gridMesh) {
            this.gridContent.add(gridMesh as THREE.Object3D);
        }

        Logger.info(SSGSystemFilter.RenderDiagnostics, 'SSG Grid: ', this.gridScene);
    }

    public UpdateScene() {
        // Not impd yet
    }

    public FindObject(targetName?: string) {
        if (!targetName) {
            return undefined;
        }
        return this.systemScene.getObjectByName(targetName);
    }
}

export const SceneManager = SSGSceneManager.Instance;
