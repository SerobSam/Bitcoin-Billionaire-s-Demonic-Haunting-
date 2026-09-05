import pytest

from src.player_progression import PlayerProgression
from src.runtime import PlayerState
from src.upgrades import PlayerUpgrades


def test_spend_upgrade_point_and_apply_bonus():
    progression = PlayerProgression(upgrade_points=2)
    upgrades = PlayerUpgrades()

    upgrades.spend(progression, "max_health")
    upgrades.spend(progression, "hashrate")

    player = PlayerState()
    upgrades.apply(player)

    assert progression.upgrade_points == 0
    assert player.max_health == 110
    assert player.hashrate == 55


def test_no_points_and_unknown_upgrade_are_rejected():
    progression = PlayerProgression()
    upgrades = PlayerUpgrades()

    with pytest.raises(RuntimeError, match="No upgrade points"):
        upgrades.spend(progression, "hashrate")

    progression.upgrade_points = 1
    with pytest.raises(KeyError, match="Unknown upgrade"):
        upgrades.spend(progression, "telepathy")


def test_upgrade_serialization_round_trip():
    upgrades = PlayerUpgrades(max_health_bonus=2, hashrate_bonus=1, corruption_resistance=3, points_spent=6)
    assert PlayerUpgrades.from_dict(upgrades.to_dict()) == upgrades
