# Campaign Progression

Genesis Protocol now has a data-driven campaign spine connecting the first playable mission to the larger world map, combat progression, and a persistent player profile.

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
- `grant_rewards()` for applying earned combat rewards to a loadout
- `next_mission()` for the post-mission handoff

`src/loadout.py` consumes ability IDs from the combat registry and provides a stable progression boundary: new campaigns begin with `packet_burn`, while mission rewards can unlock additional combat abilities.

## Persistent player profile

`src/profile.py` provides `CampaignProfile`, the long-lived player state shared across missions. It carries:

- `PlayerProgression` level, XP, and unspent upgrade points
- `PlayerUpgrades` purchased health, hashrate, and corruption-resistance bonuses
- `AbilityLoadout` combat abilities earned through campaign rewards
- mission-earned health, hashrate, corruption, evidence, reputation, choices, and inventory

`CampaignProfile.save()` and `CampaignProfile.load()` provide JSON persistence so the same character can leave one mission and resume the next without resetting progression or unlocked abilities.

Before each mission, `mission_player()` refreshes upgrade bonuses and returns the shared `PlayerState`. Campaign rewards are then applied to the same profile, keeping combat unlocks and inventory available for subsequent missions.

## Player XP

`PlayerProgression` keeps persistent level progression independently of the renderer. Players begin at level 1 with a 100-XP first threshold. Each subsequent threshold increases by 50 XP. XP rolls over after a level-up, and every level gained awards one upgrade point. Negative XP is rejected.

## Character upgrades

`PlayerUpgrades` converts earned upgrade points into persistent bonuses:

- `max_health` → +10 maximum health per point
- `hashrate` → +5 hashrate per point
- `corruption_resistance` → persistent resistance rating for future combat integration

Upgrades are serialized with the profile and re-applied whenever a mission begins.

These layers remain renderer- and engine-neutral so they can later drive Android/Vulkan UI, world streaming, save slots, or another front end without rewriting mission rules.
