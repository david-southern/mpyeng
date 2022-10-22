import { Logger, SSGSystemFilter } from "./ssg.logger";
import { Utils } from "./utils";
import { SimTimeManager } from "./ssg.simtime.manager";

export class SSGCanvasManager {
    public static readonly CanvasDivID = "system-canvas";
    public static readonly SystemTimeDivID = "system-time";

    private static _Instance = new SSGCanvasManager();
    public static get Instance() {
        return SSGCanvasManager._Instance;
    }

    // Make the constructor private to signal that SSGRxSettings is a singleton
    public constructor() {
        this.canvasElement = Utils.SafeGetElement(SSGCanvasManager.CanvasDivID);
        this.systemTimeElement = Utils.SafeGetElement(SSGCanvasManager.SystemTimeDivID);

        this.canvasWidth = this.canvasElement.offsetWidth;
        this.canvasHeight = this.canvasElement.offsetHeight;
        this.canvasAspect = this.canvasWidth / this.canvasHeight;

        const rect = this.canvasElement.getBoundingClientRect();

        Logger.info(SSGSystemFilter.Initialization, `Initializing SSG window @(${rect.left}, ${rect.top}), `
            + `size: (${this.canvasWidth} x ${this.canvasHeight}), aspect: ${this.canvasAspect}`);

        SimTimeManager.Tick$.subscribe(() => {
            this.SetSystemTime("System Time: " + Utils.HumanTime(SimTimeManager.SimTime));
        });
    }

    private canvasElement: HTMLElement;
    private systemTimeElement: HTMLElement;

    private canvasWidth: number;
    public get CanvasWidth() {
        return this.canvasWidth;
    }

    private canvasHeight: number;
    public get CanvasHeight() {
        return this.canvasHeight;
    }

    private canvasAspect: number;
    public get CanvasAspect() {
        return this.canvasAspect;
    }

    public AddRenderElement(renderElement: HTMLElement) {
        this.canvasElement.appendChild(renderElement);
    }

    public SetSystemTime(systemTime: string) {
        this.systemTimeElement.innerHTML = systemTime;
    }
}

export const CanvasManager = SSGCanvasManager.Instance;
