# Genesis Protocol — Unity Playable Hub

The repository now contains a dependency-light Unity 6 playable prototype for the Wastelands Research Hub.

## Open and play

1. Install **Unity 6000.0.58f2** or a compatible Unity 6 editor.
2. Open the repository as a Unity project.
3. Open `Assets/Scenes/Hub_Wastelands.unity`.
4. Press **Play**. The runtime bootstrap builds the Hub from Unity primitives, so no external 3D package is required for the first playable slice.

## Controls

- **WASD** — move
- **E** — interact with nearby terminals, evidence, beacons, the boss console, and DLC gates
- **Left Mouse Button** — Packet Burn attack toward the nearest enemy in front of the player
- **R** — Cleanse choice
- **F** — Exploit choice
- **Q** — Quarantine choice

## Playable loop

1. Start at the Hub Core.
2. Visit **MAIN STORY // OPERATIONS**.
3. Travel to the Research Ring and defeat the Chrome Oni.
4. Return to Operations and decode the recovered signal.
5. Choose Cleanse, Exploit, or Quarantine.
6. Explore the Hub, collect 12 evidence fragments, use fast travel, take the side bounty, heal, and upgrade hashrate.
7. Visit the Genesis Breach Chamber console to activate the Genesis Echo boss encounter.
8. Inspect the Neon Tokyo, Hell's Datacenter, and Genesis Epilogue DLC entrances.

## Production boundary

This is the first **playable Unity blockout**, not the final art pass. It intentionally uses runtime-generated primitives so the game can be tested before importing the full character, environment, texture, animation, audio, VFX, and HDRP asset libraries. The authoritative Hub layout remains `data/world/wastelands_hub.json`.
