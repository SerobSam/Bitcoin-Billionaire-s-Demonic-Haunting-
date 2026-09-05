# Bitcoin Billionaire's Demonic Haunting

Bitcoin Billionaire's Demonic Haunting is a techno-horror action RPG where a rogue entity born from the Bitcoin genesis block possesses a billionaire and hijacks global networks. Survive digital hauntings, decode corrupted systems, fight spectral algorithms, and uncover the truth behind the genesis spark.

## Repository Contents
- `docs/game-design.md` establishes the high concept, design pillars, core loop, and player fantasy.
- `docs/story-bible.md` captures the premise, characters, locations, antagonist, and ending themes.
- `data/entities.json` seeds prototype character and antagonist data.
- `src/runtime.py` provides the deterministic mission/combat runtime.
- `src/player_progression.py` provides persistent XP and leveling.
- `src/live_ops.py` provides premium power offers and purchasable story add-ons.

## Monetization & Content Add-ons
The prototype now supports a premium-credit economy with three explicitly capped power offers:
- Infernal Armor — +25 max health and +3 corruption resistance.
- Ghost Hashrate — +35 hashrate.
- Genesis Overclock — +15 max health, +50 hashrate, +2 corruption resistance.

It also includes three content add-ons with new mission chains:
- Neon Tokyo — 2 missions.
- Hell's Datacenter — 2 missions.
- Genesis: Aftermath — 2 post-finale missions.

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
