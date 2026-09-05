import pytest

from src.live_ops import SeasonPass
from src.live_ops_rewards import claim_season_reward, grant_event_reward


def test_claim_season_reward_redeems_into_inventory():
    season = SeasonPass()
    season.add_xp(250)
    inventory = {}

    assert claim_season_reward(season, inventory, 1) == "season_cache_1"
    assert inventory == {"season_cache_1": 1}


def test_premium_claim_requires_unlocked_track():
    season = SeasonPass()
    season.add_xp(250)
    with pytest.raises(ValueError, match="locked"):
        claim_season_reward(season, {}, 1, premium=True)


def test_premium_claim_redeems_inventory_after_unlock():
    season = SeasonPass()
    season.add_xp(250)
    season.unlock_premium()
    inventory = {}

    assert claim_season_reward(season, inventory, 1, premium=True) == "premium_cache_1"
    assert inventory["premium_cache_1"] == 1


def test_event_reward_requires_an_item():
    with pytest.raises(ValueError, match="cannot be empty"):
        grant_event_reward({}, "")
