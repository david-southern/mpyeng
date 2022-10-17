import { SSGSettings, EmptySettings } from './ssg.settings';

type SettingsCB = (settings: SSGSettings) => void;

class SettingsManagerImpl {
    public CurrentSettings: SSGSettings = EmptySettings;
    public PrevSettings: SSGSettings = EmptySettings;;

    private settingsCallbacks: SettingsCB[] = [];

    public publishSettings(newSettings: SSGSettings) {
        this.PrevSettings = this.CurrentSettings;
        this.CurrentSettings = newSettings;

        for (const nextCB of this.settingsCallbacks) {
            nextCB(newSettings);
        }
    }

    public subscribeSettings = (settingsCB: SettingsCB) => {
        if (settingsCB) {
            this.settingsCallbacks.push(settingsCB);
        }
    };

    public clearSettingsSubscriptions = () => {
        this.settingsCallbacks = [];
    }
};

export const SettingsManager = new SettingsManagerImpl();
