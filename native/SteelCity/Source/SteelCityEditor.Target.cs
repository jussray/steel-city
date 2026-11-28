using UnrealBuildTool;
public class SteelCityEditorTarget : TargetRules
{
    public SteelCityEditorTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Editor;
        DefaultBuildSettings = BuildSettingsVersion.V4;
        ExtraModuleNames.Add("SteelCity");
    }
}
