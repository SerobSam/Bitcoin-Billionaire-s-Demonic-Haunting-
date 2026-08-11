#!/usr/bin/env python3
"""Materialize final Genesis Protocol 3D engine package metadata from authoritative JSON specs."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "10_final_3d_engine_package"
FINAL_SPEC = ROOT / "docs/assets/final_3d_engine_package_spec.json"
COMPLETE_SPEC = ROOT / "docs/assets/complete_3d_asset_package_spec.json"
CLASSES = ROOT / "assets/gameplay/classes.json"
LOOT = ROOT / "assets/gameplay/loot_tiers.json"
MERKLE = ROOT / "assets/gameplay/merkle_rules.json"
MANIFEST = ROOT / "assets/manifest/asset_manifest.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_readme(path: Path, title: str, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# " + title + "\n\n" + "\n".join(f"- {line}" for line in lines) + "\n", encoding="utf-8")


def main() -> None:
    final = load(FINAL_SPEC)
    complete = load(COMPLETE_SPEC)
    classes = load(CLASSES)["classes"]
    loot = load(LOOT)["tiers"]
    merkle = load(MERKLE)
    manifest = load(MANIFEST)

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    package_assets: list[dict] = []

    for world in final["world_models"]:
        region = world["id"].removeprefix("world_").removesuffix("_final_LOD0_v01")
        metadata = {
            "source_spec": FINAL_SPEC.as_posix(),
            "id": world["id"],
            "category": "world",
            "name": world["name"],
            "naming_convention": final["naming_convention"],
            "blockout": world["blockout"],
            "final_meshes": world["final_meshes"],
            "pbr_materials": world["texture_sets"],
            "lods": world["lods"],
            "streaming": world["streaming"],
            "lighting_preset": world["lighting_preset"],
            "collision_policy": "author UCX convex hulls for modules, heightfield for terrain, fracture hulls for destructible layer",
            "exports": final["export_settings"],
            "readme_path": f"10_final_3d_engine_package/world/{region}/README.md",
        }
        rel = f"world/{region}/metadata.json"
        write_json(OUT / rel, metadata)
        write_readme(OUT / f"world/{region}/README.md", world["name"], [
            "Build blockout, final meshes, collision, LOD0/LOD1/LOD2, PBR texture sets, lighting preset, and tile streaming exactly from metadata.json.",
            "Export FBX ASCII and GLTF 2.0 with meters units, Y-up axis, embedded media disabled.",
            "Package all Albedo/Normal/Roughness/AO/Height maps referenced by metadata.json before engine import.",
        ])
        package_assets.append({"id": world["id"], "category": "world", "metadata": rel, "readme": f"world/{region}/README.md"})

    class_by_id = {c["id"]: c for c in classes}
    for character in final["characters"]:
        cid = character["id"].removeprefix("character_").removesuffix("_final_LOD0_v01")
        gameplay = class_by_id.get(cid)
        skill_clips = []
        if gameplay:
            for skill in gameplay["skills"]:
                skill_clips.append({
                    "skill_id": skill["id"],
                    "clip": f"anim_{cid}_skill_{skill['id']}_v01",
                    "type": skill["type"],
                    "cost_hashrate": skill["cost_hashrate"],
                    "cooldown_ms": skill["cooldown_ms"],
                    "tags": skill["tags"],
                })
        metadata = {
            "source_specs": [FINAL_SPEC.as_posix(), CLASSES.as_posix()],
            "id": character["id"],
            "category": character["type"],
            "concept": character["concept"],
            "production_pipeline": character["pipeline"],
            "skeleton": character["skeleton"],
            "facial_blendshapes": character["facial_blendshapes"],
            "skin_weights": character["skin_weights"],
            "lods": character["lods"],
            "exports": character["exports"],
            "gameplay_class": gameplay,
            "skill_animation_clips": skill_clips,
            "base_animation_state_machine": final["animations"]["state_machines"]["player" if gameplay else "boss" if character["type"] == "boss" else "enemy"],
            "root_motion_rules": final["animations"]["root_motion"],
            "blendspaces": final["animations"]["blendspaces"],
            "readme_path": f"10_final_3d_engine_package/characters/{cid}/README.md",
        }
        rel = f"characters/{cid}/metadata.json"
        write_json(OUT / rel, metadata)
        write_readme(OUT / f"characters/{cid}/README.md", character["name"], [
            "Produce sculpt, retopo, UV, bakes, textures, rig, skin weights, LOD0/LOD1/LOD2, FBX, GLTF, and JSON metadata from metadata.json.",
            "Playable class assets must include generated skill animation clips derived from assets/gameplay/classes.json.",
            "Facial blendshape names and skeleton contract are import-blocking requirements.",
        ])
        package_assets.append({"id": character["id"], "category": character["type"], "metadata": rel, "readme": f"characters/{cid}/README.md"})

    animation_metadata = {
        "source_specs": [FINAL_SPEC.as_posix(), CLASSES.as_posix()],
        "global_clips": final["animations"]["clips"],
        "root_motion_rules": final["animations"]["root_motion"],
        "blendspaces": final["animations"]["blendspaces"],
        "state_machines": final["animations"]["state_machines"],
        "class_skill_clip_counts": {c["id"]: len(c["skills"]) for c in classes},
        "class_skill_clips": {
            c["id"]: [f"anim_{c['id']}_skill_{s['id']}_v01" for s in c["skills"]] for c in classes
        },
    }
    write_json(OUT / "animations/animation_blueprint.json", animation_metadata)
    write_readme(OUT / "animations/README.md", "Animation Blueprint", [
        "Use this blueprint for player, enemy, and boss state machines.",
        "Class skill clips are generated directly from assets/gameplay/classes.json and must be authored before gameplay lock.",
    ])

    destructibility_metadata = {
        "source_spec": FINAL_SPEC.as_posix(),
        "state_machine": final["destructibility"]["state_machine"],
        "materials": final["destructibility"]["materials"],
        "locked_doors": final["destructibility"]["locked_doors"],
        "loot_tiers": loot,
        "save_delta_fields": ["object_id", "state", "health", "loot_claimed", "navmesh_delta_hash"],
    }
    write_json(OUT / "destructibility/destructibility_blueprint.json", destructibility_metadata)
    write_readme(OUT / "destructibility/README.md", "Universal Destructibility", [
        "Implement intact -> damaged -> broken -> debris exactly as destructibility_blueprint.json.",
        "Loot outcomes must use assets/gameplay/loot_tiers.json weights.",
    ])

    for tool in final["craft_tools"]:
        tid = tool["id"].removeprefix("tool_").removesuffix("_final_LOD0_v01")
        metadata = {
            "source_spec": FINAL_SPEC.as_posix(),
            "id": tool["id"],
            "category": "tool",
            "model": tool["model"],
            "animations": tool["animations"],
            "vfx": tool["vfx"],
            "sound_cues": tool["sound_cues"],
            "icons": tool["icons"],
            "export_settings": final["export_settings"],
            "readme_path": f"10_final_3d_engine_package/tools/{tid}/README.md",
        }
        rel = f"tools/{tid}/metadata.json"
        write_json(OUT / rel, metadata)
        write_readme(OUT / f"tools/{tid}/README.md", tool["name"], [
            "Build in-hand and world pickup meshes, collision, use/equip/recover animations, VFX, sound cue references, SVG icon and PNG icon from metadata.json.",
            "Socket grip marker and single convex hull are required for engine import.",
        ])
        package_assets.append({"id": tool["id"], "category": "tool", "metadata": rel, "readme": f"tools/{tid}/README.md"})

    ui_metadata = {
        "source_specs": [FINAL_SPEC.as_posix(), MERKLE.as_posix(), COMPLETE_SPEC.as_posix()],
        "screens": final["ui"]["screens"],
        "icons": final["ui"]["icons"],
        "typography": final["ui"]["typography"],
        "accessibility": final["ui"]["accessibility"],
        "merkle_node_types": merkle["node_types"],
        "mnemonic_seed_slots": merkle["seed_phrase_slots"],
        "modifier_types": merkle["modifier_types"],
        "palette": final["palette"],
    }
    write_json(OUT / "ui/ui_blueprint.json", ui_metadata)
    write_readme(OUT / "ui/README.md", "UI and Icon Blueprint", [
        "Build HUD, inventory, skill bar, Merkle Tree, Mnemonic Board, map, and tooltip layouts from ui_blueprint.json.",
        "Mnemonic Board must expose all 12 seed phrase slots and Merkle UI must support all node types and modifier types.",
    ])

    lighting_metadata = {
        "source_specs": [FINAL_SPEC.as_posix(), COMPLETE_SPEC.as_posix()],
        "palette": final["palette"],
        "lighting_presets_by_world": {w["id"]: w["lighting_preset"] for w in final["world_models"]},
        "environmental_tint_rules": {
            "danger_and_breach": "Terracotta Signal",
            "safe_scan_and_AR": "Muted Teal",
            "rare_loot_and_boss_weakpoints": "Phosphor Gold",
            "text_and_rim_readability": "Cold Bone",
            "base_shadow_and_panel": "Deep Ledger",
            "dust_masonry_inactive": "Ash Concrete",
        },
    }
    write_json(OUT / "lighting/lighting_palette_blueprint.json", lighting_metadata)
    write_readme(OUT / "lighting/README.md", "Lighting and Palette Blueprint", [
        "Apply painterly warm key, teal bounce, Cold Bone rim, and biome fog cards from lighting_palette_blueprint.json.",
        "Tint rules are strict so UI, gameplay affordances, and environments share one visual identity.",
    ])

    bundle_manifest = {
        "schema_version": "1.0.0",
        "source_specs": [FINAL_SPEC.as_posix(), COMPLETE_SPEC.as_posix(), CLASSES.as_posix(), LOOT.as_posix(), MERKLE.as_posix(), MANIFEST.as_posix()],
        "naming_convention": final["naming_convention"],
        "asset_count": len(package_assets),
        "assets": package_assets,
        "repository_manifest_asset_count": len(manifest["assets"]),
        "export_bundle_command": "python3 tools/package_assets.py --src . --out build/genesis_asset_export.zip",
    }
    write_json(OUT / "manifest/final_3d_asset_manifest.json", bundle_manifest)
    write_readme(OUT / "README.md", "Genesis Protocol Final 3D Engine Package", [
        "This directory materializes the authoritative JSON specs into engine-ready per-asset metadata and README files.",
        "Each metadata file is an import checklist for DCC export, runtime integration, validation, and deterministic bundling.",
    ])


if __name__ == "__main__":
    main()
