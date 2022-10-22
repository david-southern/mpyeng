export enum SSGSystemFilter {
    Initialization,
    RenderSettings,
    RenderDiagnostics,
    ExportDiagnostics,
    ModelBuilding,
    TimingDiagnostics,
    Always
}

const shortSource = new Map<string, string>([
    [SSGSystemFilter[SSGSystemFilter.Initialization], "Init"],
    [SSGSystemFilter[SSGSystemFilter.RenderSettings], "RS"],
    [SSGSystemFilter[SSGSystemFilter.RenderDiagnostics], "RD"],
    [SSGSystemFilter[SSGSystemFilter.ExportDiagnostics], "Exp"],
    [SSGSystemFilter[SSGSystemFilter.ModelBuilding], "MB"],
    [SSGSystemFilter[SSGSystemFilter.TimingDiagnostics], "TD"],
    [SSGSystemFilter[SSGSystemFilter.Always], "All"],
]);

class LoggerImpl {
    private filteredSystems = new Map<SSGSystemFilter, boolean>();

    constructor() {
        // this.filterSystem(SSGSystemFilter.RenderSettings, false);

        // this.filterSystem(SSGSystemFilter.Initialization, false);
        // this.filterSystem(SSGSystemFilter.RenderDiagnostics, false);
        this.filterSystem(SSGSystemFilter.ExportDiagnostics, false);
        // this.filterSystem(SSGSystemFilter.ModelBuilding, false);
        // this.filterSystem(SSGSystemFilter.TimingDiagnostics, false);
    }

    public filterSystem(system: SSGSystemFilter, allow = false) {
        this.filteredSystems.set(system, !allow);
    }

    public wouldLog(system: SSGSystemFilter): boolean {
        return system == SSGSystemFilter.Always || !this.filteredSystems.get(system);
    }

    public info(system: SSGSystemFilter, message: string, ...args: any[]) {
        if (this.wouldLog(system)) {
            const source = shortSource.get(SSGSystemFilter[system]) ?? SSGSystemFilter[system];
            console.log(`${source}: ${message}`, ...args);
        }
    }

    public error(system: SSGSystemFilter, message: string, ...args: any[]) {
        const source = shortSource.get(SSGSystemFilter[system]) ?? SSGSystemFilter[system];
        console.error(`${source}: ${message}`, ...args);
    }
}

export const Logger = new LoggerImpl();