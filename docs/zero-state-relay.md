# Zero-State Relay — Campaign Finale

Zero-State Relay is the fourth and final mission in the current campaign spine.

## Objective sequence

1. Reach the Zero-State Relay tower.
2. Stabilize the collapsing genesis relay and expose its corrupted root.
3. Fight the Genesis Entity — Phase 1.
4. Decode the final genesis signal with the `genesis` key.
5. Trigger the Genesis Entity — Phase 2 transformation.
6. Defeat Phase 2 and choose Cleanse, Exploit, or Quarantine.
7. Extract before the relay resets.

## Finale mechanics

The Genesis Entity now has two distinct combat phases. Phase 1 uses an 80-health encounter with 14 damage and 9 corruption per hit. Decoding the corrupted relay root exposes the entity's second form: a 100-health encounter with 20 damage and 15 corruption per hit.

The phase transition deliberately reuses the existing deterministic encounter engine instead of introducing a separate combat implementation. The decoded genesis signal also grants a hashrate surge before Phase 2, making the investigation loop directly feed the boss fight.

After Phase 2 falls, the generic moral-choice system determines the ending direction. Extraction awards a `genesis_core` relic, providing a concrete hook for post-campaign progression.

## Campaign endpoint

After extraction, `Campaign.next_mission("zero_state_relay")` returns `None`. This is the current campaign endpoint and is ready for a future New Game+ layer, alternate finale, or post-credits content without changing the existing mission progression contract.
