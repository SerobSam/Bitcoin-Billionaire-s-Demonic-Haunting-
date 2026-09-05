"""Command-line entry point for the Genesis Protocol campaign slice."""
from __future__ import annotations

import json
from pathlib import Path

from campaign import Campaign
from darkpool import DarkPoolDescentMission
from irvine import IrvineConsensusMission
from loot import load_tiers, roll_drop
from mission import BelAirBlackoutMission
from runtime import Choice
from zerostate import ZeroStateRelayMission

ROOT = Path(__file__).resolve().parents[1]


def load_entities() -> dict:
    """Load the narrative entity seed data."""
    with (ROOT / "data" / "entities.json").open(encoding="utf-8") as entity_file:
        return json.load(entity_file)


def run_vertical_slice() -> BelAirBlackoutMission:
    """Run the deterministic first-mission objective sequence."""
    mission = BelAirBlackoutMission()
    mission.reach_estate()
    mission.scan_terminal()
    while not mission.survive_wraith(20):
        pass
    mission.decode_fragment()
    mission.make_choice(Choice.QUARANTINE)
    tiers = load_tiers(ROOT / "assets" / "gameplay" / "loot_tiers.json")
    drop = roll_drop(tiers, seed=20260905)
    mission.game.player.add_item(f"{drop['tier']}_cache")
    mission.extract()
    return mission


def run_irvine_consensus() -> IrvineConsensusMission:
    """Run the deterministic second-mission objective sequence."""
    mission = IrvineConsensusMission()
    mission.enter_suburbs()
    mission.trace_consensus()
    while not mission.break_vanguard(25):
        pass
    mission.decode_vote()
    mission.make_choice(Choice.QUARANTINE)
    mission.extract()
    return mission


def run_dark_pool_descent() -> DarkPoolDescentMission:
    """Run the deterministic third-mission objective sequence."""
    mission = DarkPoolDescentMission()
    mission.enter_dungeons()
    mission.find_choir()
    while not mission.break_warden(30):
        pass
    mission.decode_liturgy()
    mission.make_choice(Choice.QUARANTINE)
    mission.extract()
    return mission


def run_zero_state_relay() -> ZeroStateRelayMission:
    """Run the deterministic campaign finale sequence."""
    mission = ZeroStateRelayMission()
    mission.reach_relay()
    mission.stabilize_relay()
    while not mission.break_entity_phase1(40):
        pass
    mission.decode_genesis()
    while not mission.break_entity_phase2(40):
        pass
    mission.make_choice(Choice.QUARANTINE)
    mission.extract()
    return mission


def main() -> None:
    entities = load_entities()
    protagonist = entities["playable_character"]
    antagonist = entities["antagonist"]
    campaign = Campaign.load(ROOT / "data" / "missions" / "campaign.json")

    print(f"{protagonist['name']} vs. {antagonist['name']}")
    print("Genesis Protocol — Campaign Demo")

    bel_air = run_vertical_slice()
    campaign.complete_mission("bel_air_blackout")
    print(f"Bel Air complete: {bel_air.complete}")
    print(f"Bel Air choice: {bel_air.game.player.choices[-1]}")

    if campaign.next_mission("bel_air_blackout") is None:
        raise RuntimeError("Campaign failed to unlock Irvine Consensus")
    irvine = run_irvine_consensus()
    campaign.complete_mission("irvine_consensus")
    print(f"Irvine complete: {irvine.complete}")
    print(f"Irvine health: {irvine.game.player.health}/{irvine.game.player.max_health}")
    print(f"Irvine corruption: {irvine.game.player.corruption}%")
    print(f"Irvine evidence: {irvine.game.player.evidence}")
    print(f"Irvine choice: {irvine.game.player.choices[-1]}")

    if campaign.next_mission("irvine_consensus") is None:
        raise RuntimeError("Campaign failed to unlock Dark Pool Descent")
    dark_pool = run_dark_pool_descent()
    campaign.complete_mission("dark_pool_descent")
    print(f"Dark Pool complete: {dark_pool.complete}")
    print(f"Dark Pool health: {dark_pool.game.player.health}/{dark_pool.game.player.max_health}")
    print(f"Dark Pool corruption: {dark_pool.game.player.corruption}%")
    print(f"Dark Pool evidence: {dark_pool.game.player.evidence}")
    print(f"Dark Pool choice: {dark_pool.game.player.choices[-1]}")

    if campaign.next_mission("dark_pool_descent") is None:
        raise RuntimeError("Campaign failed to unlock Zero-State Relay")
    finale = run_zero_state_relay()
    campaign.complete_mission("zero_state_relay")
    print(f"Zero-State Relay complete: {finale.complete}")
    print(f"Final health: {finale.game.player.health}/{finale.game.player.max_health}")
    print(f"Final hashrate: {finale.game.player.hashrate}")
    print(f"Final corruption: {finale.game.player.corruption}%")
    print(f"Final evidence: {finale.game.player.evidence}")
    print(f"Final choice: {finale.game.player.choices[-1]}")
    print(f"Genesis Core: {finale.game.player.inventory.get('genesis_core', 0)}")
    print(f"Next mission: {campaign.next_mission('zero_state_relay') or 'Campaign complete'}")


if __name__ == "__main__":
    main()
