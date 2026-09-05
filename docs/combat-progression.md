# Tactical Combat Progression

The combat layer provides deterministic ability execution with progression-aware loadouts.

## Core abilities

| Ability | Type | Damage | Cooldown | Corruption gain |
| --- | --- | ---: | ---: | ---: |
| Packet Burn | Digital | 28 | 2 turns | 0 |
| Salt Circle | Occult | 18 | 3 turns | 5 |
| Cold Storage | Void | 12 | 4 turns | 8 |

Basic attacks advance all cooldowns. Using an ability advances the turn and starts that ability's cooldown while ticking the others.

## Unlock progression

A new loadout begins with `packet_burn`. Campaign rewards unlock additional abilities:

- **Bel Air Blackout** → `salt_circle`
- **Irvine Consensus** → `cold_storage`
- **Dark Pool Descent** → no combat ability reward
- **Zero-State Relay** → `genesis_core` inventory reward

Locked abilities are rejected before combat damage is applied. Loadouts serialize only stable ability IDs, keeping progression compatible with a future Android/Vulkan front end.

## Character upgrades

Level-up points are persistent across the campaign and can be spent at an in-world `UpgradeStation` safe node. The station exposes three stable upgrade IDs:

- `max_health` — **Hardened Frame**: +10 maximum health per point
- `hashrate` — **Hotter Hash**: +5 hashrate per point
- `corruption_resistance` — **Salted Core**: reduce corruption gained from abilities by 1 per point

Purchased upgrades are applied immediately to the persistent `CampaignProfile` and survive profile save/load. Combat accepts the resulting corruption-resistance value so high-risk abilities become progressively safer without changing their damage balance.

## Design intent

The system is deterministic and engine-neutral: the same inputs always produce the same damage, cooldown, and corruption state. Corruption is a combat consequence for high-risk abilities, while character upgrades give players a controlled way to invest level-up points into survivability, throughput, or resistance.

The data definitions in `data/gameplay/abilities.json` mirror the runtime ability IDs and balance values.
