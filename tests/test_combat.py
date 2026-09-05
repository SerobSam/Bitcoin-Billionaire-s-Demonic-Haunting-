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


def test_corruption_resistance_reduces_ability_gain():
    loadout = AbilityLoadout()
    loadout.unlock("salt_circle")
    combat = CombatSystem(
        Combatant(100, 100, corruption=0),
        Combatant(100, 100),
        loadout,
        corruption_resistance=2,
    )
    combat.use("salt_circle")
    assert combat.player.corruption == 3


def test_corruption_resistance_can_fully_block_gain():
    loadout = AbilityLoadout()
    loadout.unlock("cold_storage")
    combat = CombatSystem(
        Combatant(100, 100, corruption=0),
        Combatant(100, 100),
        loadout,
        corruption_resistance=10,
    )
    combat.use("cold_storage")
    assert combat.player.corruption == 0


def test_negative_corruption_resistance_is_rejected():
    with pytest.raises(ValueError, match="non-negative"):
        CombatSystem(Combatant(100, 100), Combatant(100, 100), corruption_resistance=-1)


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


def test_enemy_attack_applies_damage_and_resisted_corruption():
    combat = CombatSystem(
        Combatant(100, 100, corruption=10),
        Combatant(100, 100),
        corruption_resistance=3,
    )
    assert combat.enemy_attack(12, corruption_gain=7) == 12
    assert combat.player.health == 88
    assert combat.player.corruption == 14
    assert combat.turn == 1


def test_enemy_attack_cannot_continue_after_player_defeat():
    combat = CombatSystem(Combatant(10, 10), Combatant(100, 100))
    combat.enemy_attack(20)
    assert combat.player_defeated
    with pytest.raises(RuntimeError, match="already defeated"):
        combat.enemy_attack(1)


def test_enemy_attack_rejects_a_defeated_enemy():
    combat = CombatSystem(Combatant(100, 100), Combatant(1, 1))
    combat.basic_attack(1)
    assert combat.defeated
    with pytest.raises(RuntimeError, match="enemy"):
        combat.enemy_attack(1)
