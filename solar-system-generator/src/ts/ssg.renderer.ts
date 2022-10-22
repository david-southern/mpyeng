import _ from "lodash";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls";

import * as PP from "postprocessing";

import { Logger, SSGSystemFilter } from "./ssg.logger";
import { Utils } from "./utils";
import { SimTimeManager, SSGSimTimeManager } from "./ssg.simtime.manager";
import { SSGSettings } from "./ssg.settings";
import { DefaultBackgroundImage } from "./ssg.settings.backgrounds";
import { firstValueFrom } from "rxjs";
import { THREEUtils } from "./utils.three";
import { CanvasManager } from "./canvas.manager";
import { CameraManager } from "./camera.manager";
import { SceneManager } from "./scene.manager";

const DEFAULT_FOV = 30;
const DEFAULT_ASPECT = 1.61;

export class SSGRenderer {
    private renderer: THREE.WebGLRenderer;
    private loader: THREE.TextureLoader;
    private composer: PP.EffectComposer;
    private textureEffect: PP.TextureEffect;
    private backgroundAdjustEffect: PP.BrightnessContrastEffect;

    public constructor() {
        this.renderer = new THREE.WebGLRenderer({
            powerPreference: "high-performance",
            antialias: false,
            stencil: false,
            depth: false
        });
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.renderer.setSize(CanvasManager.CanvasWidth, CanvasManager.CanvasHeight);
        CameraManager.SetRenderElement(this.renderer.domElement);

        this.loader = new THREE.TextureLoader();

        this.composer = new PP.EffectComposer(this.renderer);

        // Clear the renderer to start
        this.composer.addPass(new PP.ClearPass());

        // Display the background
        const defaultTexture = this.loader.load(DefaultBackgroundImage.URL);
        this.textureEffect = new PP.TextureEffect({
            texture: defaultTexture
        });
        this.composer.addPass(new PP.EffectPass(CameraManager.Camera, this.textureEffect));

        // Adjust the background contrast/brightness
        this.backgroundAdjustEffect = new PP.BrightnessContrastEffect();
        this.composer.addPass(new PP.EffectPass(CameraManager.Camera, this.backgroundAdjustEffect));

        // We want the grid to render behind the scene geometry, so render it separately from the scene, clearing only
        // the depth buffer between renders.
        const gridRenderPass = new PP.RenderPass(SceneManager.GridScene, CameraManager.Camera);
        this.composer.addPass(gridRenderPass);
        gridRenderPass.clearPass.enabled = false;
        gridRenderPass.ignoreBackground = true;

        // Clear the depth buffer so that the system scene will render 'in front' of the grid scene
        this.composer.addPass(new PP.ClearPass(false, true, false));
        const sceneRenderPass = new PP.RenderPass(SceneManager.SystemScene, CameraManager.Camera);
        sceneRenderPass.clearPass.enabled = false;
        sceneRenderPass.ignoreBackground = true;
        this.composer.addPass(sceneRenderPass);

        // Can I remove this?  Originally, the previous passes did not display correctly until I added this EffectPass...
        this.composer.addPass(new PP.EffectPass(CameraManager.Camera, new PP.ColorDepthEffect({ bits: 32 })));

        CanvasManager.AddRenderElement(this.renderer.domElement);

        this.getNextAnimationFrame();
    }

    private getNextAnimationFrame() {
        requestAnimationFrame((animationTime: DOMHighResTimeStamp) => { this.updateAnimation(animationTime); });
    }

    private async updateAnimation(actualMillis: number) {
        await SimTimeManager.UpdateSimTime(actualMillis);
        CameraManager.UpdateCamera();
        SceneManager.UpdateScene();

        this.composer.render();

        this.getNextAnimationFrame();
    }
}
