from datetime import date

import pytest

from src.live_ops import CONTENT_ADD_ONS, DLC_MISSIONS, LiveOpsWallet, RotatingEventSchedule
from src.runtime import Choice, Encounter, GameState


def test_season_pass_free_and_premium_rewards():
    game = GameState()
    game.season_pass.add_xp(500, multiplier=1.0)

    assert game.season_pass.tier == 3
    assert game.season_pass.claim(1) == "season_cache_1"
    game.season_pass.unlock_premium()
    assert game.season_pass.claim(1, premium=True) == "premium_cache_1"

    with pytest.raises(ValueError, match="already claimed"):
        game.season_pass.claim(1)


def test_runtime_claims_season_and_event_rewards():
    game = GameState()
    game.season_pass.add_xp(250)
    assert game.claim_season_reward(1) == "season_cache_1"
    assert game.player.inventory["season_cache_1"] == 1
    assert game.claim_active_event_reward() == game.active_event.reward_item
    with pytest.raises(ValueError, match="already claimed"):
        game.claim_active_event_reward()


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
    game.begin_encounter(Encounter("Chrome Oni", 45, 11, 6))
    assert game.attack(50)
    game.decode()
    game.choose(Choice.QUARANTINE)

    assert game.phase == "complete"
    assert game.player.inventory["neon_shard"] == 1
    assert "neon_tokyo_blackout" in game.completed_dlc_missions
    assert game.player.evidence >= 3
    assert game.player.progression.xp > 0
    assert game.season_pass.xp > 0


@pytest.mark.parametrize("add_on_id", tuple(CONTENT_ADD_ONS))
def test_all_dlc_chains_require_and_support_sequential_runtime_play(add_on_id):
    add_on = CONTENT_ADD_ONS[add_on_id]
    wallet = LiveOpsWallet(credits=add_on.price_credits)
    wallet.purchase_add_on(add_on_id)
    game = GameState()

    first_id, second_id = add_on.missions
    game.begin_dlc_mission(wallet, first_id)
    game.investigate()
    first = DLC_MISSIONS[first_id]
    game.begin_encounter(Encounter(first.enemy_name, first.enemy_health, first.enemy_damage, first.corruption_on_hit))
    assert game.attack(first.enemy_health)
    game.decode()
    game.choose(Choice.CLEANSE)

    assert first_id in game.completed_dlc_missions
    game.begin_dlc_mission(wallet, second_id)
    assert game.dlc_mission_id == second_id


def test_dlc_chain_cannot_skip_first_mission():
    wallet = LiveOpsWallet(credits=900)
    wallet.purchase_add_on("neon_tokyo")
    game = GameState()
    with pytest.raises(RuntimeError, match="Previous DLC mission"):
        game.begin_dlc_mission(wallet, "shibuya_wraith_hunt")


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
    game.claim_active_event_reward()
    game.completed_dlc_missions.add("neon_tokyo_blackout")
    game.save(path)

    loaded = GameState.load(path)
    assert loaded.season_pass.to_dict() == game.season_pass.to_dict()
    assert loaded.claimed_event_ids == game.claimed_event_ids
    assert loaded.completed_dlc_missions == game.completed_dlc_missions
