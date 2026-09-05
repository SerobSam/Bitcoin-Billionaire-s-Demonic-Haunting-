# Campaign Progression

Genesis Protocol now has a data-driven campaign spine connecting the first playable mission to the larger world map and combat progression.

## Mission chain

1. **Bel Air Blackout** — Bel Air Blackout Zone → unlocks `salt_circle`
2. **Irvine Consensus** — Irvine Suburbs → unlocks `cold_storage`
3. **Dark Pool Descent** — Dark Pool Dungeons
4. **Zero-State Relay** — Zero-State Relay Towers → awards `genesis_core`

`data/missions/campaign.json` is the source of truth for mission IDs, regions, unlock dependencies, forward progression, and rewards.

## Runtime behavior

`src/campaign.py` loads the mission graph and provides:

- `is_unlocked()` for gating
- `available()` for mission selection UI
- `complete_mission()` for persistent campaign progression
- `rewards_for()` for post-mission reward handoff
- `next_mission()` for the post-mission handoff

`src/loadout.py` consumes ability IDs from the combat registry and provides a stable progression boundary: new campaigns begin with `packet_burn`, while mission rewards can unlock additional combat abilities.

The campaign and loadout layers are intentionally renderer- and engine-neutral so they can later drive Android/Vulkan UI, world streaming, or another front end without rewriting mission rules.
