# Dark Pool Descent

The third campaign mission moves Genesis Protocol beneath the surface into the **Dark Pool Dungeons**.

## Objective spine

1. Descend into the Dark Pool dungeons.
2. Locate the Blackwater Choir signal and scan its corrupted Merkle root.
3. Fight the Dark Pool Warden and recover a corrupted chain fragment.
4. Decode the submerged chain liturgy with the Genesis key.
5. Choose Cleanse, Exploit, or Quarantine.
6. Escape through the flooded service shaft.

## Runtime behavior

`src/darkpool.py` keeps the mission engine-neutral while reusing the shared `GameState`, `Encounter`, choice consequences, and Merkle investigation mechanics. The Warden has 60 health, deals 14 damage per exchange, and adds 8 corruption on each hit.

Completing `dark_pool_descent` unlocks `zero_state_relay` through `data/missions/campaign.json`.
