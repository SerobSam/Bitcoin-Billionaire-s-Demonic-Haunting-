from pathlib import Path

from src.loot import load_tiers, roll_drop


ROOT = Path(__file__).resolve().parents[1]


def test_seeded_loot_roll_is_reproducible():
    tiers = load_tiers(ROOT / "assets" / "gameplay" / "loot_tiers.json")
    assert roll_drop(tiers, 20260905) == roll_drop(tiers, 20260905)


def test_seeded_affixes_stay_within_tier_range():
    tiers = load_tiers(ROOT / "assets" / "gameplay" / "loot_tiers.json")
    drop = roll_drop(tiers, 20260905)
    tier = next(t for t in tiers if t.id == drop["tier"])
    assert tier.affix_min <= drop["affixes"] <= tier.affix_max
