from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_requested_asset_inventory_exists_and_has_content():
    required_files = [
        ROOT / "00_styleguide" / "master_style_guide.pdf",
        ROOT / "01_world" / "topography" / "world_topography_master_8k_EXR_v01.exr",
        ROOT / "01_world" / "biome_masks" / "world_biomemask_master_8k_PNG_v01.png",
        ROOT / "01_world" / "streaming" / "world_streaming_grid_JSON_v01.json",
        ROOT / "02_biomes" / "urban" / "concept.md",
        ROOT / "02_biomes" / "urban" / "materials.json",
        ROOT / "02_biomes" / "urban" / "meshes.gltf",
        ROOT / "02_biomes" / "forest" / "concept.md",
        ROOT / "02_biomes" / "forest" / "materials.json",
        ROOT / "02_biomes" / "forest" / "meshes.gltf",
        ROOT / "02_biomes" / "quarry" / "concept.md",
        ROOT / "02_biomes" / "quarry" / "materials.json",
        ROOT / "02_biomes" / "quarry" / "meshes.gltf",
        ROOT / "02_biomes" / "coastal" / "concept.md",
        ROOT / "02_biomes" / "coastal" / "materials.json",
        ROOT / "02_biomes" / "coastal" / "meshes.gltf",
        ROOT / "02_biomes" / "cavern" / "concept.md",
        ROOT / "02_biomes" / "cavern" / "materials.json",
        ROOT / "02_biomes" / "cavern" / "meshes.gltf",
        ROOT / "03_characters" / "hero" / "profile.json",
        ROOT / "03_characters" / "npc" / "profile.json",
        ROOT / "03_characters" / "enemies" / "profile.json",
        ROOT / "03_characters" / "bosses" / "profile.json",
        ROOT / "04_props" / "destructibles" / "wood" / "behavior.json",
        ROOT / "04_props" / "destructibles" / "masonry" / "behavior.json",
        ROOT / "04_props" / "destructibles" / "glass" / "behavior.json",
        ROOT / "04_props" / "destructibles" / "metal" / "behavior.json",
        ROOT / "04_props" / "destructibles" / "foliage" / "behavior.json",
        ROOT / "04_props" / "destructibles" / "soil" / "behavior.json",
        ROOT / "05_tools" / "hammer" / "spec.json",
        ROOT / "05_tools" / "pick" / "spec.json",
        ROOT / "05_tools" / "lockpick" / "spec.json",
        ROOT / "05_tools" / "saw" / "spec.json",
        ROOT / "05_tools" / "explosives" / "spec.json",
        ROOT / "05_tools" / "scaffold_deployer" / "spec.json",
        ROOT / "06_ui" / "icons" / "svg" / "icon_set.svg",
        ROOT / "06_ui" / "icons" / "png" / "icon_sheet.png",
        ROOT / "06_ui" / "icons" / "atlas" / "icon_atlas.json",
        ROOT / "07_vfx" / "digital_static" / "effect.json",
        ROOT / "07_vfx" / "phosphor_code" / "effect.json",
        ROOT / "07_vfx" / "analog_sparks" / "effect.json",
        ROOT / "07_vfx" / "dust" / "effect.json",
        ROOT / "07_vfx" / "shards" / "effect.json",
        ROOT / "08_audio_refs" / "atmosphere" / "cue.json",
        ROOT / "08_audio_refs" / "combat" / "cue.json",
        ROOT / "08_audio_refs" / "boss" / "cue.json",
        ROOT / "08_audio_refs" / "lore" / "cue.json",
        ROOT / "09_scenes" / "urban_sample" / "scene.json",
        ROOT / "09_scenes" / "forest_sample" / "scene.json",
        ROOT / "09_scenes" / "quarry_sample" / "scene.json",
        ROOT / "09_scenes" / "coastal_sample" / "scene.json",
        ROOT / "09_scenes" / "cavern_sample" / "scene.json",
        ROOT / "09_scenes" / "destruction_lab" / "scene.json",
        ROOT / "manifest" / "asset_manifest.json",
    ]

    missing = [str(path.relative_to(ROOT)) for path in required_files if not path.exists()]
    assert not missing, f"Missing required asset files: {missing}"


def test_manifest_contains_full_asset_inventory():
    manifest = (ROOT / "manifest" / "asset_manifest.json").read_text(encoding="utf-8")
    assert 'world_topography_master_LOD0_v01' in manifest
    assert 'biome_urban_master_LOD0_v01' in manifest
    assert 'character_hero_analogexorcist_LOD0_v01' in manifest
    assert 'scene_destruction_lab_LOD0_v01' in manifest
