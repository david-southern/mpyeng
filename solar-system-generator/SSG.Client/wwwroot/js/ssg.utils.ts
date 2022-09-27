import * as THREE from 'three';

export interface Vector3 {
    X: number;
    Y: number;
    Z: number;
}

export class Constants {
    public static OneAU = 1.496e11;
    public static SolarMass = 1.989e30;
    public static SolarRadius = 6.960e8;
    public static EarthMass = 5.974e24;
    public static EarthRadius = 6.378e6;
}

export class Utils {
    public static setPosition(object3d: THREE.Object3D, x: number, y: number, z: number) {
        object3d.position.x = x;
        object3d.position.y = y;
        object3d.position.z = z;
    }

    public static degreesToRadians(degrees: number) {
        return (degrees / 180) * Math.PI;
    }

    /**
     * Normalize a planetary radius with 1 = EarthRadius
     * @param rawRadius
     */
    public static normalizePlanetaryRadius(rawRadius: number): number {
        return rawRadius / Constants.EarthRadius;
    }

    /**
     * Normalize a orbital radius with 1 = One AU
     * @param rawRadius
     */
    public static normalizeOrbitalRadius(rawRadius: number): number {
        return rawRadius / Constants.OneAU;
    }

    /**
     * Normalize a planetary mass with 1 = EarthMass
     * @param rawMass
     */
    public static normalizePlanetaryMass(rawMass: number): number {
        return rawMass / Constants.EarthMass;
    }

    public static planetMaterial(color: string) {
        return new THREE.MeshLambertMaterial({ color });
    }

    public static starMaterial(color: string) {
        return new THREE.MeshLambertMaterial({ emissive: color });
    }

    public static orbitalMaterial(color: string) {
        return new THREE.LineBasicMaterial({ color });
    }

    public static buildEllipse(x: number, y: number, z: number, xrad: number, yrad: number, color: string, inclination: number = 0) {
        const startAngle = 0;
        const endAngle = 2 * Math.PI;
        const clockwiseDirection = false;

        const curve = new THREE.EllipseCurve(x, y, xrad, yrad, startAngle, endAngle, clockwiseDirection, inclination);

        const points = curve.getPoints(250);
        const geometry = new THREE.BufferGeometry().setFromPoints(points);

        // Create the final object to add to the scene
        const ellipse = new THREE.Line(geometry, Utils.orbitalMaterial(color));
        Utils.setPosition(ellipse, x, y, z);

        return ellipse;
    }

    public static buildPlanet(x: number, y: number, z: number, radius: number, color: string) {
        const geometry = new THREE.SphereGeometry(radius, 32, 16);
        const sphere = new THREE.Mesh(geometry, Utils.planetMaterial(color));
        Utils.setPosition(sphere, x, y, z);

        return sphere;
    }

    public static buildStar(x: number, y: number, z: number, radius: number, color: string) {
        const starGroup = new THREE.Group();

        const pointLight = new THREE.PointLight(color, 1);
        starGroup.add(pointLight)

        const geometry = new THREE.SphereGeometry(radius, 32, 16);
        const sphere = new THREE.Mesh(geometry, Utils.starMaterial(color));
        Utils.setPosition(sphere, x, y, z);

        starGroup.add(sphere);

        return starGroup;
    }

    public static buildGrid(size: number, divisions: number, centerColor: string, lineColor: string) {
        const gridHelper = new THREE.GridHelper(size, divisions, centerColor, lineColor);
        gridHelper.rotation.x = Utils.degreesToRadians(90);
        gridHelper.renderOrder = -1;

        return gridHelper;
    }

    public static buildPolarGrid(radius: number, sectors: number, rings: number, divisions: number,
        color1: string, color2: string) {

        const gridHelper = new THREE.PolarGridHelper(radius, sectors, rings, divisions, color1, color2);
        gridHelper.rotation.x = Utils.degreesToRadians(90);
        gridHelper.renderOrder = -1;

        return gridHelper;
    }
}

