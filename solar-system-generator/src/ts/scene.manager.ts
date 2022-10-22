import _ from 'lodash';
import { combineLatest, ReplaySubject, Subject, takeUntil } from 'rxjs';
import * as THREE from 'three';
import { CelestialObject } from './celestial-object';
import { GlobalSettings, GRID_TYPE_NONE, GRID_TYPE_POLAR, GRID_TYPE_RECTANGULAR } from './ssg.settings';
import { SimTimeManager } from './ssg.simtime.manager';
import { Utils } from './utils';
import { THREEUtils } from './utils.three';

export class SSGSceneManager {
    private static _Instance = new SSGSceneManager();
    public static get Instance() {
        return SSGSceneManager._Instance;
    }

    public SceneUpdated$ = new ReplaySubject<THREE.Scene>(1);

    // Make the constructor private to signal that SSGRxSettings is a singleton
    private constructor() {
        this.systemScene = new THREE.Scene();
        this.systemScene.name = 'SSG-root';

        this.gridScene = new THREE.Scene();
        this.systemScene.name = 'Grid-root';

        this.ambientLight = new THREE.AmbientLight();
        this.systemScene.add(this.ambientLight);

        this.directionalLight = new THREE.DirectionalLight();
        this.systemScene.add(this.directionalLight);

        GlobalSettings.SystemRoot$.pipe(takeUntil(this.unsubscribe))
            .subscribe(rootObject => this.RenderSystem(rootObject));

        combineLatest([
            this.SceneUpdated$, GlobalSettings.GridType$, GlobalSettings.GridSizeFactor$,
            GlobalSettings.GridMajorDivisions$, GlobalSettings.GridMinorDivisions$,
            GlobalSettings.GridMajorColor$, GlobalSettings.GridMinorColor$
        ]).pipe(takeUntil(this.unsubscribe))
            .subscribe(([
                sceneUpdated, gridType, gridSizeFactor,
                majorDivisions, minorDivisions,
                majorColor, minorColor
            ]) => {
                this.RenderGrid(sceneUpdated, gridType, gridSizeFactor,
                    majorDivisions, minorDivisions,
                    majorColor, minorColor);
            });
    }

    public Destroy() {
        this.unsubscribe.next();
        this.unsubscribe.complete();
    }

    private unsubscribe = new Subject<void>();

    private systemScene: THREE.Scene;
    public get SystemScene() {
        return this.systemScene;
    }
    private systemContent?: THREE.Group;

    private gridScene: THREE.Scene;
    public get GridScene() {
        return this.gridScene;
    }
    private gridContent?: THREE.Group;

    private ambientLight: THREE.AmbientLight;
    private directionalLight: THREE.DirectionalLight;

    private RenderSystem(rootObject?: CelestialObject) {
        let sceneUpdated = false;

        try {
            if (this.systemContent) {
                this.systemContent.removeFromParent();
                this.systemContent = undefined;
                sceneUpdated = true;
            }

            if (!rootObject) {
                return;
            }
        }
        finally {
            if (sceneUpdated) {
                this.SceneUpdated$.next(true);
            }
        }
    }

    private RenderGrid(sceneUpdated: THREE.Scene, gridType: string, gridSizeFactor: number,
        majorDivisions: number, minorDivisions: number, majorColor: string, minorColor: string) {
        if (this.gridContent) {
            this.gridContent.removeFromParent();
            this.gridContent = undefined;
        }

        if (!gridType || gridType == GRID_TYPE_NONE) {
            return;
        }

        this.gridContent = new THREE.Group();
        this.gridContent.name = 'SSG-system-grid';

        const boundingBox = new THREE.Box3();
        boundingBox.setFromObject(this.systemScene);

        const gridSize = Math.max(boundingBox.max.x - boundingBox.min.x, boundingBox.max.y - boundingBox.min.y)
            * GlobalSettings.GridSizeFactor;

        let gridMesh;

        if (gridType == GRID_TYPE_RECTANGULAR) {
            const gridHelper = new THREE.GridHelper(gridSize, GlobalSettings.GridMajorDivisions,
                GlobalSettings.GridMajorColor, GlobalSettings.GridMinorColor);
            gridHelper.rotation.x = Utils.DegreesToRadians(90);
            gridHelper.renderOrder = -1;
        }

        if (gridType == GRID_TYPE_POLAR) {
            const gridHelper = new THREE.PolarGridHelper(gridSize / 2,
                GlobalSettings.GridMinorDivisions, GlobalSettings.GridMajorDivisions, 64,
                GlobalSettings.GridMajorColor, GlobalSettings.GridMinorColor);
            gridHelper.rotation.x = Utils.DegreesToRadians(90);
            gridHelper.renderOrder = -1;
        }

        if (gridMesh) {
            this.gridContent.add(gridMesh);
        }
    }

    public UpdateScene() {
    }

    public FindObject(targetName?: string) {
        if (!targetName) {
            return undefined;
        }
        return this.systemScene.getObjectByName(targetName);
    }
}

export const SceneManager = SSGSceneManager.Instance;