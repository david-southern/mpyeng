import { SSGOldSettings, EmptySettings } from "./zzz.settings";

type SettingsCB = (settings: SSGOldSettings) => void;

class SettingsManagerImpl
{
    public CurrentSettings: SSGOldSettings = EmptySettings;
    public PrevSettings: SSGOldSettings = EmptySettings;

    private settingsCallbacks: SettingsCB[] = [];

    public publishSettings(newSettings: SSGOldSettings)
    {
        this.PrevSettings = this.CurrentSettings;
        this.CurrentSettings = newSettings;

        for (const nextCB of this.settingsCallbacks)
        {
            nextCB(newSettings);
        }
    }

    public subscribeSettings = (settingsCB: SettingsCB) =>
    {
        this.settingsCallbacks.push(settingsCB);
    };

    public clearSettingsSubscriptions = () =>
    {
        this.settingsCallbacks = [];
    };
}

export const SettingsManager = new SettingsManagerImpl();
