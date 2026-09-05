# Campaign Progression

Genesis Protocol now has a data-driven campaign spine connecting the first playable mission to the larger world map.

## Mission chain

1. **Bel Air Blackout** — Bel Air Blackout Zone
2. **Irvine Consensus** — Irvine Suburbs
3. **Dark Pool Descent** — Dark Pool Dungeons
4. **Zero-State Relay** — Zero-State Relay Towers

`data/missions/campaign.json` is the source of truth for mission IDs, regions, unlock dependencies, and forward progression.

## Runtime behavior

`src/campaign.py` loads the mission graph and provides:

- `is_unlocked()` for gating
- `available()` for mission selection UI
- `complete_mission()` for persistent campaign progression
- `next_mission()` for the post-mission handoff

The campaign layer is intentionally renderer- and engine-neutral so it can later drive Android/Vulkan UI, world streaming, or another front end without rewriting mission rules.
