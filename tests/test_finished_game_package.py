import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FINISHED = ROOT / "12_finished_game"


def load(relative: str):
    return json.loads((FINISHED / relative).read_text(encoding="utf-8"))


def test_finished_game_generator_uses_all_authoritative_sources_and_biomes():
    subprocess.run([sys.executable, str(ROOT / "tools" / "generate_finished_game.py")], check=True)
    manifest = load("manifest/finished_game_manifest.json")
    assert manifest["class_count"] == 4
    assert manifest["loot_tier_count"] == 7
    assert manifest["biome_mission_count"] == 5
    assert manifest["final_region_count"] == 7
    assert manifest["uses_destructible_state_machine"] == "system_destructible_state_machine_standard_v01"

    campaign = load("campaign/final_campaign_runtime.json")
    biome_names = {mission["biome"] for mission in campaign["biome_missions"]}
    assert biome_names == {"Urban District", "Mixed Forest", "Quarry", "Coastal Cliffs", "Subterranean Caverns"}
    assert campaign["scripted_events"][0]["uses"]["forced_breach"]["destructive"] is True
    assert campaign["save_system"]["destructible_state_machine"] == "system_destructible_state_machine_standard_v01"


def test_finished_game_runtime_systems_online_and_ui_are_complete():
    systems = load("systems/final_gameplay_runtime.json")
    assert set(systems["class_runtime"]) == {"cypherpunk", "digital_wraith", "grid_vanguard", "code_weaver"}
    assert systems["merkle_tree"]["seed_phrase_slots"][-1] == "slot_12"
    assert systems["loot"]["tiers"][-1]["id"] == "immutable"
    assert systems["destructible_object_system"]["canonical_state_machine"]["states"] == ["intact", "damaged", "broken", "debris"]

    online = load("multiplayer/final_online_runtime.json")
    assert "coop" in online and "pvp" in online and "endgame" in online
    assert "server-authoritative damage" in online["pvp"]["anti_cheat"]
    assert set(online["endgame"]["modes"]) == {"sybil_invasion", "dark_pool_dungeon_runs", "zero_state_relay_tower_defense", "overflow_arena"}

    ui = load("ui/final_ui_runtime.json")
    assert "mnemonic_board" in ui["widgets"]
    assert ui["widgets"]["mnemonic_board"][-1] == "slot_12"
    assert ui["loot_colors"]["immutable"] == "#FFFFFF"


def test_finished_game_android_and_play_store_release_are_ready():
    manifest_xml = (FINISHED / "android/AndroidManifest.xml").read_text(encoding="utf-8")
    assert "Genesis Protocol" in manifest_xml
    release = load("android/play_store_release_checklist.json")
    assert release["package_name"] == "com.genesisprotocol.game"
    assert release["obfuscation_minification"]["r8"] is True
    assert release["asset_compression"]["textures"] == "ASTC by device tier"
    assert release["release_channels"] == ["internal", "closed_alpha", "open_beta", "production"]
