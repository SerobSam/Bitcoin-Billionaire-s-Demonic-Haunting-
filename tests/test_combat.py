import pytest

from src.combat import ABILITIES, CombatSystem, Combatant
from src.loadout import AbilityLoadout


def test_packet_burn_deals_damage_and_starts_cooldown():
    combat = CombatSystem(Combatant(100, 100), Combatant(100, 100))
    assert combat.use("packet_burn") == 28
    assert combat.enemy.health == 72
    with pytest.raises(RuntimeError, match="cooldown"):
        combat.use("packet_burn")


def test_basic_attack_ticks_cooldowns():
    combat = CombatSystem(Combatant(100, 100), Combatant(100, 100))
    combat.use("packet_burn")
    combat.basic_attack()
    assert combat.cooldowns["packet_burn"].remaining == 0


def test_ability_corruption_gain_is_applied():
    combat = CombatSystem(Combatant(100, 100, corruption=0), Combatant(100, 100))
    combat.use("salt_circle")
    assert combat.player.corruption == ABILITIES["salt_circle"].corruption_gain


def test_locked_ability_cannot_be_used():
    loadout = AbilityLoadout()
    combat = CombatSystem(Combatant(100, 100), Combatant(100, 100), loadout)
    with pytest.raises(RuntimeError, match="locked"):
        combat.use("salt_circle")


def test_unlocked_ability_can_be_used():
    loadout = AbilityLoadout()
    loadout.unlock("salt_circle")
    combat = CombatSystem(Combatant(100, 100), Combatant(100, 100), loadout)
    combat.use("salt_circle")
    assert combat.enemy.health == 82


def test_unknown_ability_is_explicit():
    combat = CombatSystem(Combatant(100, 100), Combatant(100, 100))
    with pytest.raises(KeyError, match="Unknown ability"):
        combat.use("not_real")
