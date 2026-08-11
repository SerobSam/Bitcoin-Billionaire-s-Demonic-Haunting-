import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs" / "assets" / "complete_3d_asset_package_spec.json"


def load_spec():
    return json.loads(SPEC.read_text(encoding="utf-8"))


def test_complete_3d_spec_covers_all_requested_biomes_and_exports():
    spec = load_spec()
    biome_names = {entry["name"] for entry in spec["world"]}
    assert biome_names == {
        "Urban District",
        "Mixed Forest",
        "Quarry",
        "Coastal Cliffs",
        "Subterranean Caverns",
    }
    for biome in spec["world"]:
        assert biome["concept_3d"]
        assert biome["blockout"]["greybox_meshes"]
        assert "terrain heightfield" in biome["layered_world_model"]
        assert biome["heightmaps"] and biome["topography_maps"] and biome["biome_masks"]
        assert biome["pbr_texture_sets"]
        assert set(biome["lods"]) == {"LOD0", "LOD1", "LOD2"}
        assert {"GLTF 2.0", "FBX ASCII", "JSON metadata"}.issubset(set(biome["exports"]))


def test_complete_3d_spec_covers_characters_animations_destructibility_tools_and_ui():
    spec = load_spec()
    assert len(spec["palette"]) == 6
    assert len(spec["characters"]["npc_archetypes"]) == 8
    assert len(spec["characters"]["hero"]["outfits"]) == 4
    assert "skeleton_64_bone" in spec["characters"]
    assert set(spec["characters"]["hero"]["lods"]) == {"LOD0", "LOD1", "LOD2"}
    for required in ["idle_calm", "walk", "run", "sprint", "jump", "climb", "vault", "attack_light_combo", "block", "parry", "lockpick", "forced_breach", "death_front", "ragdoll_blend"]:
        assert required in spec["animations"]["sets"]
    assert spec["destructibility"]["state_machine"] == ["intact", "damaged", "broken", "debris"]
    assert set(spec["destructibility"]["materials"]) == {"wood", "masonry", "glass", "metal", "foliage", "soil"}
    assert set(spec["tools"]) == {"hammer", "pick", "lockpick", "saw", "explosives", "scaffold_deployer"}
    assert {"HUD", "Inventory", "Crafting panel", "Map", "Contextual tooltips"}.issubset(set(spec["ui"]["screens"]))
