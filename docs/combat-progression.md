# Tactical Combat Progression

The combat layer now provides deterministic ability execution on top of the existing mission runtime.

## Core abilities

| Ability | Type | Damage | Cooldown | Corruption |
| --- | --- | ---: | ---: | ---: |
| Packet Burn | Digital | 28 | 2 turns | 0 |
| Salt Circle | Occult | 18 | 3 turns | 5 |
| Cold Storage | Void | 12 | 4 turns | 8 |

Basic attacks advance all cooldowns. Using an ability advances the turn and starts that ability's cooldown while ticking the others.

## Design intent

The system is deterministic and engine-neutral: the same inputs always produce the same damage and cooldown state. Corruption is treated as a spendable resource, reinforcing the game's moral-economy theme without introducing random combat outcomes at this layer.

The data definitions in `data/gameplay/abilities.json` mirror the runtime ability IDs so a future Android/Vulkan front end can load the same balance contract.
