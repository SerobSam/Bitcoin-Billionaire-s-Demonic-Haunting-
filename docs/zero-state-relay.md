# Zero-State Relay — Campaign Finale

Zero-State Relay is the fourth and final mission in the current campaign spine.

## Objective sequence

1. Reach the Zero-State Relay tower.
2. Stabilize the collapsing genesis relay and expose its corrupted root.
3. Fight the Genesis Entity — Phase 1.
4. Decode the final genesis signal with the `genesis` key.
5. Choose Cleanse, Exploit, or Quarantine.
6. Extract before the relay resets.

## Finale mechanics

The Genesis Entity uses a high-health encounter with heavy corruption pressure. The recovered relay root is represented as a corrupted Merkle node, preserving the campaign's investigation/decode loop.

Successful decoding grants an additional hashrate surge before the final moral choice. The choice uses the same consequence model established by earlier missions, so the campaign finale remains mechanically consistent while the narrative stakes escalate.

## Campaign endpoint

After extraction, `Campaign.next_mission("zero_state_relay")` returns `None`. This is the current campaign endpoint and is ready for a future New Game+ layer, alternate finale, or post-credits content without changing the existing mission progression contract.
