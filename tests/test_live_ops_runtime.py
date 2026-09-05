from datetime import date

import pytest

from src.live_ops import LiveOpsWallet, RotatingEventSchedule
from src.runtime import Choice, GameState


def test_season_pass_free_and_premium_rewards():
    game = GameState()
    game.season_pass.add_xp(500, multiplier=1.0)

    assert game.season_pass.tier == 3
    assert game.season_pass.claim(1) == "season_cache_1"
    game.season_pass.unlock_premium()
    assert game.season_pass.claim(1, premium=True) == "premium_cache_1"

    with pytest.raises(ValueError, match="already claimed"):
        game.season_pass.claim(1)


def test_rotating_event_is_deterministic_and_has_week_window():
    schedule = RotatingEventSchedule()
    first = schedule.event_for(date(2026, 1, 1))
    same = schedule.event_for(date(2026, 1, 1))
    start, end = schedule.window(date(2026, 9, 5))

    assert first.event_id == same.event_id
    assert (end - start).days == 6
    assert start <= date(2026, 9, 5) <= end


def test_dlc_mission_is_playable_through_runtime():
    wallet = LiveOpsWallet(credits=900)
    wallet.purchase_add_on("neon_tokyo")
    game = GameState()

    game.begin_dlc_mission(wallet, "neon_tokyo_blackout")
    game.investigate()
    game.begin_encounter(game.encounter or __import__("src.runtime", fromlist=["Encounter"]).Encounter("Chrome Oni", 45, 11, 6))
    while not game.attack(50):
        pass
    game.decode()
    game.choose(Choice.QUARANTINE)

    assert game.phase == "complete"
    assert game.player.inventory["neon_shard"] == 1
    assert game.player.evidence >= 3
    assert game.player.progression.xp > 0
    assert game.season_pass.xp > 0


def test_unowned_dlc_cannot_start():
    game = GameState()
    wallet = LiveOpsWallet()
    with pytest.raises(PermissionError, match="not owned"):
        game.begin_dlc_mission(wallet, "server_cathedral")


def test_live_ops_state_round_trips(tmp_path):
    path = tmp_path / "save.json"
    game = GameState()
    game.season_pass.add_xp(250)
    game.season_pass.unlock_premium()
    game.season_pass.claim(1, premium=True)
    game.save(path)

    loaded = GameState.load(path)
    assert loaded.season_pass.to_dict() == game.season_pass.to_dict()
