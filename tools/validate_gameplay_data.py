#!/usr/bin/env python3
"""Validate Genesis Protocol gameplay data tables."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


def fail(message: str) -> None:
    print(f"gameplay validation failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def validate_classes() -> int:
    data = load("assets/gameplay/classes.json")
    classes = data.get("classes", [])
    if len(classes) != 4:
        fail("expected exactly four playable classes")
    skill_ids: set[str] = set()
    for cls in classes:
        for field in ["id", "name", "resource", "role", "passive_identity", "ultimate", "skills", "passives"]:
            if field not in cls:
                fail(f"class {cls.get('id', '<unknown>')} missing {field}")
        if len(cls["skills"]) != 6:
            fail(f"class {cls['id']} must define six active skills")
        if len(cls["passives"]) != 12:
            fail(f"class {cls['id']} must define twelve passives")
        ultimate_count = 0
        for skill in cls["skills"]:
            if skill["id"] in skill_ids:
                fail(f"duplicate skill id {skill['id']}")
            skill_ids.add(skill["id"])
            if not skill["id"].startswith(cls["id"] + "_"):
                fail(f"skill {skill['id']} must be prefixed by class id {cls['id']}")
            if skill["cost_hashrate"] < 0 or skill["cooldown_ms"] <= 0:
                fail(f"skill {skill['id']} has invalid cost or cooldown")
            if not skill.get("tags"):
                fail(f"skill {skill['id']} must define tags")
            if skill["type"] == "ultimate":
                ultimate_count += 1
        if ultimate_count != 1:
            fail(f"class {cls['id']} must define exactly one active ultimate")
    return len(skill_ids)


def validate_loot() -> int:
    data = load("assets/gameplay/loot_tiers.json")
    tiers = data.get("tiers", [])
    expected = ["scrap", "copper", "silicon", "encrypted", "sovereign", "genesis", "immutable"]
    if [tier.get("id") for tier in tiers] != expected:
        fail("loot tiers must be ordered Scrap through Immutable")
    previous_weight = None
    for tier in tiers:
        if not HEX_RE.match(tier["color"]):
            fail(f"tier {tier['id']} has invalid color")
        if tier["affix_min"] > tier["affix_max"]:
            fail(f"tier {tier['id']} has inverted affix range")
        if previous_weight is not None and tier["drop_weight"] > previous_weight:
            fail("drop weights must not increase with rarity")
        previous_weight = tier["drop_weight"]
    return len(tiers)


def validate_merkle() -> int:
    data = load("assets/gameplay/merkle_rules.json")
    if len(data.get("seed_phrase_slots", [])) != 12:
        fail("Mnemonic Board must define twelve seed phrase slots")
    if set(data.get("node_types", [])) != {"leaf", "branch", "root"}:
        fail("Merkle node types must be leaf, branch, root")
    return len(data["modifier_types"])


def main() -> None:
    skill_count = validate_classes()
    tier_count = validate_loot()
    modifier_count = validate_merkle()
    print(f"validated {skill_count} skills, {tier_count} loot tiers, and {modifier_count} Merkle modifiers")


if __name__ == "__main__":
    main()
  
