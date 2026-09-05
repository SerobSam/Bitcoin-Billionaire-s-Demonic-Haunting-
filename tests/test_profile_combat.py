from src.combat import CombatSystem, Combatant
from src.profile import CampaignProfile


def test_combat_from_profile_uses_persistent_upgrades_and_loadout():
    profile = CampaignProfile.new()
    profile.player.progression.add_xp(100)
    profile.upgrades.spend(profile.progression, "corruption_resistance")
    profile.upgrades.apply(profile.player)
    profile.loadout.unlock("salt_circle")

    combat = CombatSystem.from_profile(profile, Combatant(health=40, max_health=40))

    combat.use("salt_circle")

    assert combat.player.corruption == 4
    assert combat.enemy.health == 22
    assert combat.corruption_resistance == 1


def test_combat_sync_persists_health_and_corruption_to_profile():
    profile = CampaignProfile.new()
    profile.player.corruption = 10
    combat = CombatSystem.from_profile(profile, Combatant(health=25, max_health=25))

    combat.use("packet_burn")
    combat.sync_player_to_profile(profile)

    assert profile.player.health == combat.player.health
    assert profile.player.max_health == combat.player.max_health
    assert profile.player.corruption == combat.player.corruption
