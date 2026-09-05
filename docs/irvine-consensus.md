# Irvine Consensus

The second playable mission extends the Bel Air vertical slice into the **Irvine Suburbs** region.

## Objective chain

1. Enter the silent Irvine consensus district.
2. Trace the compromised neighborhood consensus node.
3. Fight the **Grid Vanguard** security construct.
4. Decode the stolen consensus vote with the genesis key.
5. Make the Cleanse / Exploit / Quarantine moral choice.
6. Extract before the district reconnects.

## Runtime

`src/irvine.py` owns the ordered objective state while reusing the engine-neutral runtime, Merkle investigation, encounter, corruption, loot-fragment, and moral-choice mechanics.

The Grid Vanguard has 50 health, deals 10 damage per exchange, and adds 5 corruption on each hit. The mission uses the corrupted `irvine_consensus` Merkle root, so decoding requires the `genesis` key.

The campaign spine unlocks Irvine Consensus after Bel Air Blackout and points onward to Dark Pool Descent.
