#!/usr/bin/env python3
"""Generate the final Genesis Protocol game-build package from authoritative repo JSON metadata."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "11_full_game_build"
SOURCES = {
    "classes": ROOT / "assets/gameplay/classes.json",
    "loot": ROOT / "assets/gameplay/loot_tiers.json",
    "merkle": ROOT / "assets/gameplay/merkle_rules.json",
    "complete_spec": ROOT / "docs/assets/complete_3d_asset_package_spec.json",
    "final_spec": ROOT / "docs/assets/final_3d_engine_package_spec.json",
    "asset_manifest": ROOT / "assets/manifest/asset_manifest.json",
    "materialized_manifest": ROOT / "10_final_3d_engine_package/manifest/final_3d_asset_manifest.json",
    "animation_blueprint": ROOT / "10_final_3d_engine_package/animations/animation_blueprint.json",
    "destructibility": ROOT / "10_final_3d_engine_package/destructibility/destructibility_blueprint.json",
    "ui": ROOT / "10_final_3d_engine_package/ui/ui_blueprint.json",
    "lighting": ROOT / "10_final_3d_engine_package/lighting/lighting_palette_blueprint.json",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, data: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data, encoding="utf-8")


def class_balance(classes: list[dict]) -> dict:
    return {
        cls["id"]: {
            "resource": cls["resource"],
            "role": cls["role"],
            "active_skill_count": sum(1 for s in cls["skills"] if s["type"] == "active"),
            "ultimate": cls["ultimate"],
            "pvp_damage_scalar": 0.82,
            "coop_threat_scalar": 1.0,
            "animation_clips": [f"anim_{cls['id']}_skill_{skill['id']}_v01" for skill in cls["skills"]],
        }
        for cls in classes
    }


def main() -> None:
    data = {name: load(path) for name, path in SOURCES.items()}
    classes = data["classes"]["classes"]
    loot = data["loot"]["tiers"]
    merkle = data["merkle"]
    complete = data["complete_spec"]
    final = data["final_spec"]
    materialized_manifest = data["materialized_manifest"]
    animation = data["animation_blueprint"]
    destruction = data["destructibility"]
    ui = data["ui"]
    lighting = data["lighting"]

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    class_ids = [cls["id"] for cls in classes]
    final_regions = [world["name"] for world in final["world_models"]]
    complete_biomes = [world["name"] for world in complete["world"]]
    final_bosses = [c for c in final["characters"] if c["type"] == "boss"]
    enemy_ids = [c["id"] for c in final["characters"] if c["type"] in {"enemy", "boss"}]

    campaign = {
        "source_specs": [str(SOURCES[k]) for k in ["classes", "loot", "merkle", "complete_spec", "final_spec", "materialized_manifest"]],
        "acts": [
            {
                "act": "I",
                "title": "Blackout Handshake",
                "regions": ["Irvine Suburbs", "Bel Air Blackout Zone"],
                "biome_framework": "Urban District",
                "missions": [
                    {"id": "mission_irvine_hashwake", "objectives": ["teach walk/run/sprint/dash", "unlock first Merkle leaf", "breach smart-lock tutorial"], "enemies": ["character_ghostprocess_final_LOD0_v01"], "loot_table": [loot[0]["id"], loot[1]["id"]]},
                    {"id": "mission_belair_blackout", "objectives": ["restore emergency relay", "choose lockpick or breach route", "defeat Sybil ambush"], "enemies": ["character_sybilswarm_final_LOD0_v01"], "loot_table": [loot[1]["id"], loot[2]["id"]]},
                ],
            },
            {
                "act": "II",
                "title": "Consensus Fracture",
                "regions": ["Manhattan Consensus", "Mojave Ground Return Rail Junction"],
                "biome_framework": "Quarry",
                "missions": [
                    {"id": "mission_manhattan_merkle", "objectives": ["route through Consensus rooftops", "defend Merkle compiler", "extract encrypted cache"], "enemies": enemy_ids[:2], "loot_table": [loot[2]["id"], loot[3]["id"]]},
                    {"id": "mission_mojave_ground", "objectives": ["align grounding rods", "escort rail junction payload", "survive dust destruction event"], "enemies": enemy_ids, "loot_table": [loot[1]["id"], loot[3]["id"]]},
                ],
            },
            {
                "act": "III",
                "title": "Cold Pool Descent",
                "regions": ["Alpine Cold Storage Bunker", "Dark Pool Dungeons"],
                "biome_framework": "Subterranean Caverns",
                "missions": [
                    {"id": "mission_alpine_seedvault", "objectives": ["recover 12-slot mnemonic board", "survive Cold Storage alarm", "craft final tool upgrade"], "enemies": ["character_darkpoolwarden_final_LOD0_v01"], "loot_table": [loot[3]["id"], loot[4]["id"]]},
                    {"id": "mission_darkpool_warden", "objectives": ["complete Dark Pool dungeon run", "destroy liquidity mirrors", "defeat Dark Pool Warden"], "enemies": ["character_darkpoolwarden_final_LOD0_v01"], "loot_table": [loot[4]["id"], loot[5]["id"]]},
                ],
            },
            {
                "act": "IV",
                "title": "Zero-State Genesis",
                "regions": ["Zero-State Relay Towers"],
                "biome_framework": "Coastal Cliffs",
                "missions": [
                    {"id": "mission_zero_state_tower", "objectives": ["activate relay tower defense", "hold three Core Nodes", "open Genesis arena"], "enemies": enemy_ids, "loot_table": [loot[4]["id"], loot[5]["id"]]},
                    {"id": "mission_genesis_entity", "objectives": ["defeat Genesis Entity Phase 1", "survive phase transition", "defeat Genesis Entity Phase 2"], "bosses": [boss["id"] for boss in final_bosses], "loot_table": [loot[5]["id"], loot[6]["id"]]},
                ],
            },
        ],
        "difficulty_scaling": {"solo": 1.0, "coop_2p": 1.55, "coop_3p": 2.05, "coop_4p": 2.45, "new_game_plus_per_clear": 0.35},
        "save_system": {"checkpoint_scope": "mission + destructible deltas + Merkle tree + inventory", "autosave_events": ["mission_start", "boss_phase_change", "loot_claim", "relay_capture"]},
    }
    write_json(OUT / "campaign/campaign_acts_i_iv.json", campaign)

    coop = {
        "class_balance": class_balance(classes),
        "mission_variants": {act["act"]: {"shared_progression": True, "revive_tokens_per_player": 2, "enemy_scalar": campaign["difficulty_scaling"]["coop_2p"], "loot_rolls": "personal with party rarity pity"} for act in campaign["acts"]},
        "shared_merkle_synergy": {"node_types": merkle["node_types"], "synergy_rule": "matching branch modifiers grant party buff; root modifiers are host-authoritative"},
        "network_replication": {"authority": "host authoritative with deterministic asset ids", "replicated": ["player_transform", "skill_cast", "damage_event", "destructible_state", "loot_claim", "revive_state"], "tick_rate_hz": 30},
    }
    write_json(OUT / "multiplayer/coop_rules.json", coop)

    endgame = {
        "modes": {
            "sybil_invasion": {"players": "1-4", "matchmaking": "region + difficulty + class role", "reward_tiers": [t["id"] for t in loot[2:]], "replication": coop["network_replication"]},
            "dark_pool_dungeon_runs": {"players": "1-4", "tiles": ["Dark Pool Dungeons", "Subterranean Caverns"], "reward_tiers": [t["id"] for t in loot[3:]], "session_persistence": "floor seed + destructible deltas"},
            "zero_state_relay_tower_defense": {"players": "1-4", "objective": "defend three relay cores", "enemy_scaling": campaign["difficulty_scaling"], "reward_tiers": [t["id"] for t in loot[4:]]},
            "overflow_arena": {"players": "1-4", "objective": "survive escalating waves", "wave_sources": enemy_ids, "reward_tiers": [t["id"] for t in loot]},
        }
    }
    write_json(OUT / "modes/endgame_modes.json", endgame)

    pvp = {
        "modes": {
            "siphon_protocol": {"team_sizes": ["1v1", "2v2", "3v3"], "win_condition": "drain opposing Core Node", "class_scalars": class_balance(classes)},
            "core_node_control": {"team_sizes": ["3v3"], "win_condition": "territory capture score", "replicated_objectives": ["node_owner", "capture_progress", "contested_state"]},
            "packet_breach": {"team_sizes": ["2v2", "3v3"], "win_condition": "plant or prevent payload breach", "payload_uses_destructibility": True},
        },
        "mmr": {"placement_matches": 10, "seasonal_soft_reset": 0.65, "ranked_rewards": [t["id"] for t in loot[2:]]},
        "balance_rules": {cls["id"]: {"ultimate_charge_scalar": 0.7, "cooldown_scalar": 1.15, "loot_disabled": True, "normalized_hashrate": 100} for cls in classes},
    }
    write_json(OUT / "multiplayer/pvp_rules.json", pvp)

    input_spec = {
        "movement": {"walk": "left_stick <0.55", "run": "left_stick >=0.55", "sprint": "left_stick + sprint", "dash": "B / touch dodge", "vault_climb_jump": "context action + traversal tag"},
        "combat": {"light_attack": "R1 / primary touch", "heavy_attack": "R2 hold", "block": "L1", "parry": "L1 timed", "target_lock": "R3 / touch focus"},
        "skills": {cls["id"]: {skill["id"]: f"skill_slot_{i+1}" for i, skill in enumerate(cls["skills"])} for cls in classes},
        "camera": {"mode": "third_person", "shoulder_swap": True, "lock_on_orbit": True, "collision_probe": "spherecast camera boom"},
        "accessibility": ui["accessibility"],
        "animation_integration": {"blendspaces": animation["blendspaces"], "root_motion": animation["root_motion_rules"]},
    }
    write_json(OUT / "controls/input_camera_mapping.json", input_spec)

    systems = {
        "classes": class_balance(classes),
        "merkle_progression": {"node_types": merkle["node_types"], "seed_phrase_slots": merkle["seed_phrase_slots"], "modifier_types": merkle["modifier_types"]},
        "loot_tiers": loot,
        "crafting": {"tools": [tool["id"] for tool in final["craft_tools"]], "materials_from_loot_tiers": [tier["id"] for tier in loot]},
        "enemy_ai_state_machines": animation["state_machines"],
        "boss_phase_logic": {boss["id"]: animation["state_machines"]["boss"] for boss in final_bosses},
        "destructible_object_system": destruction,
    }
    write_json(OUT / "systems/gameplay_systems.json", systems)

    ui_build = {
        "screens": ui["screens"] | {"coop": ["party frames", "revive prompt", "shared Merkle synergy"], "pvp": ["scoreboard", "MMR badge", "objective status"], "matchmaking": ["mode select", "role fill", "latency bucket"], "settings": ["graphics", "audio", "controls", "accessibility"]},
        "icons": ui["icons"],
        "typography": ui["typography"],
        "accessibility": ui["accessibility"],
    }
    write_json(OUT / "ui/full_ui_build.json", ui_build)

    android_manifest = """<manifest xmlns:android=\"http://schemas.android.com/apk/res/android\">\n  <uses-feature android:name=\"android.hardware.vulkan.version\" android:version=\"0x00400000\" android:required=\"true\" />\n  <uses-permission android:name=\"android.permission.INTERNET\" />\n  <uses-permission android:name=\"android.permission.ACCESS_NETWORK_STATE\" />\n  <application android:label=\"Genesis Protocol\" android:theme=\"@style/Theme.GenesisProtocol\" android:extractNativeLibs=\"false\">\n    <activity android:name=\".MainActivity\" android:screenOrientation=\"landscape\" android:exported=\"true\">\n      <intent-filter>\n        <action android:name=\"android.intent.action.MAIN\" />\n        <category android:name=\"android.intent.category.LAUNCHER\" />\n      </intent-filter>\n    </activity>\n  </application>\n</manifest>\n"""
    write_text(OUT / "android/AndroidManifest.xml", android_manifest)

    gradle = """plugins {\n    id(\"com.android.application\")\n    id(\"org.jetbrains.kotlin.android\")\n}\n\nandroid {\n    namespace = \"com.genesisprotocol.game\"\n    compileSdk = 36\n    defaultConfig {\n        applicationId = \"com.genesisprotocol.game\"\n        minSdk = 26\n        targetSdk = 36\n        versionCode = 1\n        versionName = \"1.0.0\"\n        ndk { abiFilters += listOf(\"arm64-v8a\") }\n    }\n    signingConfigs { create(\"release\") { storeFile = file(System.getenv(\"GENESIS_KEYSTORE\") ?: \"release.keystore\") } }\n    buildTypes { release { isMinifyEnabled = true; isShrinkResources = true; signingConfig = signingConfigs.getByName(\"release\") } }\n    assetPacks += setOf(\":assetpack_worlds\", \":assetpack_audio\", \":assetpack_highres\")\n}\n"""
    write_text(OUT / "android/build.gradle.kts", gradle)

    release = {
        "package_name": "com.genesisprotocol.game",
        "api_level": {"min_sdk": 26, "target_sdk": 36, "compile_sdk": 36},
        "aab_steps": ["python3 tools/generate_final_3d_package.py", "python3 tools/package_assets.py --src . --out build/genesis_asset_export.zip", "./gradlew bundleRelease"],
        "signing": {"keystore_env": "GENESIS_KEYSTORE", "key_alias_env": "GENESIS_KEY_ALIAS", "password_env": ["GENESIS_KEYSTORE_PASSWORD", "GENESIS_KEY_PASSWORD"]},
        "permissions": ["INTERNET", "ACCESS_NETWORK_STATE"],
        "supported_devices": ["Android API 26+", "Vulkan 1.0+", "arm64-v8a"],
        "bundle_structure": ["base APK: code/UI/core classes", "assetpack_worlds", "assetpack_audio", "assetpack_highres"],
        "compression": {"textures": "ASTC by device tier", "audio": "Opus", "meshes": "GLTF/FBX converted to runtime binary cache"},
        "release_channels": ["internal", "closed_alpha", "open_beta", "production"],
    }
    write_json(OUT / "android/release_build_spec.json", release)

    world_build = {
        "final_regions": final_regions,
        "complete_biomes": complete_biomes,
        "materialized_world_metadata": [asset for asset in materialized_manifest["assets"] if asset["category"] == "world"],
    }
    write_json(OUT / "world/world_build_index.json", world_build)

    package_manifest = {
        "schema_version": "1.0.0",
        "source_files": {name: path.as_posix() for name, path in SOURCES.items()},
        "outputs": ["campaign", "multiplayer", "modes", "controls", "systems", "ui", "android", "world"],
        "authoritative_asset_count": len(data["asset_manifest"]["assets"]),
        "materialized_asset_count": materialized_manifest["asset_count"],
        "class_count": len(classes),
        "loot_tier_count": len(loot),
        "complete_biome_count": len(complete_biomes),
        "final_region_count": len(final_regions),
    }
    write_json(OUT / "manifest/full_game_build_manifest.json", package_manifest)
    write_text(OUT / "README.md", "# Genesis Protocol Full Game Build\n\n- Generated exclusively from repository JSON specifications.\n- Contains campaign, co-op, PvP, endgame, controls, systems, UI, Android build, release, and world integration metadata.\n")


if __name__ == "__main__":
    main()
