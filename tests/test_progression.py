import pytest

from src.progression import PlayerProgression


def test_xp_levels_and_grants_upgrade_point():
    progression = PlayerProgression()
    assert progression.award_xp(100) == 1
    assert progression.level == 2
    assert progression.experience == 0
    assert progression.upgrade_points == 1


def test_xp_rolls_over_across_multiple_levels():
    progression = PlayerProgression()
    assert progression.award_xp(350) == 2
    assert progression.level == 3
    assert progression.experience == 50
    assert progression.upgrade_points == 2


def test_negative_xp_is_ignored():
    progression = PlayerProgression()
    assert progression.award_xp(-50) == 0
    assert progression.experience == 0


def test_upgrade_point_requires_balance():
    progression = PlayerProgression()
    with pytest.raises(RuntimeError, match="No upgrade points"):
        progression.spend_upgrade_point()
    progression.award_xp(100)
    progression.spend_upgrade_point()
    assert progression.upgrade_points == 0


def test_progression_round_trip():
    original = PlayerProgression()
    original.award_xp(250)
    restored = PlayerProgression.from_dict(original.to_dict())
    assert restored == original
