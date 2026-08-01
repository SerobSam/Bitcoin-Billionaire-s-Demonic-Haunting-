"""Prototype data entry point for Bitcoin Billionaire's Demonic Haunting."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_entities() -> dict:
    """Load the narrative entity seed data."""
    with (ROOT / "data" / "entities.json").open(encoding="utf-8") as entity_file:
        return json.load(entity_file)


def main() -> None:
    """Print a concise prototype roster for quick verification."""
    entities = load_entities()
    protagonist = entities["playable_character"]
    antagonist = entities["antagonist"]
    print(f"{protagonist['name']} vs. {antagonist['name']}")
    print("Starting tools:")
    for tool in protagonist["starting_tools"]:
        print(f"- {tool}")


if __name__ == "__main__":
    main()
  
