# Genesis Protocol — Hub Level Design

## Wastelands Research Hub

The Hub is the player's persistent safe-and-dangerous base: a vertically layered research outpost built around a Genesis signal tower. It is the central handoff point between investigation, campaign missions, side activities, upgrades, social NPCs, exploration, and DLC.

### Design goals

- Make the Hub readable within 30 seconds from the spawn plaza.
- Give every gameplay system a physical location instead of menu-only interactions.
- Create three circulation layers: public plaza, restricted research ring, and subterranean service network.
- Keep combat, stealth, traversal, and cinematic routes overlapping so the space changes meaning as the story advances.
- Build the level from modular Unity Prefabs so the same kit can support later regions.

## 1. Main-story missions

**Mission Board — Central Operations Tower**

- Primary launch point for campaign missions.
- Holographic world map shows unlocked regions and mission dependencies.
- Mission staging room supports dialogue, loadout confirmation, and cutscene transitions.
- Story progression changes signage, NPC placement, lighting, and accessible doors.

**Mission route:** Spawn Plaza → Operations Tower → Research Ring → Gate Hangar → regional deployment.

## 2. Side missions

**Mercantile Row / Field Office**

- Bounty board, civilian requests, faction jobs, investigation leads.
- Three rotating side-mission sockets: investigation, combat, recovery.
- Side missions can redirect the player through stealth alleys, rooftops, maintenance corridors, or the quarry lift.

## 3. Combat arenas

**Arena A — Training Yard**

- Early-game tutorial combat.
- Low cover, destructible barriers, spawn gates.

**Arena B — Reactor Court**

- Mid-game arena surrounding the power core.
- Multi-level cover, electrified hazards, elevated enemy positions.

**Arena C — Breach Ring**

- Late-game combat arena around the Genesis tower.
- Dynamic corruption hazards and multiple enemy entry lanes.

Combat arenas remain inactive during normal exploration and are activated by encounter volumes or mission state.

## 4. Stealth routes

Every major destination has at least one non-front-door approach:

- Service tunnels beneath the plaza.
- Vent network connecting the research labs.
- Rooftop catwalk from the hangar to the research ring.
- Maintenance bridge around the reactor court.
- Drainage channel leading to the underground archive.

Use occluders, shadow pockets, cover volumes, locked sightlines, and one-way traversal gates. Stealth routes should shorten direct travel but expose the player to optional evidence and environmental hazards.

## 5. Vertical traversal

**Traversal spine:** Plaza Level → Research Ring → Tower Roof → Cliff Walk → Sublevel.

- Elevators provide safe vertical travel.
- Ladders and maintenance stairs support stealth.
- Zip-line connects tower roof to the cliffside relay.
- Jump-pad/anti-gravity launch point unlocks after traversal progression.
- Rooftops become explorable after the first major story unlock.

Vertical routes must never be purely decorative: each level contains at least one collectible, shortcut, NPC interaction, or alternate combat position.

## 6. Hidden rooms

**Black Archive:** behind a falsified research wall; contains lore and rare evidence.

**Cold Wallet Vault:** requires a later key; contains premium-grade crafting materials.

**Developer Maintenance Room:** accessible through a service terminal sequence; contains environmental references to the game's systems without bypassing progression.

Hidden rooms use subtle environmental tells: unusual cable routing, mismatched panels, faint audio, corrupted decals, or a terminal that reports an impossible room index.

## 7. Collectibles / evidence

Place **12 evidence objects** across the Hub:

- 3 in public areas.
- 3 in research spaces.
- 2 on rooftops.
- 2 in maintenance tunnels.
- 1 in the Black Archive.
- 1 late-game Genesis artifact.

Evidence should reveal the billionaire's history, the Genesis Spark, faction motives, and clues toward alternate endings. Collected evidence persists through the campaign profile.

## 8. NPC spaces

**Operations Tower:** mission handler and campaign briefing NPCs.

**Field Office:** side-mission contacts and civilian witnesses.

**Workshop:** Faraday Forge crafting and equipment upgrades.

**Upgrade Station:** persistent health, hashrate, and corruption-resistance upgrades.

**Medical Bay:** healing, status explanation, and companion dialogue.

**Hangar:** vehicle/fast-travel staging and major story arrivals.

NPC schedules shift between story states. Dialogue changes after major missions and world events.

## 9. Fast-travel points

- **Hub Core Beacon** — main plaza.
- **Research Ring Beacon** — unlocked after first research mission.
- **Cliff Relay** — unlocked after traversal progression.
- **Underground Gate** — unlocked after the Dark Pool story beat.
- **Genesis Tower Beacon** — late-game.

Fast travel must respect mission locks and active encounter state.

## 10. Enemy spawn / control volumes

Use explicit Unity trigger volumes instead of uncontrolled random spawning.

| Volume | Location | Purpose |
|---|---|---|
| HZ-01 | Outer Gate | invasion entry |
| HZ-02 | Reactor Court | arena combat |
| HZ-03 | Research Ring | story ambush |
| HZ-04 | Underground | horror encounter |
| HZ-05 | Tower Roof | late-game breach |
| HZ-06 | Cliff Relay | optional bounty |

Each volume references an encounter profile, maximum active enemies, reinforcement points, cooldown, and mission/event conditions.

## 11. Boss arenas

**Genesis Breach Chamber** is the Hub's boss-capable space.

- Circular multi-level arena.
- Central Genesis signal core.
- Three destructible relay pylons.
- Outer ring for evasive movement.
- Upper catwalk for ranged phases.
- Underground escape route for post-boss cinematic transition.

The arena remains visually integrated with the Hub but is sealed by mission-state gates until required.

## 12. Cinematic spaces

- **Arrival Causeway:** first reveal of the Hub.
- **Operations Observatory:** campaign briefings and major reveals.
- **Genesis Tower Roof:** character conversations against the world skyline.
- **Medical Bay:** intimate companion scenes.
- **Reactor Court:** major supernatural manifestations.
- **Breach Chamber:** boss introduction and finale transitions.
- **Cliff Walk:** quiet reflection / ending setup.

Cinematic spaces provide controlled camera volumes, NPC staging markers, lighting presets, and temporary player-input constraints.

## 13. DLC entrances

Three permanent entrances are placed in the Hub:

- **Neon Tokyo Gate** — east transit terminal; unlocks `neon_tokyo_blackout`.
- **Hell's Datacenter Gate** — sealed geothermal lift; unlocks `datacenter_descent`.
- **Genesis Epilogue Gate** — corrupted Genesis portal; unlocks `aftershock`.

Each entrance visibly exists before purchase/unlock but remains inactive until the corresponding content add-on is owned and the mission chain is available. The entrance then becomes a physical mission-launch point.

## Unity implementation

### Scene composition

Use additive scene loading with a persistent Hub root:

```text
Hub_Wastelands.unity
├── Hub_Root
├── Hub_Terrain
├── Hub_Architecture
├── Hub_Interior_Operations
├── Hub_Interior_Research
├── Hub_Interior_Workshop
├── Hub_Underground
├── Hub_Rooftops
├── Hub_Traversal
├── Hub_NPCs
├── Hub_Encounters
├── Hub_Collectibles
├── Hub_Cinematics
├── Hub_FastTravel
└── Hub_DLC
```

### Unity systems

- **Terrain Tools:** sculpt the cliff basin, drainage channel, and outer approaches.
- **ProBuilder:** block out modular buildings and gameplay spaces before final art.
- **Prefab Variants:** standardize walls, doors, terminals, cover, lighting, and research equipment.
- **AI Navigation:** bake navigation surfaces per gameplay layer; keep rooftop and underground navigation separate where appropriate.
- **Cinemachine:** author arrival, briefing, boss, and reveal camera volumes.
- **Timeline:** sequence mission briefings, environmental manifestations, and boss introductions.
- **VFX Graph:** Genesis corruption, signal beams, sparks, ash, and supernatural distortions.
- **Shader Graph:** wet metal, emissive signage, corrupted screens, holograms, and Genesis surfaces.
- **Addressables:** stream interiors, optional underground spaces, DLC gates, and cinematic sets independently.
- **Occlusion Culling:** partition the Hub into plaza, research, underground, and tower visibility cells.
- **Light Probe Groups / Reflection Probes:** maintain consistent character and prop lighting through interiors and exterior transitions.
- **Volume system:** author exploration, combat, stealth, cinematic, and corruption post-processing profiles.

### World-state hooks

```text
HubState
├── story_progress
├── unlocked_regions
├── completed_side_missions
├── evidence_collected
├── fast_travel_unlocked
├── traversal_upgrades
├── active_encounter
├── boss_unlocked
└── owned_dlc
```

The Hub is intentionally data-driven so mission progression can change doors, NPCs, encounter volumes, collectibles, lighting, and DLC availability without duplicating the scene.

## Greybox target

- Approximate playable footprint: **2.5 km x 2.5 km** outer territory.
- Dense authored core: **~0.6 km x 0.6 km**.
- Three gameplay elevations plus underground network.
- 15+ mission/activity nodes.
- 12 evidence collectibles.
- 5 fast-travel nodes.
- 6 enemy control volumes.
- 3 combat arenas.
- 1 boss-capable arena.
- 3 DLC entrances.

## Art direction

The Hub begins as a cold, functional research installation and gradually reveals occult corruption. Exterior materials are weathered concrete, painted steel, dark glass, snow-dusted rock, and utility cables. Interior materials shift toward sterile composites, server metal, wet floors, and increasingly impossible Genesis geometry. Lighting starts neutral/cool and gains cyan signal light, red emergency states, and violet corruption as the campaign advances.
