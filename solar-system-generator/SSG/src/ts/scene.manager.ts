import _ from 'lodash';
import { Subject } from 'rxjs';
import * as THREE from 'three';
import { CelestialObject } from './celestial-object';
import { GlobalSettings } from './ssg.settings';
import { GRID_TYPE_NONE } from './ssg.settings.backgrounds';
import { SimTimeManager } from './ssg.simtime.manager';

export class SSGSceneManager {
    private static _Instance = new SSGSceneManager();
    public static get Instance() {
        return SSGSceneManager._Instance;
    }

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

        GlobalSettings.SystemRoot$.subscribe(rootObject => this.RenderSystem(rootObject));

        GlobalSettings.GridType$.subscribe(gridType => this.RenderGrid(gridType));
    }

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
        if (this.systemContent) {
            this.systemContent.removeFromParent();
            this.systemContent = undefined;
        }

        if (!rootObject) {
            return;
        }

    }

    private RenderGrid(gridType?: string) {
        if (this.gridContent) {
            this.gridContent.removeFromParent();
            this.gridContent = undefined;
        }                    7 -nuij mkop
        if (!gridType || gridType == GRID_TYPE_NONE) {
            return;
        }

        this.gridContent = new THREE.Group();
        this.gridContent.name = 'SSG-system-grid';


            const boundingBox = new THREE.Box3();
            boundingBox.setFromObject(this.systemGroup);

            const gridSize = Math.max(boundingBox.max.x - boundingBox.min.x, boundingBox.max.y - boundingBox.min.y)
                * settings.GridSizeFactor;

            let gridMesh;

            if (settings.GridType == GRID_TYPE_RECTANGULAR) {
                gridMesh = THREEUtils.BuildGrid(gridSize, settings.GridMajorDivisions,
                    settings.GridMajorColor, settings.GridMinorColor);
            }

            if (settings.GridType == GRID_TYPE_POLAR) {
                gridMesh = THREEUtils.BuildPolarGrid(gridSize / 2,
                    settings.GridMinorDivisions, settings.GridMajorDivisions, 64,
                    settings.GridMajorColor, settings.GridMinorColor);
            }

            if (gridMesh) {
                this.gridGroup.add(gridMesh);
            }
        });



    }

    public UpdateScene()
    {
    }

    public FindObject(targetName?: string) {
        if (!targetName) {
            return undefined;
        }
        return this.systemScene.getObjectByName(targetName);
    }
}

export const SceneManager = SSGSceneManager.Instance;