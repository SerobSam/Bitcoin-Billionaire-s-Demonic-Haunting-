import random

from src.loot import LootTier, choose_tier, roll_drop


def test_weighted_selection_is_deterministic():
    tiers = [LootTier("scrap", "Scrap", 1000, 0, 1), LootTier("genesis", "Genesis", 25, 5, 6)]
    assert choose_tier(tiers, random.Random(7)).id == choose_tier(tiers, random.Random(7)).id


def test_roll_drop_respects_tier_affix_range():
    tiers = [LootTier("encrypted", "Encrypted", 1, 3, 4)]
    drop = roll_drop(tiers, seed=123)
    assert drop["tier"] == "encrypted"
    assert 3 <= drop["affixes"] <= 4
