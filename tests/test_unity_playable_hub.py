from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def test_unity_hub_scene_and_bootstrap_exist():
    scene = ROOT / "Assets" / "Scenes" / "Hub_Wastelands.unity"
    script = ROOT / "Assets" / "GenesisPrototype.cs"
    assert scene.exists()
    assert script.exists()
    source = script.read_text(encoding="utf-8")
    for marker in ("RuntimeInitializeOnLoadMethod", "CharacterController", "Genesis_Breach_Arena", "NEON TOKYO // DLC", "Evidence Fragment", "FastTravel", "SideMission"):
        assert marker in source


def test_unity_hub_manifest_covers_playable_features():
    manifest = json.loads((ROOT / "data" / "world" / "wastelands_hub.json").read_text(encoding="utf-8"))
    types = {zone["type"] for zone in manifest["zones"]}
    assert {"main_story", "side_missions", "combat_arena", "stealth_route", "vertical_traversal", "hidden_room", "collectibles", "npc_space", "fast_travel", "enemy_control", "boss_arena", "cinematic", "dlc_entrance"} <= types
    assert manifest["evidence"]["total"] == 12
    assert manifest["fast_travel"]["nodes"] == 5


def test_full_world_builder_and_campaign_map_are_defined():
    builder = ROOT / "Assets" / "Editor" / "GenesisWorldBuilder.cs"
    manifest = json.loads((ROOT / "data" / "world" / "full_world.json").read_text(encoding="utf-8"))
    source = builder.read_text(encoding="utf-8")
    for marker in ("BuildFullWorld", "CreateRegion", "CreateRoads", "GenesisWorldAnchor", "Addressables", "HDRP"):
        assert marker in source
    assert len(manifest["regions"]) >= 8
    assert len(manifest["world_routes"]) >= 7
    assert manifest["playable_target"] == "hub_to_campaign_to_endgame_with_optional_dlc"
