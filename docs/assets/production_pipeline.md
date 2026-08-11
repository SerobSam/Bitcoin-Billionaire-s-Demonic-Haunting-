# Genesis Protocol Production Asset Pipeline

## Purpose

This pipeline turns concept art, source meshes, PBR textures, animation clips, destructible fracture maps, UI vectors, and metadata into deterministic Android engine import bundles for Genesis Protocol. It supplements the main game specification with concrete validation gates, folder contracts, and test scenes.

## Source-to-Engine Flow

1. **Source authoring**: artists commit PSD, AI, Blend, Maya, Substance, WAV, and editorial source files into the source depot using the project naming convention.
2. **Review exports**: DCC tools export FBX ASCII and GLTF 2.0 in meters, Y-up, with embedded media disabled.
3. **Texture packing**: base color exports as 16-bit sRGB PNG; normals as 16-bit TGA; roughness/metalness as packed EXR; height and AO as EXR.
4. **Metadata write**: every asset receives a JSON manifest row with `id`, `name`, `category`, `variant`, `LOD`, `version`, `formats`, `size_bytes`, `polycount`, `texture_resolutions`, `dependencies`, and `readme_path`.
5. **Automated validation**: `tools/validate_asset_manifest.py` checks schema-critical fields, palette count, naming convention, IDs, LOD values, categories, and non-negative budgets.
6. **Runtime conversion**: CI converts textures to ASTC tiers, compiles shaders to SPIR-V, builds UI atlases, and packs assets into Play Asset Delivery packs.
7. **Sample scene verification**: biome scenes and the destructibility lab are loaded on low, mid, and high device profiles to verify frame time, memory, LOD switching, and collision stability.

## Required Package Structure

```text
AssetPackage/
  00_styleguide/master_style_guide.pdf
  01_world/topography/world_topography_master_8k_EXR_v01.exr
  01_world/biome_masks/world_biomemask_master_8k_PNG_v01.png
  01_world/streaming/world_streaming_grid_JSON_v01.json
  02_biomes/urban/{concept,materials,meshes,readme.md}
  02_biomes/forest/{concept,materials,meshes,readme.md}
  02_biomes/quarry/{concept,materials,meshes,readme.md}
  02_biomes/coastal/{concept,materials,meshes,readme.md}
  02_biomes/cavern/{concept,materials,meshes,readme.md}
  03_characters/{hero,npc,enemies,bosses}
  04_props/destructibles/{wood,masonry,glass,metal,foliage,soil}
  05_tools/{hammer,pick,lockpick,saw,explosives,scaffold_deployer}
  06_ui/icons/{svg,png,atlas}
  07_vfx/{digital_static,phosphor_code,analog_sparks,dust,shards}
  08_audio_refs/{atmosphere,combat,boss,lore}
  09_scenes/{urban_sample,forest_sample,quarry_sample,coastal_sample,cavern_sample,destruction_lab}
  manifest/asset_manifest.json
```

## Validation Gates

| Gate | Pass requirement | Failure action |
|---|---|---|
| Naming | `category_assetname_variant_LOD_version` | block import and report offending id |
| Scale | 1 unit = 1 meter; humanoid hero 1.75-1.9 m | return to DCC owner |
| Skeleton | 64-bone skeleton, no missing required deform bones | block character import |
| LOD | LOD0/LOD1/LOD2 present for mesh assets unless marked `NA` | block release bundle |
| Texture | required PBR channels present and power-of-two sizes | generate red debug material |
| Destruction | state machine metadata and fracture/debris dependencies present | block destructible tag |
| UI | SVG source plus 512x512 PNG and atlas metadata | block UI atlas build |
| Performance | scene budget within target tier | demote LOD, reduce debris, or split tile |

## Test Scenes

- **Urban Sample**: stucco houses, smart glass, locked doors, AR property sigils, HOA Wraith combat.
- **Forest Sample**: foliage destruction, hidden root hatch, teal fog, Recluse NPC pathing.
- **Quarry Sample**: masonry fracture, pick usage, scaffold traversal, dust-heavy lighting.
- **Coastal Sample**: wet materials, container props, skiff route, glass and metal destruction.
- **Cavern Sample**: portal streaming, spectral liquidity, low-light readability, Subterranean entrance loop.
- **Destruction Lab**: all material types, lockpick/forced breach outcomes, debris pooling telemetry, navmesh semantic update.

## Production-Ready Pipeline Expansion

The complete engine-ready pipeline is maintained in `docs/assets/production_ready_art_asset_pipeline.md`. It adds explicit color accessibility variants, biome-by-biome PBR requirements, hidden subsurface entrance rules, destructible physics budgets, locked-door outcomes, character rig contracts, animation coverage, UI typography, craft tool visual specs, iteration gates, and deterministic zip packaging.

## Export Bundle Command

```bash
python3 tools/package_assets.py --src . --out build/genesis_asset_export.zip
```

## CI Commands

```bash
python3 -m json.tool assets/manifest/asset_manifest.json
python3 tools/validate_asset_manifest.py assets/manifest/asset_manifest.json
```
5. **Automated validation**: `tools/validate_asset_manifest.py` checks schema-critical fields, palette count, naming convention, IDs, LOD values, categories, and non-negative budgets.
6. **Runtime conversion**: CI converts textures to ASTC tiers, compiles shaders to SPIR-V, builds UI atlases, and packs assets into Play Asset Delivery packs.
7. **Sample scene verification**: biome scenes and the destructibility lab are loaded on low, mid, and high device profiles to verify frame time, memory, LOD switching, and collision stability.

## Required Package Structure

```text
AssetPackage/
  00_styleguide/master_style_guide.pdf
  01_world/topography/world_topography_master_8k_EXR_v01.exr
  01_world/biome_masks/world_biomemask_master_8k_PNG_v01.png
  01_world/streaming/world_streaming_grid_JSON_v01.json
  02_biomes/urban/{concept,materials,meshes,readme.md}
  02_biomes/forest/{concept,materials,meshes,readme.md}
  02_biomes/quarry/{concept,materials,meshes,readme.md}
  02_biomes/coastal/{concept,materials,meshes,readme.md}
  02_biomes/cavern/{concept,materials,meshes,readme.md}
  03_characters/{hero,npc,enemies,bosses}
  04_props/destructibles/{wood,masonry,glass,metal,foliage,soil}
  05_tools/{hammer,pick,lockpick,saw,explosives,scaffold_deployer}
  06_ui/icons/{svg,png,atlas}
  07_vfx/{digital_static,phosphor_code,analog_sparks,dust,shards}
  08_audio_refs/{atmosphere,combat,boss,lore}
  09_scenes/{urban_sample,forest_sample,quarry_sample,coastal_sample,cavern_sample,destruction_lab}
  manifest/asset_manifest.json
```

## Validation Gates

| Gate | Pass requirement | Failure action |
|---|---|---|
| Naming | `category_assetname_variant_LOD_version` | block import and report offending id |
| Scale | 1 unit = 1 meter; humanoid hero 1.75-1.9 m | return to DCC owner |
| Skeleton | 64-bone skeleton, no missing required deform bones | block character import |
| LOD | LOD0/LOD1/LOD2 present for mesh assets unless marked `NA` | block release bundle |
| Texture | required PBR channels present and power-of-two sizes | generate red debug material |
| Destruction | state machine metadata and fracture/debris dependencies present | block destructible tag |
| UI | SVG source plus 512x512 PNG and atlas metadata | block UI atlas build |
| Performance | scene budget within target tier | demote LOD, reduce debris, or split tile |

## Test Scenes

- **Urban Sample**: stucco houses, smart glass, locked doors, AR property sigils, HOA Wraith combat.
- **Forest Sample**: foliage destruction, hidden root hatch, teal fog, Recluse NPC pathing.
- **Quarry Sample**: masonry fracture, pick usage, scaffold traversal, dust-heavy lighting.
- **Coastal Sample**: wet materials, container props, skiff route, glass and metal destruction.
- **Cavern Sample**: portal streaming, spectral liquidity, low-light readability, Subterranean entrance loop.
- **Destruction Lab**: all material types, lockpick/forced breach outcomes, debris pooling telemetry, navmesh semantic update.

## Production-Ready Pipeline Expansion

The complete engine-ready pipeline is maintained in `docs/assets/production_ready_art_asset_pipeline.md`. It adds explicit color accessibility variants, biome-by-biome PBR requirements, hidden subsurface entrance rules, destructible physics budgets, locked-door outcomes, character rig contracts, animation coverage, UI typography, craft tool visual specs, iteration gates, and deterministic zip packaging.

## Export Bundle Command

```bash
python3 tools/package_assets.py --src . --out build/genesis_asset_export.zip
```

## CI Commands

```bash
python3 -m json.tool assets/manifest/asset_manifest.json
python3 tools/validate_asset_manifest.py assets/manifest/asset_manifest.json
```

## Final 3D Engine Package
`docs/assets/final_3d_engine_package_spec.json` is included in deterministic exports and is the authoritative build checklist for Genesis Protocol region, class, enemy, boss, tool, destructibility, UI, and animation asset integration.

## Materialized Final 3D Package
Run `python3 tools/generate_final_3d_package.py` to convert authoritative specs and gameplay JSON into `10_final_3d_engine_package/`, which contains per-world, per-character, per-tool, UI, lighting, destructibility, animation, README, and manifest metadata for engine import.

## Full Game Build Package
Run `python3 tools/generate_full_game_build.py` after materializing 3D metadata to generate `11_full_game_build/`, the authoritative campaign, co-op, PvP, endgame, input, gameplay systems, UI, Android, release, and world integration handoff generated from repo JSON.
