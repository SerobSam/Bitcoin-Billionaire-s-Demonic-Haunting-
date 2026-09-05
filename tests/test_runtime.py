import json

import pytest

from src.runtime import Choice, Encounter, GameState


def test_vertical_slice_progression(tmp_path):
    game = GameState()
    assert game.phase == "investigate"

    game.investigate()
    assert game.player.progression.xp == 25
    game.begin_encounter(Encounter("Digital Wraith", 20, 5, 3))
    assert game.attack(10) is False
    assert game.player.health == 95
    assert game.attack(10) is True
    assert game.phase == "decode"
    assert game.player.inventory["corrupted_fragment"] == 1
    assert game.player.progression.xp == 125

    game.decode()
    assert game.phase == "choice"
    assert game.player.hashrate == 60
    assert game.player.progression.xp == 175
    game.choose(Choice.CLEANSE)
    assert game.phase == "complete"
    assert game.player.reputation == 2
    assert game.player.choices == ["cleanse"]
    assert game.player.progression.level == 2
    assert game.player.progression.xp == 100
    assert game.player.progression.upgrade_points == 1


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
    game.player.choices.append("quarantine")
    game.player.earn_xp(137)
    game.save(path)

    loaded = GameState.load(path)
    assert loaded.mission == game.mission
    assert loaded.phase == game.phase
    assert loaded.player.inventory == {"encrypted_shard": 2}
    assert loaded.player.corruption == 17
    assert loaded.player.choices == ["quarantine"]
    assert loaded.player.progression == game.player.progression


def test_cannot_attack_without_combat():
    game = GameState()
    with pytest.raises(RuntimeError):
        game.attack(10)
