{
  "id": "system_destructible_state_machine_standard_v01",
  "states": ["intact", "damaged", "broken", "debris"],
  "transitions": [
    { "from": "intact", "to": "damaged", "trigger": "damage >= damage_threshold", "events": ["apply_damage_decal", "emit_material_creak"] },
    { "from": "damaged", "to": "broken", "trigger": "damage >= break_threshold || forced_breach", "events": ["swap_fractured_mesh", "spawn_primary_chunks", "update_navmesh_semantic"] },
    { "from": "broken", "to": "debris", "trigger": "chunks_sleep_timeout || distance_cull", "events": ["return_rigid_bodies_to_pool", "spawn_debris_decals", "persist_semantic_state"] }
  ],
  "materials": {
    "wood": { "max_primary_chunks": 12, "debris_pool": "pool_wood_splinters_v01", "sleep_seconds": 3.0, "noise_radius_m": 18 },
    "masonry": { "max_primary_chunks": 24, "debris_pool": "pool_masonry_rubble_v01", "sleep_seconds": 4.0, "noise_radius_m": 26 },
    "glass": { "max_primary_chunks": 8, "debris_pool": "pool_glass_shards_v01", "sleep_seconds": 2.0, "noise_radius_m": 20 },
    "metal": { "max_primary_chunks": 10, "debris_pool": "pool_metal_panels_v01", "sleep_seconds": 4.5, "noise_radius_m": 30 },
    "foliage": { "max_primary_chunks": 6, "debris_pool": "pool_leaf_cards_v01", "sleep_seconds": 1.5, "noise_radius_m": 8 },
    "soil": { "max_primary_chunks": 0, "debris_pool": "pool_soil_clumps_v01", "sleep_seconds": 1.0, "noise_radius_m": 10 }
  },
  "locked_door_outcomes": {
    "lockpick": { "destructive": false, "duration_seconds": 4.2, "noise_radius_m": 4, "loot_quality_delta": 0, "animation": "anim_interact_lockpick_loop_v01" },
    "forced_breach": { "destructive": true, "duration_seconds": 1.1, "noise_radius_m": 28, "loot_quality_delta": -1, "animation": "anim_interact_forced_breach_v01" }
  },
  "physics_budget": { "max_active_rigid_debris": 64, "max_visual_debris_instances": 256, "cpu_spike_ms": 2.5, "gpu_vfx_ms": 1.5 }
}
