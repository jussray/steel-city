using UnrealBuildTool;
public class SteelCityTarget : TargetRules
{
    public SteelCityTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Game;
        DefaultBuildSettings = BuildSettingsVersion.V4;
        ExtraModuleNames.Add("SteelCity");
    }
}
