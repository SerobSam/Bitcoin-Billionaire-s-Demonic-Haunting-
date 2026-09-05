# Genesis Protocol — Vertical Slice

## Bel Air Blackout

The first playable mission establishes the game's foundational loop:

1. **Investigate** the compromised site and collect evidence.
2. **Scan** a corrupted Merkle node for an actionable clue.
3. **Fight** the Digital Wraith or survive long enough to extract its fragment.
4. **Decode** the fragment using a valid genesis key.
5. **Roll loot** from the project's authoritative loot-tier table.
6. **Choose** Cleanse, Exploit, or Quarantine.
7. **Persist** the resulting state so later missions can react to the player's history.

### Design intent

The vertical slice is deterministic where reproducibility matters (tests and scripted smoke runs) while preserving weighted loot selection for future runtime randomness. Existing asset data remains authoritative; gameplay systems should consume those definitions rather than duplicate them.

### Current runtime modules

- `src/runtime.py` — player state, combat, mission phases, moral choices, persistence.
- `src/loot.py` — loot-tier loading, weighted selection, deterministic drop rolls.
- `src/merkle.py` — node scanning, corruption-aware decoding, investigation completion.
- `src/main.py` — command-line smoke path.

This slice is intentionally engine-neutral so the same rules can later drive an Android/Vulkan frontend or a test harness.
