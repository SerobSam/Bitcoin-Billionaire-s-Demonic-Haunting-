import pytest

from src.loadout import AbilityLoadout


def test_default_loadout_starts_with_packet_burn():
    loadout = AbilityLoadout()
    assert loadout.is_unlocked("packet_burn")
    assert not loadout.is_unlocked("salt_circle")


def test_unlock_adds_ability_and_preserves_order():
    loadout = AbilityLoadout()
    ability = loadout.unlock("salt_circle")
    assert ability.ability_id == "salt_circle"
    assert [item.ability_id for item in loadout.available()] == ["packet_burn", "salt_circle"]


def test_locked_ability_is_rejected():
    with pytest.raises(RuntimeError, match="locked"):
        AbilityLoadout().require("cold_storage")


def test_loadout_round_trip():
    original = AbilityLoadout()
    original.unlock("cold_storage")
    restored = AbilityLoadout.from_dict(original.to_dict())
    assert restored.to_dict() == original.to_dict()


def test_unknown_ability_is_explicit():
    with pytest.raises(KeyError, match="Unknown ability"):
        AbilityLoadout().unlock("not_real")
