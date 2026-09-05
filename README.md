# Bitcoin Billionaire's Demonic Haunting

Bitcoin Billionaire's Demonic Haunting is a techno-horror action RPG where a rogue entity born from the Bitcoin genesis block possesses a billionaire and hijacks global networks. Survive digital hauntings, decode corrupted systems, fight spectral algorithms, and uncover the truth behind the genesis spark.

## Repository Contents
- `docs/game-design.md` establishes the high concept, design pillars, core loop, and player fantasy.
- `docs/story-bible.md` captures the premise, characters, locations, antagonist, and ending themes.
- `data/entities.json` seeds prototype character and antagonist data.
- `src/runtime.py` provides the deterministic mission/combat runtime, including playable DLC missions.
- `src/player_progression.py` provides persistent XP and leveling.
- `src/live_ops.py` provides premium power offers, a ten-tier seasonal reward track, rotating XP events, and purchasable story add-ons.
- `src/live_ops_rewards.py` applies claimed season and event rewards to player inventory.

## Live Ops, Monetization & Content Add-ons
The prototype supports a premium-credit economy with three explicitly capped power offers:
- Infernal Armor — +25 max health and +3 corruption resistance.
- Ghost Hashrate — +35 hashrate.
- Genesis Overclock — +15 max health, +50 hashrate, +2 corruption resistance.

Season 1 contains a ten-tier free/premium battle-pass-style reward track. Progression XP is deterministic and capped at tier 10; premium rewards require the premium track to be unlocked before they can be claimed.

Rotating events select a deterministic weekly event schedule, with Blood Moon Protocol (1.5x XP), Hash Rush (2.0x XP), and Ghost Signal (1.25x XP). Event multipliers apply to runtime season XP earned from investigations, combat victories, decoding, and choices.

The three content add-ons expose complete two-mission chains that can be launched through the runtime:
- Neon Tokyo — Neon Tokyo Blackout and Shibuya Wraith Hunt.
- Hell's Datacenter — Datacenter Descent and Server Cathedral.
- Genesis: Aftermath — Aftershock and Zero-Day Epilogue.

DLC victories award mission-specific XP, evidence, and loot, while season progression continues alongside the DLC runtime.

The runtime models purchases only; real payment processing, storefront APIs, refunds, and platform billing remain outside the game simulation.

## Quick Start
Run the prototype roster check:

```bash
python3 src/main.py
```

Run the automated test suite:

```bash
pytest -q
```
