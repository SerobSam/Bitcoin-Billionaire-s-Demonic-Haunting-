from src.campaign import Campaign
from src.profile import CampaignProfile


def test_campaign_profile_carries_progression_upgrades_and_loadout(tmp_path):
    profile = CampaignProfile.new()
    profile.progression.add_xp(100)
    profile.upgrades.spend(profile.progression, "max_health")
    profile.upgrades.spend(profile.progression, "corruption_resistance") if profile.progression.upgrade_points else None
    profile.loadout.unlock("salt_circle")
    profile.player.add_item("cold_storage", 2)

    restored_path = tmp_path / "profile.json"
    profile.save(restored_path)
    restored = CampaignProfile.load(restored_path)

    assert restored.progression.level == 2
    assert restored.progression.upgrade_points == 0
    assert restored.upgrades.max_health_bonus == 1
    assert restored.upgrades.corruption_resistance == 0
    assert restored.player.max_health == 110
    assert restored.player.corruption_resistance == 0
    assert restored.loadout.is_unlocked("packet_burn")
    assert restored.loadout.is_unlocked("salt_circle")
    assert restored.player.inventory["cold_storage"] == 2


def test_campaign_profile_persists_corruption_resistance_upgrade(tmp_path):
    profile = CampaignProfile.new()
    profile.progression.add_xp(100)
    profile.upgrades.spend(profile.progression, "corruption_resistance")
    profile.apply_upgrades()

    restored_path = tmp_path / "profile.json"
    profile.save(restored_path)
    restored = CampaignProfile.load(restored_path)

    assert restored.upgrades.corruption_resistance == 1
    assert restored.player.corruption_resistance == 1


def test_mission_rewards_persist_on_profile():
    campaign = Campaign.load("data/missions/campaign.json")
    profile = CampaignProfile.new()

    campaign.complete_mission("bel_air_blackout")
    rewards = profile.grant_mission_rewards(campaign, "bel_air_blackout")

    assert rewards == ("salt_circle",)
    assert profile.loadout.is_unlocked("salt_circle")

    campaign.complete_mission("irvine_consensus")
    profile.grant_mission_rewards(campaign, "irvine_consensus")
    assert profile.loadout.is_unlocked("salt_circle")
    assert profile.loadout.is_unlocked("cold_storage")


def test_shared_profile_player_keeps_state_between_missions():
    profile = CampaignProfile.new()
    first_player = profile.mission_player()
    first_player.evidence = 3
    first_player.earn_xp(25)

    second_player = profile.mission_player()

    assert second_player is first_player
    assert second_player.evidence == 3
    assert second_player.progression.xp == 25
