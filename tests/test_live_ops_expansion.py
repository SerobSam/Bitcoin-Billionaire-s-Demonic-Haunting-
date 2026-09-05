from datetime import date

import pytest

from src.dlc_missions import PlayableDLCMission, missions_for_add_on
from src.live_ops import RotatingEventSchedule, SeasonPass
from src.runtime import Choice


def finish_mission(mission: PlayableDLCMission) -> None:
    mission.investigate()
    while not mission.attack(100):
        pass
    mission.decode()
    mission.choose(Choice.QUARANTINE)
    assert mission.extract()
    assert mission.completed


def test_season_pass_free_and_premium_tracks():
    season = SeasonPass()
    season.add_xp(500)
    assert season.tier == 3
    assert season.claim(1) == "season_cache_1"
    with pytest.raises(ValueError, match="already claimed"):
        season.claim(1)
    with pytest.raises(ValueError, match="Premium reward track is locked"):
        season.claim(1, premium=True)
    season.unlock_premium()
    assert season.claim(1, premium=True) == "premium_cache_1"


def test_season_pass_xp_is_capped_and_rejects_invalid_values():
    season = SeasonPass()
    season.add_xp(999999)
    assert season.maxed
    assert season.xp == 2500
    with pytest.raises(ValueError):
        season.add_xp(-1)


def test_rotating_events_are_deterministic():
    schedule = RotatingEventSchedule()
    assert schedule.event_for(date(2026, 1, 1)).event_id == "blood_moon"
    assert schedule.event_for(date(2026, 1, 2)).event_id == "hash_rush"
    assert schedule.window(date(2026, 1, 7)) == (date(2026, 1, 5), date(2026, 1, 11))


def test_all_three_dlc_chains_are_playable_through_runtime():
    expected = {
        "neon_tokyo": ("neon_tokyo_blackout", "shibuya_wraith_hunt"),
        "hells_datacenter": ("datacenter_descent", "server_cathedral"),
        "genesis_epilogue": ("aftershock", "zero_day_epilogue"),
    }
    for add_on_id, mission_ids in expected.items():
        assert tuple(spec.mission_id for spec in missions_for_add_on(add_on_id)) == mission_ids
        for mission_id in mission_ids:
            mission = PlayableDLCMission.start(mission_id)
            finish_mission(mission)
            assert mission.game.phase == "complete"
            assert mission.game.player.inventory[mission.spec.loot] == 1
