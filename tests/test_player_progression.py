from src.player_progression import PlayerProgression


def test_xp_levels_and_rollover():
    progression = PlayerProgression()

    assert progression.xp_to_next_level == 100
    assert progression.add_xp(99) == 0
    assert progression.level == 1
    assert progression.xp == 99

    assert progression.add_xp(1) == 1
    assert progression.level == 2
    assert progression.xp == 0
    assert progression.upgrade_points == 1
    assert progression.xp_to_next_level == 150


def test_large_xp_gain_can_cross_multiple_levels():
    progression = PlayerProgression()

    assert progression.add_xp(400) == 2
    assert progression.level == 3
    assert progression.xp == 150
    assert progression.upgrade_points == 2


def test_invalid_progression_values_are_rejected():
    for kwargs in ({"level": 0}, {"xp": -1}, {"upgrade_points": -1}):
        try:
            PlayerProgression(**kwargs)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid progression value was accepted")


def test_serialization_round_trip():
    original = PlayerProgression(level=4, xp=37, upgrade_points=3)
    restored = PlayerProgression.from_dict(original.to_dict())

    assert restored == original
