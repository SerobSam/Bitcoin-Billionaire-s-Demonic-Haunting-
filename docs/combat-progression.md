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

## Design intent

The system is deterministic and engine-neutral: the same inputs always produce the same damage and cooldown state. Corruption is a combat consequence for high-risk abilities, reinforcing the game's moral-economy theme without introducing random combat outcomes at this layer.

The data definitions in `data/gameplay/abilities.json` mirror the runtime ability IDs and balance values.
