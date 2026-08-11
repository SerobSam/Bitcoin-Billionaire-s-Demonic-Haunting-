import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "10_final_3d_engine_package"


def load(relative: str):
    return json.loads((PACKAGE / relative).read_text(encoding="utf-8"))


def test_materialized_package_manifest_and_core_blueprints_are_generated():
    subprocess.run([sys.executable, str(ROOT / "tools" / "generate_final_3d_package.py")], check=True)
    manifest = load("manifest/final_3d_asset_manifest.json")
    assert manifest["asset_count"] == 25
    assert manifest["naming_convention"] == "category_assetname_variant_LOD_version"
    assert (PACKAGE / "animations/animation_blueprint.json").exists()
    assert (PACKAGE / "destructibility/destructibility_blueprint.json").exists()
    assert (PACKAGE / "ui/ui_blueprint.json").exists()
    assert (PACKAGE / "lighting/lighting_palette_blueprint.json").exists()


def test_materialized_world_character_tool_metadata_is_engine_ready():
    bel_air = load("world/belair_blackout/metadata.json")
    assert bel_air["blockout"]["file"].endswith(".gltf")
    assert bel_air["blockout"]["collision_proxy"].endswith(".fbx")
    assert bel_air["pbr_materials"][0]["albedo"].endswith(".png")
    assert bel_air["pbr_materials"][0]["normal"].endswith(".tga")
    assert bel_air["pbr_materials"][0]["height"].endswith(".exr")

    cypherpunk = load("characters/cypherpunk/metadata.json")
    assert cypherpunk["gameplay_class"]["id"] == "cypherpunk"
    assert len(cypherpunk["skill_animation_clips"]) == len(cypherpunk["gameplay_class"]["skills"])
    assert "64-bone" in cypherpunk["skeleton"]
    assert cypherpunk["exports"]["fbx"].endswith(".fbx")
    assert cypherpunk["exports"]["gltf"].endswith(".gltf")

    needle = load("tools/pneumatic_needle_gun/metadata.json")
    assert needle["model"]["in_hand_gltf"].endswith(".gltf")
    assert needle["model"]["in_hand_fbx"].endswith(".fbx")
    assert needle["icons"]["svg"].endswith(".svg")
    assert needle["icons"]["png"].endswith(".png")


def test_materialized_ui_lighting_and_destruction_use_authoritative_gameplay_data():
    ui = load("ui/ui_blueprint.json")
    assert len(ui["mnemonic_seed_slots"]) == 12
    assert set(ui["merkle_node_types"]) == {"leaf", "branch", "root"}
    assert "ultimate_charge" in ui["modifier_types"]

    lighting = load("lighting/lighting_palette_blueprint.json")
    assert len(lighting["palette"]) == 6
    assert lighting["environmental_tint_rules"]["safe_scan_and_AR"] == "Muted Teal"

    destruction = load("destructibility/destructibility_blueprint.json")
    assert destruction["state_machine"] == ["intact", "damaged", "broken", "debris"]
    assert [tier["id"] for tier in destruction["loot_tiers"]][0] == "scrap"
