import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "11_full_game_build"


def load(relative: str):
    return json.loads((BUILD / relative).read_text(encoding="utf-8"))


def test_full_game_generator_outputs_campaign_and_modes_from_authoritative_data():
    subprocess.run([sys.executable, str(ROOT / "tools" / "generate_full_game_build.py")], check=True)
    manifest = load("manifest/full_game_build_manifest.json")
    assert manifest["class_count"] == 4
    assert manifest["loot_tier_count"] == 7
    assert manifest["complete_biome_count"] == 5
    assert manifest["final_region_count"] == 7

    campaign = load("campaign/campaign_acts_i_iv.json")
    assert [act["act"] for act in campaign["acts"]] == ["I", "II", "III", "IV"]
    assert campaign["acts"][-1]["missions"][-1]["bosses"] == [
        "character_genesisentity_phase1_final_LOD0_v01",
        "character_genesisentity_phase2_final_LOD0_v01",
    ]
    assert "save_system" in campaign

    endgame = load("modes/endgame_modes.json")
    assert set(endgame["modes"]) == {
        "sybil_invasion",
        "dark_pool_dungeon_runs",
        "zero_state_relay_tower_defense",
        "overflow_arena",
    }


def test_full_game_build_contains_coop_pvp_controls_systems_and_ui():
    coop = load("multiplayer/coop_rules.json")
    assert coop["network_replication"]["tick_rate_hz"] == 30
    assert "destructible_state" in coop["network_replication"]["replicated"]
    assert coop["shared_merkle_synergy"]["node_types"] == ["leaf", "branch", "root"]

    pvp = load("multiplayer/pvp_rules.json")
    assert set(pvp["modes"]) == {"siphon_protocol", "core_node_control", "packet_breach"}
    assert pvp["modes"]["siphon_protocol"]["team_sizes"] == ["1v1", "2v2", "3v3"]

    controls = load("controls/input_camera_mapping.json")
    assert controls["camera"]["mode"] == "third_person"
    assert "cypherpunk" in controls["skills"]

    systems = load("systems/gameplay_systems.json")
    assert systems["merkle_progression"]["seed_phrase_slots"][-1] == "slot_12"
    assert systems["loot_tiers"][-1]["id"] == "immutable"
    assert "destructible_object_system" in systems

    ui = load("ui/full_ui_build.json")
    assert "coop" in ui["screens"]
    assert "pvp" in ui["screens"]
    assert "matchmaking" in ui["screens"]
    assert "settings" in ui["screens"]


def test_android_release_build_artifacts_are_export_ready():
    manifest_xml = (BUILD / "android/AndroidManifest.xml").read_text(encoding="utf-8")
    assert "android.hardware.vulkan.version" in manifest_xml
    assert "android.permission.INTERNET" in manifest_xml
    gradle = (BUILD / "android/build.gradle.kts").read_text(encoding="utf-8")
    assert "com.genesisprotocol.game" in gradle
    assert "bundleRelease" not in gradle
    release = load("android/release_build_spec.json")
    assert release["package_name"] == "com.genesisprotocol.game"
    assert "./gradlew bundleRelease" in release["aab_steps"]
    assert "assetpack_worlds" in release["bundle_structure"][1]
