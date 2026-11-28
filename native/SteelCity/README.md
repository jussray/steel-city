# Steel City native edition — authored source foundation
Target assumption: Unreal Engine 5.3, desktop editor first. Not compiled or rendered. No external code or assets imported. Browser edition remains canonical for gameplay.
## Included
Game module and targets, camera pawn, built-in collision-aware flying mode with falling exit, basic keyboard input, authority-only blast request with cooldown (not a projectile), local-player widget hook (not a widget asset), seven-ID/five-star authoritative ledger and pickup actor, automation test source.
## First editor gate
Generate project files and build SteelCityEditor with UE 5.3 and the supported C++ toolchain. Create an empty test level with a floor and PlayerStart, assign a visible hero mesh and seven distinct pickup actor IDs (steel-star-1 through steel-star-7), assign pickup meshes, and run SteelCity.Gameplay.StarLedger in the editor automation panel. Test movement, camera, hover, landing and collection through real input. Do not mark verified until this succeeds.
## Not implemented
Playable map, hero and pickup art, UMG widget assets, Enhanced Input actions, touch/controller bindings, sprint/talk/climb, actual blast projectile, NPCs, seven-act runtime, save migration, multiplayer input prediction or RPCs, session reset, native lighting and VFX. No hardware or visual parity proof. The source snapshot at ../../graphics/native-game-contract.json is the migration reference; this module does not load it yet.

## HUD and art direction candidate
Create a Widget Blueprint derived from USteelCityHUD with a TextBlock named StarCountText, assign it on a derived player controller, and select that controller in the level GameMode. The widget subscribes to replicated count changes and handles initial/late GameState arrival. Validate 0/5 through 5/5, duplicate rejection, late join and widget teardown. The hero camera contains a local, conservative bloom and blue/gold grade starting preset; tune it with real assets. No actual UMG layout or native rendered evidence exists.

## Native interaction candidate
Programmatic touch joystick, local 256x256 minimap capture at five updates/second, and authority-only line-of-sight Talk are authored. Place an ASteelCityNPC with configured Dialogue in the editor to test. Native map and joystick are rectangular fallbacks; circular material/brush art, objective runtime, multiplayer RPC and mobile capture/hold testing remain pending. No asset purchase or native compile. The previous no-widget statement is superseded by the programmatic fallback.
