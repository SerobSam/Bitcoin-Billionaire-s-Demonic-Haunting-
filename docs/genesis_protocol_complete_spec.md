# Genesis Protocol: Complete Android Game and Asset Production Specification

## 1. Executive Summary

**Genesis Protocol** is a third-person techno-horror action RPG for Android set after a rogue entity, the Genesis Spark, emerges from corrupted proof-of-work residue and possesses a Bitcoin billionaire whose smart-grid empire becomes a planetary haunting machine. The game fuses the **Genesis Protocol** systems canon—Cypherpunk, Digital Wraith, Grid Vanguard, Code Weaver, Merkle Tree progression, Hashrate scaling, Faraday Forge crafting, Anti-Gravity Studio traversal fabrication, Mnemonic Board seed phrases, Sybil Invasions, Dark Pool Dungeons, Zero-State Relays, Overflow Arena, PvP Siphon Protocol, Developer Console identity, and Recluse Chronicles seasons—with the narrative canon of **Bitcoin Billionaire's Demonic Haunting**: haunted wealth, demonized infrastructure, psychological dread, corrupted networks, spectral algorithms, and environments where suburban quiet and financial power rot into digital possession.

The production target is a premium-feeling Android action adventure with:

- **Native C++ Android NDK engine core** for deterministic gameplay, ECS, physics integration, procedural dungeons, destructibility, and save serialization.
- **Vulkan renderer** optimized for tile-based mobile GPUs, clustered forward+ lighting, GPU-driven culling, streaming terrain tiles, PBR materials, temporal upscaling, and ARCore camera composition.
- **Jetpack Compose shell UI** for menus, HUD overlays, inventory, Merkle skill visualization, Darknet Bazaar, Developer Console identity, accessibility, and settings.
- **Media3 + ExoPlayer audio layer** for seamless atmospheric loops, adaptive combat music, audiobook lore chapters, modem screams, server-fan hum, and boss telegraphs.
- **Room DB + encrypted file blobs** for offline saves, character builds, world state, codex unlocks, replayable dungeons, and season progress.
- **WorkManager daemon simulation** for asynchronous world events, mining-daemon invasions, bazaar rotations, and offline Hashrate simulations.
- **Kotlin coroutines** for UI event streams, combat scheduling, network status, audio crossfades, and ECS bridge messages.
- **ARCore GeoScan Matrix overlays** that project hidden signal geometry, subsurface entrances, haunt signatures, and Zero-State tower anomalies into real-world camera views.

The shipped game is structured into four campaign acts, nine major regions, four classes, seven loot tiers, deterministic procedural endgame activities, optional PvP invasions, and a complete realistic-stylized art pipeline with warm terracotta accents, muted teal complements, and deep neutral bases.

## 2. Engine Architecture

### 2.1 Android Module Layout

```text
GenesisProtocol/
  app/                                # Android application shell
    src/main/AndroidManifest.xml
    src/main/java/com/genesisprotocol/
      MainActivity.kt                 # Compose + Surface host
      ui/                             # Compose screens and HUD overlays
      audio/                          # Media3 managers
      ar/                             # ARCore GeoScan session bridge
      data/                           # Room entities, DAO, repositories
      worker/                         # WorkManager daemon jobs
      net/                            # PvP and event network clients
    src/main/cpp/
      engine/                         # C++ game engine
      renderer/vulkan/                # Vulkan backend
      ecs/                            # Entity-component system
      gameplay/                       # Combat, skills, loot, Merkle compiler
      world/                          # Streaming, procedural dungeon generation
      physics/                        # Character controller + destruction
      save/                           # Deterministic state serialization
      audio_bridge/                   # Native event emitter to Kotlin audio
  assets/
    bundles/                          # Packed world, character, audio assets
    shaders/                          # SPIR-V output
    metadata/asset_manifest.json
  docs/
    genesis_protocol_complete_spec.md
    art_asset_pipeline.md
```

### 2.2 Runtime Layering

| Layer | Language | Responsibility | Threading |
|---|---|---|---|
| Android Shell | Kotlin | lifecycle, permissions, Compose UI, Room, WorkManager, Media3, ARCore | main + coroutine dispatchers |
| Engine Bridge | JNI/C API | binary command queues between Kotlin and C++ | lock-free queues |
| Core Engine | C++20 | ECS, fixed-step simulation, combat, skills, save graph | simulation thread |
| Renderer | C++20/Vulkan | frame graph, PBR, particles, UI composition surface | render thread |
| IO/Streaming | C++20 + Kotlin | asset bundles, terrain tiles, texture mips, async save | IO pool |
| Network | Kotlin + C++ validation | PvP session orchestration, anti-cheat state hashes | IO dispatcher |
| Audio | Kotlin Media3 | music, audiobook, loop layering, SFX triggering | audio service thread |

### 2.3 Rendering Pipeline

The Vulkan renderer uses a frame graph with explicit resource lifetime tracking and transient attachment aliasing:

1. **Acquire swapchain image** from `ANativeWindow` hosted by `SurfaceView` below Compose overlays.
2. **CPU culling** for coarse region/streaming visibility using quadtree cells and portal cells for caverns.
3. **GPU culling** for instance batches with compute frustum and occlusion tests.
4. **Depth pre-pass** for opaque terrain, buildings, large props, and characters.
5. **Cluster build pass**: 16x9x24 clusters, supporting 256 visible punctual lights, 24 shadowed lights, and volumetric fog probes.
6. **Opaque PBR pass**: mobile-friendly metallic/roughness BRDF, packed material channels, vertex animation texture for foliage, cascaded shadows.
7. **Destructible decal pass**: crack masks, scorches, impact dents, glass spiderwebs, soil displacement stains.
8. **Character pass**: GPU skinning, 64-bone palette, per-character LOD material swaps, facial blendshape texture buffers.
9. **Transparent pass**: glass, AR overlays, phosphor code, spectral enemies, modem scream waveforms.
10. **Particle/VFX pass**: digital static, analog sparks, hash embers, dust, shards, foliage strips.
11. **ARCore composite pass** when GeoScan is active: camera image, depth occlusion, teal scan lines, hidden geometry masks.
12. **Post-processing**: exposure, painterly LUT, vignette, chromatic corruption during haunt events, TAA/FSR-style upscaling.
13. **Compose overlay** renders UI on top with shared state from native engine snapshots.

Target render budgets:

| Device tier | Resolution strategy | FPS | Triangle budget | Texture memory | Draw calls |
|---|---:|---:|---:|---:|---:|
| Low Vulkan 1.1 | 1280x720 dynamic | 30 | 450k visible | 512 MB | 450 |
| Mid Vulkan 1.1 | 1600x900 dynamic | 45 | 800k visible | 768 MB | 700 |
| High Vulkan 1.2 | 1920x1080 dynamic | 60 | 1.4M visible | 1.2 GB | 1,100 |

### 2.4 Memory Management

- **Vulkan Memory Allocator pattern**: large device-local heaps for static meshes/textures, upload ring buffers for streaming, per-frame transient uniform arenas.
- **Engine arenas**: frame arena reset every render frame; simulation arena for deterministic tick allocations; persistent world arena per loaded region.
- **Asset residency**: all assets have `Critical`, `VisibleSoon`, `Optional`, or `Evictable` residency. Combat arenas pin enemies, boss telegraphs, character animation clips, and hit VFX.
- **Texture streaming**: 256 m tiles request mips based on projected screen area; caverns stream by portal visibility; AR overlays stream as vector/SDF atlases.
- **Destruction pooling**: debris rigid bodies, particles, and shard meshes are pooled by material and region to avoid heap spikes during breaches.

### 2.5 Entity-Component System

Entities are 32-bit handles with generation counters. Components are structure-of-arrays chunks grouped by archetype.

Core components:

- `Transform`, `Hierarchy`, `Bounds`, `RenderMesh`, `SkinnedMesh`, `MaterialOverride`
- `RigidBody`, `CharacterController`, `NavAgent`, `DestructibleState`, `DoorLock`
- `Health`, `Shield`, `Entropy`, `Hashrate`, `Threat`, `Faction`, `LootDrop`
- `SkillLoadout`, `MerkleNodeState`, `Cooldowns`, `StatusEffects`, `CombatIntent`
- `AudioEmitter`, `AmbientZone`, `DialogueActor`, `CodexFragment`
- `GeoScanSignature`, `ARAnchorProxy`, `NetworkReplicated`, `AntiCheatHash`

Simulation order per fixed 30 Hz tick:

1. Apply queued input commands.
2. Advance cooldowns and status effects.
3. Resolve skill intents and Merkle passives.
4. Run AI behavior trees.
5. Step character controllers and physics.
6. Resolve hit volumes, shields, and damage.
7. Advance destructibility state machines.
8. Spawn loot, codex triggers, VFX, and audio events.
9. Hash authoritative state for saves/network validation.
10. Publish read-only snapshot to UI and renderer.

### 2.6 Physics and Destructibility

Use a native mobile physics backend with deterministic fixed-step wrappers, broadphase grid partitioning, capsule character controllers, convex hull collision for props, and prefractured large structures.

Destructibility state machine:

```text
INTACT
  on damage >= damageThreshold or breach command
DAMAGED
  apply crack decal, audio creak, loosen constraints
  on damage >= breakThreshold
BROKEN
  swap fractured visible mesh, enable primary chunks
  schedule loot/reveal checks
  on chunk sleep timeout or distance cull
DEBRIS
  replace chunks with pooled low-cost debris decals/instances
  persist only semantic result, not every shard
```

Material behavior:

| Material | Damage read | Break behavior | VFX/SFX | Persistence |
|---|---|---|---|---|
| Wood | cuts, splinters, hinge stress | planks detach along grain fracture map | dull cracks, sawdust, splinters | door open/broken state + loot |
| Masonry | radial cracks, chipped corners | chunks fall, dust cloud, rebar exposure | thud, grit, terracotta dust | opening silhouette + rubble decal |
| Glass | spiderweb crack mask | thin shards burst outward | sharp ping, teal shimmer for smart glass | broken pane flag |
| Metal | dents, sparks, bent seams | panels detach only at preauthored seams | analog sparks, strained groan | disabled panel state |
| Foliage | branch cuts, leaf loss | fronds bend/collapse, low mass | rustle, pollen/dust motes | respawn except quest blockers |
| Soil | impact pits, loosened cover | diggable mound displaced/reveals hatch | granular spill, muted thump | entrance revealed state |

Locked doors have two outcomes:

- **Lockpick**: non-destructive 4.2 s animation, noise radius 4 m, consumes lockpick durability, preserves stealth, yields full container loot table and codex chance.
- **Forced breach**: destructive 1.1 s windup + impact, noise radius 28 m, applies door fracture map, spawns debris and enemy alert, reduces loot quality by one roll step but may reveal emergency caches.

### 2.7 Input System

- Touch virtual sticks for movement/camera with adaptive opacity.
- Tap/hold skill buttons, swipe dodge, contextual interact, long-press GeoScan.
- Controller support using Android gamepad APIs with remappable actions.
- Accessibility presets: one-stick mode, auto-camera assist, hold/toggle sprint, enlarged combat telegraphs, reduced camera shake.

### 2.8 Combat Loop

Combat is a deterministic intent pipeline:

1. Kotlin input produces `PlayerCommand` with tick index.
2. Native combat validates stamina, Hashrate, cooldowns, animation lock, and range.
3. Skill execution creates hit volumes, projectiles, summons, shields, or field effects.
4. Merkle compiler applies selected passives as ordered modifiers.
5. Damage resolver calculates physical, electric, spectral, entropy, and proof damage.
6. Status resolver applies Burnout, Forked, Reorg, Grounded, Phased, Sybil Mark, or Cold Storage.
7. Animation graph chooses montage and root motion.
8. Audio/VFX bus emits events to Media3/SFX and Vulkan particles.
9. Anti-cheat hasher records command, RNG seed, and post-tick digest.

### 2.9 Skill Execution Pipeline

Each skill is data-defined:

```json
{
  "id": "cypherpunk_nonce_lance",
  "class": "Cypherpunk",
  "type": "projectile",
  "cost": { "hashrate": 18, "stamina": 6 },
  "cooldown_ms": 4200,
  "scales": { "proof": 1.35, "crit": 0.2 },
  "tags": ["ranged", "proof", "pierce", "chainable"],
  "merkleSockets": ["salt", "branch", "root"],
  "telegraph": "thin_terracotta_line",
  "antiCheat": "authoritative_tick_validated"
}
```

Execution phases: `CanCast`, `ReserveResources`, `Windup`, `Commit`, `Resolve`, `MerkleMutate`, `Recover`, `ReportDigest`.

### 2.10 Merkle Tree Progression Compiler

The Merkle Tree is a skill graph where leaves are learned behaviors, branches are synergy modifiers, and roots are class identity transformations. The compiler runs whenever equipment, Seed Phrases, passives, or class loadout changes.

Compiler rules:

- Leaves produce typed modifiers: `DamageMod`, `CooldownMod`, `ProjectileMod`, `SummonMod`, `TraversalMod`, `LootMod`.
- Branch nodes activate only if child leaf hashes satisfy adjacency and class constraints.
- Root nodes produce ultimate forms and global class rules.
- Seed Phrase tiles from the Mnemonic Board can salt node hashes and change modifier ordering.
- Compiler emits a deterministic `MerkleBuildHash` used for PvP matchmaking, anti-cheat, save integrity, and UI sharing.

Hash formula:

```text
LeafHash = SHA256(skillId | rank | seedSalt | itemAffixes)
BranchHash = SHA256(leftLeaf | rightLeaf | branchRule | seasonId)
RootHash = SHA256(branchA | branchB | classRoot | characterId)
PowerBudget = baseClassBudget + log2(totalHashrate + 1) * 12 + immutableBonuses
```

### 2.11 Hashrate Scaling Logic

Hashrate is both progression score and combat resource. It grows from quests, equipment, daemon contracts, Dark Pool clears, Seed Phrase discoveries, and seasonal achievements.

- **Combat Hashrate**: spendable burst resource regenerated by proof combos and grounding nodes.
- **Account Hashrate**: permanent power index used to unlock tiers and regions.
- **Threat Hashrate**: enemy scaling value derived from region corruption, player streak, co-op/PvP modifiers, and seasonal intensity.

Scaling:

```text
EffectivePower = sqrt(AccountHashrate) * ClassMultiplier + GearScore * 0.8 + MerklePower
EnemyPower = RegionBase * (1 + CorruptionTier * 0.18) * PartyScale * SiphonModifier
DamageOut = BaseSkill * (1 + ln(EffectivePower + 1) / 7) * AffixProduct
DamageTaken = EnemyBase / (1 + Armor / (Armor + 450 + ThreatHashrate * 0.2))
```

### 2.12 Procedural Dungeon Generator

Dark Pool Dungeons are deterministic from `seasonId`, `regionId`, `walletEcho`, and `dailyNonce`.

Generation stages:

1. Select theme: liquidity vault, drowned data center, offshore exchange, cold wallet catacomb.
2. Generate graph: start, 2-4 branches, 1 locked wing, 1 cursed shortcut, boss room.
3. Place rooms from authored kits with socket tags.
4. Solve traversal gates: breach, lockpick, scaffold, GeoScan, analog vehicle ramp.
5. Seed enemies using Sybil density and class counters.
6. Place loot with pity constraints and Immutable chance.
7. Bake minimap fog and AR signatures.
8. Emit dungeon manifest to save state and anti-cheat hash.

### 2.13 Audio Engine

Media3 + ExoPlayer handles long-running streams and compressed loops; native engine emits sample-accurate event markers for SFX. Audio layers:

- `Atmosphere`: region bed, wind, power hum, distant traffic, cavern resonance.
- `Haunt`: low-bit modem screams, whisper packets, corrupted prayer fragments.
- `Combat`: percussion intensity from threat heat and combo state.
- `Boss`: telegraph stems, heartbeat sidechain, phase-specific motifs.
- `Lore`: audiobook chapters with resumable playback and transcript sync.

### 2.14 Network Layer and PvP Siphon Protocol

PvP is opt-in asynchronous invasion with short live windows:

- Matchmaking uses `MerkleBuildHash`, Account Hashrate band, latency, and region.
- Server validates command streams, RNG seeds, cooldown constraints, movement envelopes, and damage digests.
- Invader appears as a **Siphon Phantom** with 85% normalized power and one PvP-specific entropy modifier.
- Defender can banish through combat, environmental breach traps, GeoScan reveal, or Zero-State relay activation.
- Rewards: Siphon Shards, cosmetic glitch trails, Darknet Bazaar tokens, codex echoes.

### 2.15 Anti-Cheat Logic

- Deterministic tick digest every 500 ms: position quantization, health, resources, cooldowns, RNG cursor, Merkle root, equipment hash.
- Server rejects impossible travel, cooldown underflow, unsigned save edits, abnormal loot seed churn, and physics outliers.
- Room save rows include HMAC signatures from Android Keystore keys.
- PvP rewards granted only after server receipt of command tape and digest consistency.
- Offline mode allows story and local dungeons but queues verifiable rewards until online reconciliation.

### 2.16 Save/Load Architecture

Room tables:

- `characters`: class, level, Account Hashrate, selected outfit, difficulty/accessibility.
- `inventory_items`: item id, tier, affixes, durability, bound status.
- `merkle_builds`: node states, seed salts, root hash, loadout name.
- `world_flags`: region unlocks, destructible semantic states, boss kills, POIs.
- `codex_entries`: lore fragments, audio logs, cinematic unlocks, transcript progress.
- `dungeons`: generated seeds, completion state, modifiers, rewards claimed.
- `pvp_events`: invasion records, queued rewards, digest status.

Large native blobs store compact world bitsets and are indexed by Room. Saves are atomic: write blob, verify hash, write Room transaction, then update active pointer.

## 3. Gameplay Systems

### 3.1 Classes

#### Cypherpunk

Role: ranged precision hacker-assassin who weaponizes cryptographic proof and social-engineering decoys.

- Resource: **Nonce Charge**, generated by weak-point hits and GeoScan reveals.
- Passive identity: critical hits fork projectiles into spectral afterimages.
- Ultimate: **Genesis Broadcast** fires a sky-to-ground proof beam that chains through marked enemies and opens hidden routes.

Skills:

| Skill | Type | Effect | Merkle modifiers |
|---|---|---|---|
| Nonce Lance | projectile | piercing proof bolt, bonus vs shields | double-salt pierce, ricochet branch, root chain |
| Cold Wallet Trap | deployable | freezes enemies in encrypted stasis | larger trigger, loot key chance, silent arm |
| Social Ghost | decoy | holographic lure emits false wealth signature | taunt strength, explosion, stealth reset |
| Packet Knife | melee | fast slash that uploads Sybil Mark | bleed fork, backstab refund, armor shred |
| Dust Mixer | field | obscures vision and lowers enemy accuracy | heal cloud, poison hash, longer duration |
| Genesis Broadcast | ultimate | massive beam and reveal pulse | season roots alter element |

#### Digital Wraith

Role: evasive phase fighter who crosses signal planes and punishes isolated enemies.

- Resource: **Phase Debt**, spent to ignore collision and paid back as vulnerability.
- Passive identity: dodges leave corrupt packets that detonate when enemies cross.
- Ultimate: **Null Possession** inhabits a target or machine, turning it against its faction.

Skills: Phase Step, Wraith Claw, Static Veil, Reorg Dash, Echo Split, Null Possession.

#### Grid Vanguard

Role: defensive brawler and grounding specialist who controls space with shields and electromagnetic anchors.

- Resource: **Ground Charge**, gained by blocking, parrying, and absorbing electric hazards.
- Passive identity: perfect blocks convert damage to team shields.
- Ultimate: **Blackout Bastion** drops a Faraday dome that disables projectiles, drones, and Sybil links.

Skills: Faraday Shield, Breaker Maul, Ground Return, Tesla Snare, Bastion Pull, Blackout Bastion.

#### Code Weaver

Role: summoner-engineer who compiles drones, turrets, scaffolds, and combat s
