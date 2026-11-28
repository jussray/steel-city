#!/usr/bin/env python3
"""Static native source contracts; never an UnrealBuildTool/UHT or runtime pass."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "native" / "SteelCity" / "Source" / "SteelCity"
header = (SOURCE / "SteelCityHUD.h").read_text(encoding="utf-8")
body = (SOURCE / "SteelCityHUD.cpp").read_text(encoding="utf-8")
joystick = (SOURCE / "SteelCityJoystick.cpp").read_text(encoding="utf-8")
hero = (SOURCE / "SteelCityHero.cpp").read_text(encoding="utf-8")
build = (SOURCE / "SteelCity.Build.cs").read_text(encoding="utf-8")
widgets = re.findall(r'UPROPERTY\(meta=\(BindWidget(?:Optional)?\)\)\s*TObjectPtr<(\w+)>\s+(\w+);', header)
required = {"StarCountText","TalkButton","FlyButton","BlastButton","DownButton","RunButton","JumpButton","MinimapImage","DialogueText","Joystick"}
assert required == {name for _,name in widgets}, widgets
for _, name in widgets:
    assert f'TEXT("{name}")' in body, f"Missing native fallback widget: {name}"
for file in SOURCE.rglob("*.h"):
    includes = re.findall(r'^#include .*$',file.read_text(encoding="utf-8"),re.M)
    generated = [line for line in includes if ".generated.h" in line]
    if generated:
        assert len(generated) == 1 and generated[0] == includes[-1], file
        assert f'{file.stem}.generated.h' in generated[0], file
assert 'OnTalkClicked' in header and 'FindTalkTarget()' in body
assert 'HasAuthority()' in hero and 'LineTraceSingleByChannel' in hero
assert 'Execute_Interact' in hero
assert 'NativeOnMouseCaptureLost' in joystick and 'ResetInput();' in joystick
assert 'Hero->MoveForward(-Axis.Y)' in body and 'Hero->MoveRight(Axis.X)' in body
assert 'bCaptureEveryFrame=false' in body and 'WorldViewTimer=.2f' in body
assert 'ReleaseMinimap();' in body and 'MinimapCapture->Destroy()' in body
assert all(f'"{module}"' in build for module in ("Engine","UMG","Slate","SlateCore"))
print(json.dumps({"static_source_contract":"PASS","widgets":sorted(required),
                  "native_compile":"NOT_RUN","native_runtime":"NOT_RUN",
                  "visual_parity":"NOT_RUN"},indent=2))
