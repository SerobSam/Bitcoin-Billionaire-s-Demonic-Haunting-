"""Command-line entry point for the Genesis Protocol vertical slice."""
from __future__ import annotations

import json
from pathlib import Path

from mission import BelAirBlackoutMission
from runtime import Choice
from loot import load_tiers, roll_drop

ROOT = Path(__file__).resolve().parents[1]


def load_entities() -> dict:
    """Load the narrative entity seed data."""
    with (ROOT / "data" / "entities.json").open(encoding="utf-8") as entity_file:
        return json.load(entity_file)


def run_vertical_slice() -> BelAirBlackoutMission:
    """Run the deterministic first-mission objective sequence and return its state."""
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


def main() -> None:
    entities = load_entities()
    protagonist = entities["playable_character"]
    antagonist = entities["antagonist"]
    print(f"{protagonist['name']} vs. {antagonist['name']}")
    print("Genesis Protocol — Bel Air Blackout")
    mission = run_vertical_slice()
    game = mission.game
    print(f"Mission complete: {mission.complete}")
    print(f"Health: {game.player.health}/{game.player.max_health}")
    print(f"Hashrate: {game.player.hashrate}")
    print(f"Corruption: {game.player.corruption}%")
    print(f"Evidence: {game.player.evidence}")
    print(f"Inventory: {game.player.inventory}")
    print(f"Choice: {game.player.choices[-1]}")


if __name__ == "__main__":
    main()
