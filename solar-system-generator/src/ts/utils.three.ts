import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { Logger, SSGSystemFilter } from './logger';
import { Utils } from './utils';

export class THREEUtils {
    public static DumpVec(vec: THREE.Vector2 | THREE.Vector3): string {
        return vec instanceof THREE.Vector2 ? `(${vec.x}, ${vec.y})` : `(${vec.x}, ${vec.y}, ${vec.z})`;
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

    public static RingMaterialTextured(ringColor: string, density = 0.1) {
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

        const texture = new THREE.DataTexture(data, width, height);
        texture.needsUpdate = true;

        texture.wrapS = THREE.RepeatWrapping;
        texture.wrapT = THREE.RepeatWrapping;

        return new THREE.MeshLambertMaterial({
            alphaMap: texture,
            color: ringColor,
            transparent: true,
        });
    }

    public static FitCameraToObject(
        baseScene: THREE.Scene,
        camera: THREE.PerspectiveCamera,
        aspectRatio: number,
        orbitControls?: OrbitControls,
        lookAtTarget?: THREE.Object3D
    ) {
        const offset = 1.25;

        const boundingBox = new THREE.Box3();

        // get bounding box of object - this will be used to setup controls and camera
        boundingBox.setFromObject(baseScene);

        Logger.info(
            SSGSystemFilter.RenderDiagnostics,
            `fitCamera: Object boundingBox: min: ${THREEUtils.DumpVec(boundingBox.min)}, max: ${THREEUtils.DumpVec(
                boundingBox.max
            )}`
        );

        const center = new THREE.Vector3();
        const size = new THREE.Vector3();

        boundingBox.getCenter(center);
        boundingBox.getSize(size);

        Logger.info(
            SSGSystemFilter.RenderDiagnostics,
            `fitCamera: Object boundingBox: center: ${THREEUtils.DumpVec(center)}, size: ${THREEUtils.DumpVec(size)}`
        );

        // get the max side of the bounding box (fits to width OR height as needed )
        const fov = camera.fov * (Math.PI / 180);

        Logger.info(SSGSystemFilter.RenderDiagnostics, `fitCamera: aspect ratio: ${aspectRatio}, FOV: ${camera.fov}`);

        const ySize = Math.max(size.y, size.x / aspectRatio);

        Logger.info(SSGSystemFilter.RenderDiagnostics, `fitCamera: target Y Size: ${ySize}`);

        let cameraYDistance = Math.abs(ySize / 2 / Math.tan(fov / 2));

        Logger.info(SSGSystemFilter.RenderDiagnostics, `fitCamera: camera Y: ${cameraYDistance}`);
        Logger.info(
            SSGSystemFilter.RenderDiagnostics,
            `fitCamera: calc fov: ${Utils.RadiansToDegrees(Math.atan(ySize / 2 / cameraYDistance))} deg`
        );

        cameraYDistance *= offset; // zoom out a little so that objects don't fill the screen

        // Adjust the camera so that the leading edge of the scene is fully in the view
        const cameraDistance = cameraYDistance + boundingBox.max.z;

        const minZ = boundingBox.min.z;
        const cameraToFarEdge = minZ < 0 ? -minZ + cameraDistance : cameraDistance - minZ;

        Logger.info(
            SSGSystemFilter.RenderDiagnostics,
            `New camera params: Z: ${cameraDistance}, FAR: ${cameraToFarEdge * 3}`
        );

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
