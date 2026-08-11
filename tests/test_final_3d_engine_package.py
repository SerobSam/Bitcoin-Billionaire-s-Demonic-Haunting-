import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs" / "assets" / "final_3d_engine_package_spec.json"


def load_spec():
    return json.loads(SPEC.read_text(encoding="utf-8"))


def test_final_3d_package_has_genesis_regions_and_required_world_contracts():
    spec = load_spec()
    regions = {world["name"] for world in spec["world_models"]}
    assert regions == {
        "Bel Air Blackout Zone",
        "Irvine Suburbs",
        "Manhattan Consensus",
        "Alpine Cold Storage Bunker",
        "Mojave Ground Return Rail Junction",
        "Dark Pool Dungeons",
        "Zero-State Relay Towers",
    }
    for world in spec["world_models"]:
        assert world["blockout"]["file"].endswith(".gltf")
        assert world["blockout"]["collision_proxy"].endswith(".fbx")
        assert world["final_meshes"]
        assert world["texture_sets"]
        assert set(world["lods"]) == {"LOD0", "LOD1", "LOD2"}
        assert world["metadata"].endswith(".json")


def test_final_3d_package_has_classes_enemies_bosses_tools_ui_and_destruction():
    spec = load_spec()
    character_ids = {character["id"] for character in spec["characters"]}
    for required in [
        "character_cypherpunk_final_LOD0_v01",
        "character_digitalwraith_final_LOD0_v01",
        "character_gridvanguard_final_LOD0_v01",
        "character_codeweaver_final_LOD0_v01",
        "character_ghostprocess_final_LOD0_v01",
        "character_sybilswarm_final_LOD0_v01",
        "character_darkpoolwarden_final_LOD0_v01",
        "character_genesisentity_phase1_final_LOD0_v01",
        "character_genesisentity_phase2_final_LOD0_v01",
    ]:
        assert required in character_ids
    for character in spec["characters"]:
        assert "64-bone" in character["skeleton"]
        assert character["facial_blendshapes"]
        assert set(character["lods"]) == {"LOD0", "LOD1", "LOD2"}
        assert character["exports"]["fbx"].endswith(".fbx")
        assert character["exports"]["gltf"].endswith(".gltf")
    assert spec["destructibility"]["state_machine"] == ["intact", "damaged", "broken", "debris"]
    assert set(spec["destructibility"]["materials"]) == {"wood", "masonry", "glass", "metal", "soil", "foliage"}
    assert len(spec["craft_tools"]) == 9
    assert "merkle_tree" in spec["ui"]["screens"]
    assert "mnemonic_board" in spec["ui"]["screens"]
    assert "skill_cast_primary" in spec["animations"]["clips"]
    assert "boss_phase2_transform" in spec["animations"]["clips"]
