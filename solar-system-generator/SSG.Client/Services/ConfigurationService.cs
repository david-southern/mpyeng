using Microsoft.Extensions.Options;

public class AppConfiguration
{
    public const string ConfigSectionName = "AppConfiguration";
    public string ServerBaseAddress { get; set; } = null!;
}

public class ConfigurationService
{
    private readonly IOptions<AppConfiguration> _configOptions;

    public ConfigurationService(IOptions<AppConfiguration> configOptions)
    {
        _configOptions = configOptions;
    }

    public string ServerBaseAddress => _configOptions.Value.ServerBaseAddress;
}