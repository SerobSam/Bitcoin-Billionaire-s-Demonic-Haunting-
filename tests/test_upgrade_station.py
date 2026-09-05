import pytest

from src.profile import CampaignProfile
from src.upgrade_station import UpgradeStation


def test_upgrade_station_lists_progression_options():
    station = UpgradeStation(CampaignProfile.new())
    assert [option.upgrade_id for option in station.options()] == [
        "max_health",
        "hashrate",
        "corruption_resistance",
    ]


def test_upgrade_station_spends_point_and_applies_bonus():
    profile = CampaignProfile.new()
    profile.progression.upgrade_points = 1
    station = UpgradeStation(profile)

    option = station.purchase("corruption_resistance")

    assert option.upgrade_id == "corruption_resistance"
    assert station.available_points == 0
    assert profile.upgrades.corruption_resistance == 1
    assert profile.player.corruption_resistance == 1


def test_upgrade_station_rejects_unknown_upgrade():
    profile = CampaignProfile.new()
    profile.progression.upgrade_points = 1
    station = UpgradeStation(profile)

    with pytest.raises(KeyError, match="Unknown upgrade"):
        station.purchase("genesis_ascension")

    assert station.available_points == 1


def test_upgrade_station_requires_available_point():
    station = UpgradeStation(CampaignProfile.new())

    with pytest.raises(RuntimeError, match="No upgrade points"):
        station.purchase("max_health")
