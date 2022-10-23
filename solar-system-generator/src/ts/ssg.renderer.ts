import * as THREE from "three";
import * as PP from "postprocessing";

import { SimTimeManager } from "./ssg.simtime.manager";
import { DefaultBackgroundImage } from "./ssg.settings.backgrounds";
import { CanvasManager } from "./canvas.manager";
import { CameraManager } from "./camera.manager";
import { SceneManager } from "./scene.manager";

export class SSGRenderer
{
    private renderer: THREE.WebGLRenderer;
    private loader: THREE.TextureLoader;
    private composer: PP.EffectComposer;
    private textureEffect: PP.TextureEffect;
    private backgroundAdjustEffect: PP.BrightnessContrastEffect;

    public constructor()
    {
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

    private getNextAnimationFrame()
    {
        requestAnimationFrame((animationTime: DOMHighResTimeStamp) =>
        {
            // We don't care that updateAnimation is async here
            void this.updateAnimation(animationTime);
        });
    }

    private async updateAnimation(actualMillis: number)
    {
        await SimTimeManager.UpdateSimTime(actualMillis);
        CameraManager.UpdateCamera();
        SceneManager.UpdateScene();

        this.composer.render();

        this.getNextAnimationFrame();
    }
}
