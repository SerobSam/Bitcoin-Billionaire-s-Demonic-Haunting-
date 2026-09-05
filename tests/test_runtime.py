import json

import pytest

from src.runtime import Choice, Encounter, GameState, PlayerState


def test_vertical_slice_progression(tmp_path):
    game = GameState()
    assert game.phase == "investigate"

    game.investigate()
    assert game.player.progression.xp == 25
    game.begin_encounter(Encounter("Digital Wraith", 20, 5, 3))
    assert game.attack(10) is False
    assert game.player.health == 95
    assert game.player.corruption == 3
    assert game.attack(10) is True
    assert game.phase == "decode"
    assert game.player.inventory["corrupted_fragment"] == 1
    assert game.player.progression.xp == 25

    game.decode()
    assert game.phase == "choice"
    assert game.player.hashrate == 60
    assert game.player.progression.xp == 75
    game.choose(Choice.CLEANSE)
    assert game.phase == "complete"
    assert game.player.reputation == 2
    assert game.player.choices == ["cleanse"]
    assert game.player.progression.level == 2
    assert game.player.progression.xp == 100
    assert game.player.progression.upgrade_points == 1


def test_encounter_corruption_respects_player_resistance():
    game = GameState(player=PlayerState(corruption_resistance=2))
    game.investigate()
    game.begin_encounter(Encounter("Wraith", 10, 0, 5))
    game.attack(1)
    assert game.player.corruption == 3


def test_exploit_increases_power_and_corruption():
    game = GameState()
    game.investigate()
    game.begin_encounter(Encounter("Wraith", 1, 0, 0))
    game.attack(1)
    game.decode()
    game.choose(Choice.EXPLOIT)
    assert game.player.hashrate == 90
    assert game.player.corruption == 20
    assert game.player.reputation == -1
    assert game.player.progression.level == 2


def test_save_and_load_round_trip(tmp_path):
    path = tmp_path / "save.json"
    game = GameState()
    game.player.add_item("encrypted_shard", 2)
    game.player.corruption = 17
    game.player.corruption_resistance = 3
    game.player.choices.append("quarantine")
    game.player.earn_xp(137)
    game.save(path)

    loaded = GameState.load(path)
    assert loaded.mission == game.mission
    assert loaded.phase == game.phase
    assert loaded.player.inventory == {"encrypted_shard": 2}
    assert loaded.player.corruption == 17
    assert loaded.player.corruption_resistance == 3
    assert loaded.player.choices == ["quarantine"]
    assert loaded.player.progression == game.player.progression


def test_negative_corruption_resistance_is_rejected():
    with pytest.raises(ValueError, match="non-negative"):
        PlayerState(corruption_resistance=-1)


def test_cannot_attack_without_combat():
    game = GameState()
    with pytest.raises(RuntimeError):
        game.attack(10)


def test_cannot_continue_attack_after_player_defeat():
    game = GameState(player=PlayerState(health=5))
    game.begin_encounter(Encounter("Wraith", 20, 10, 0))

    assert game.attack(1) is False
    assert game.player_defeated

    with pytest.raises(RuntimeError, match="already defeated"):
        game.attack(1)
