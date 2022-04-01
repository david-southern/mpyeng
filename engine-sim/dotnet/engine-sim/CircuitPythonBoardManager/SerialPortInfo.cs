// warning CA1416: This call site is reachable on all platforms. 'ManagementBaseObject.GetPropertyValue(string)' is only supported on: 'windows'.
#pragma warning disable CA1416
//#define ADDITIONAL_PORT_PROPS

using System.Management;

namespace CircuitPythonInterface;

public class SerialPortInfo
{
    public static List<SerialPortInfo> GetPortInformation(bool showRawData = false)
    {
        List<SerialPortInfo> retval = new();

        ManagementClass processClass = new("Win32_PnPEntity");
        ManagementObjectCollection Ports = processClass.GetInstances();

        foreach (ManagementObject property in Ports)
        {
            string? name = property.GetPropertyValue("Name")?.ToString();
            if (name != null && name.ToString().Contains("USB") && name.ToString().Contains("COM"))
            {
                SerialPortInfo? portInfo = new(property);

                // Only include ports for which we can resolve the MI, all other ports are not CircuitPyton boards
                if (portInfo?.MI != null)
                {
                    retval.Add(portInfo);
                }

                if (showRawData)
                {
                    Logger.Info($"Raw Serial Data:");
                    Logger.Info($"        Name: {name}");
                    Logger.Info($"        DeviceID: {portInfo?.DeviceID ?? "<null>"}");
                }
            }
        }

        return retval;
    }

    public SerialPortInfo(ManagementObject property)
    {
        Name = property.GetPropertyValue("Name") as string ?? string.Empty;
        DeviceID = property.GetPropertyValue("DeviceID") as string ?? string.Empty;
        PortName = null;

        // CircuitPython boards all have a name of the form <description>(COMXX) - If we can't find
        // the COMXX then it's not a CPy board
        if (!string.IsNullOrEmpty(Name))
        {
            int portStart = Name.IndexOf("COM");
            PortName = portStart < 0 ? null : Name.Substring(portStart, Name.IndexOf(")", portStart) - portStart);
        }

        if (PortName != null)
        {
            // CPy boards have a DeviceID that looks like this:
            // * USB\VID_239A&PID_80F2&MI_00\6&6E93409&0&0000 For each model (VID/PID) of board,
            //   only the MI part appears to be different.  Parse that and use it to identify the
            //   boards.
            string[] idParts = DeviceID.Split("\\");

            if (idParts.Length == 3 && idParts[0] == "USB")
            {
                string[] vpmParts = idParts[1].Split("&");

                if (vpmParts.Length == 3)
                {
                    VID = vpmParts[0];
                    PID = vpmParts[1];
                    MI = vpmParts[2];
                    AddlID = idParts[2];
                }
            }
        }

#if ADDITIONAL_PORT_PROPS
        SetAdditionalProps(property);
#endif
    }

    public string Name;
    public string DeviceID;

    public string? PortName;
    public string? VID;
    public string? PID;
    public string? MI;
    public string? AddlID;

    public override string ToString()
    {
        return string.IsNullOrEmpty(PortName) ? $"{DeviceID}//{Name}"
            : $"{PortName} // VID: {VID}, PID: {PID}, MI: {MI}, Addl: {AddlID}";
    }

#if ADDITIONAL_PORT_PROPS
    int Availability;
    string Caption;
    string ClassGuid;
    string[] CompatibleID;
    int ConfigManagerErrorCode;
    bool ConfigManagerUserConfig;
    string CreationClassName;
    string Description;
    bool ErrorCleared;
    string ErrorDescription;
    string[] HardwareID;
    DateTime InstallDate;
    int LastErrorCode;
    string Manufacturer;
    string PNPClass;
    string PNPDeviceID;
    int[] PowerManagementCapabilities;
    bool PowerManagementSupported;
    bool Present;
    string Service;
    string Status;
    int StatusInfo;
    string SystemCreationClassName;
    string SystemName;

    private void SetAdditionalProps(ManagementObject property)
    {
        Availability = property.GetPropertyValue("Availability") as int? ?? 0;
        Caption = property.GetPropertyValue("Caption") as string ?? string.Empty;
        ClassGuid = property.GetPropertyValue("ClassGuid") as string ?? string.Empty;
        CompatibleID = property.GetPropertyValue("CompatibleID") as string[] ?? new string[] { };
        ConfigManagerErrorCode = property.GetPropertyValue("ConfigManagerErrorCode") as int? ?? 0;
        ConfigManagerUserConfig = property.GetPropertyValue("ConfigManagerUserConfig") as bool? ?? false;
        CreationClassName = property.GetPropertyValue("CreationClassName") as string ?? string.Empty;
        Description = property.GetPropertyValue("Description") as string ?? string.Empty;
        ErrorCleared = property.GetPropertyValue("ErrorCleared") as bool? ?? false;
        ErrorDescription = property.GetPropertyValue("ErrorDescription") as string ?? string.Empty;
        HardwareID = property.GetPropertyValue("HardwareID") as string[] ?? new string[] { };
        InstallDate = property.GetPropertyValue("InstallDate") as DateTime? ?? DateTime.MinValue;
        LastErrorCode = property.GetPropertyValue("LastErrorCode") as int? ?? 0;
        Manufacturer = property.GetPropertyValue("Manufacturer") as string ?? string.Empty;
        PNPClass = property.GetPropertyValue("PNPClass") as string ?? string.Empty;
        PNPDeviceID = property.GetPropertyValue("PNPDeviceID") as string ?? string.Empty;
        PowerManagementCapabilities = property.GetPropertyValue("PowerManagementCapabilities") as int[] ?? new int[] { };
        PowerManagementSupported = property.GetPropertyValue("PowerManagementSupported") as bool? ?? false;
        Present = property.GetPropertyValue("Present") as bool? ?? false;
        Service = property.GetPropertyValue("Service") as string ?? string.Empty;
        Status = property.GetPropertyValue("Status") as string ?? string.Empty;
        StatusInfo = property.GetPropertyValue("StatusInfo") as int? ?? 0;
        SystemCreationClassName = property.GetPropertyValue("SystemCreationClassName") as string ?? string.Empty;
        SystemName = property.GetPropertyValue("SystemName") as string ?? string.Empty;
    }
#endif
}