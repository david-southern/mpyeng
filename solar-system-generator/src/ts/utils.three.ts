import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { Logger, SSGSystemFilter } from './ssg.logger';
import { Utils } from './utils';

export class THREEUtils {
    public static DumpVec(vec: THREE.Vector2 | THREE.Vector3): string {
        return (vec instanceof THREE.Vector2) ? `(${vec.x}, ${vec.y})` : `(${vec.x}, ${vec.y}, ${vec.z})`;
    }

    public static SetPosition(object3d: THREE.Object3D, x: number | THREE.Vector3, y?: number, z?: number) {
        if (typeof x === 'number') {
            object3d.position.x = x;
            object3d.position.y = y ?? 0;
            object3d.position.z = z ?? 0;
        } else {
            object3d.position.x = x.x;
            object3d.position.y = x.y;
            object3d.position.z = x.z;
        }
    }
    public static PlanetMaterial(color: string) {
        return new THREE.MeshLambertMaterial({ color });
    }

    public static StarMaterial(color: string) {
        return new THREE.MeshBasicMaterial({ color });
        // return new THREE.MeshLambertMaterial({ emissive: color });
    }

    public static OrbitalMaterial(color: string) {
        return new THREE.LineBasicMaterial({ color });
    }

    public static BuildOrbitalEllipse(x: number, y: number, xRadius: number, yRadius: number): THREE.EllipseCurve {
        const startAngle = 0;
        const endAngle = 2 * Math.PI;
        const clockwiseDirection = false;

        return new THREE.EllipseCurve(x, y, xRadius, yRadius, startAngle, endAngle, clockwiseDirection, 0);
    }

    public static BuildOrbitalMesh(x: number, y: number, z: number, curve: THREE.EllipseCurve, color: string) {
        const points = curve.getPoints(250);
        const geometry = new THREE.BufferGeometry().setFromPoints(points);

        // Create the final object to add to the scene
        const ellipse = new THREE.Line(geometry, THREEUtils.OrbitalMaterial(color));
        THREEUtils.SetPosition(ellipse, x, y, z);

        return ellipse;
    }

    public static BuildPlanet(x: number, y: number, z: number, radius: number, color: string) {
        const geometry = new THREE.SphereGeometry(radius, 32, 16);
        const sphere = new THREE.Mesh(geometry, THREEUtils.PlanetMaterial(color));

        THREEUtils.SetPosition(sphere, x, y, z);

        return sphere;
    }

    public static BuildStar(x: number, y: number, z: number, radius: number, color: string) {
        const starGroup = new THREE.Group();

        const pointLight = new THREE.PointLight(color, 1);
        starGroup.add(pointLight)

        const geometry = new THREE.SphereGeometry(radius, 32, 16);
        const sphere = new THREE.Mesh(geometry, THREEUtils.StarMaterial(color));
        THREEUtils.SetPosition(sphere, x, y, z);

        pointLight.castShadow = true;
        pointLight.shadow.mapSize.width = 512; // default
        pointLight.shadow.mapSize.height = 512; // default
        pointLight.shadow.camera.near = 0.5; // default
        pointLight.shadow.camera.far = 500; // default        

        starGroup.add(sphere);

        return starGroup;
    }

    public static ZZZBuildGrid(size: number, divisions: number, centerColor: string, lineColor: string) {
        const gridHelper = new THREE.GridHelper(size, divisions, centerColor, lineColor);
        gridHelper.rotation.x = Utils.DegreesToRadians(90);
        gridHelper.renderOrder = -1;

        return gridHelper;
    }

    public static ZZZBuildPolarGrid(radius: number, sectors: number, rings: number, divisions: number,
        color1: string, color2: string) {

        const gridHelper = new THREE.PolarGridHelper(radius, sectors, rings, divisions, color1, color2);
        gridHelper.rotation.x = Utils.DegreesToRadians(90);
        gridHelper.renderOrder = -1;

        return gridHelper;
    }


    public static FitCameraToObject(baseScene: THREE.Scene,
        camera: THREE.PerspectiveCamera,
        aspectRatio: number, orbitControls?: OrbitControls,
        lookAtTarget?: THREE.Object3D) {
        const offset = 1.25;

        const boundingBox = new THREE.Box3();

        // get bounding box of object - this will be used to setup controls and camera
        boundingBox.setFromObject(baseScene);

        Logger.info(SSGSystemFilter.RenderDiagnostics, `fitCamera: Object boundingBox: min: ${THREEUtils.DumpVec(boundingBox.min)}, max: ${THREEUtils.DumpVec(boundingBox.max)}`);

        const center = new THREE.Vector3();
        const size = new THREE.Vector3();

        boundingBox.getCenter(center);
        boundingBox.getSize(size);

        Logger.info(SSGSystemFilter.RenderDiagnostics, `fitCamera: Object boundingBox: center: ${THREEUtils.DumpVec(center)}, size: ${THREEUtils.DumpVec(size)}`);

        // get the max side of the bounding box (fits to width OR height as needed )
        const maxDim = Math.max(size.x, size.y, size.z);
        const fov = camera.fov * (Math.PI / 180);

        Logger.info(SSGSystemFilter.RenderDiagnostics, `fitCamera: aspect ratio: ${aspectRatio}, FOV: ${camera.fov}`);

        let ySize = Math.max(size.y, size.x / aspectRatio);

        Logger.info(SSGSystemFilter.RenderDiagnostics, `fitCamera: target Y Size: ${ySize}`);

        let cameraYDistance = Math.abs((ySize / 2) / Math.tan(fov / 2));

        Logger.info(SSGSystemFilter.RenderDiagnostics, `fitCamera: camera Y: ${cameraYDistance}`);
        Logger.info(SSGSystemFilter.RenderDiagnostics, `fitCamera: calc fov: ${Utils.RadiansToDegrees(Math.atan((ySize / 2) / cameraYDistance))} deg`);

        cameraYDistance *= offset; // zoom out a little so that objects don't fill the screen

        // Adjust the camera so that the leading edge of the scene is fully in the view
        const cameraDistance = cameraYDistance + boundingBox.max.z;

        const minZ = boundingBox.min.z;
        const cameraToFarEdge = (minZ < 0) ? -minZ + cameraDistance : cameraDistance - minZ;

        Logger.info(SSGSystemFilter.RenderDiagnostics, `New camera params: Z: ${cameraDistance}, FAR: ${cameraToFarEdge * 3}`);

        camera.position.z = cameraDistance;
        camera.far = cameraToFarEdge * 3;
        camera.updateProjectionMatrix();

        Logger.info(SSGSystemFilter.RenderDiagnostics, `fitCamera: effective FOV: ${camera.getEffectiveFOV()}`);

        if (orbitControls) {
            // prevent camera from zooming out far enough to create far plane cutoff
            orbitControls.maxDistance = cameraToFarEdge * 2;
            orbitControls.saveState();

            // set camera to rotate around the target
            const lookAtVec = new THREE.Vector3(0, 0, 0);
            if (lookAtTarget) {
                lookAtTarget.getWorldPosition(lookAtVec);
            }
            orbitControls.target = lookAtVec;
            orbitControls.update();
        }
    }
}
