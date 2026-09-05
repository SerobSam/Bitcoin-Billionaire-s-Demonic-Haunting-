import json

import pytest

from src.campaign import Campaign
from src.loadout import AbilityLoadout


def campaign(tmp_path):
    path = tmp_path / "campaign.json"
    path.write_text(json.dumps({
        "missions": [
            {"id": "one", "title": "One", "region": "A", "unlock": None, "next": "two", "rewards": ["salt_circle"]},
            {"id": "two", "title": "Two", "region": "B", "unlock": "one", "next": "three", "rewards": ["cold_storage"]},
            {"id": "three", "title": "Three", "region": "C", "unlock": "two", "next": None},
        ]
    }), encoding="utf-8")
    return Campaign.load(path)


def test_campaign_unlocks_sequentially(tmp_path):
    game = campaign(tmp_path)
    assert [m.mission_id for m in game.available()] == ["one"]
    game.complete_mission("one")
    assert [m.mission_id for m in game.available()] == ["one", "two"]
    assert game.next_mission("one").mission_id == "two"


def test_locked_mission_cannot_be_completed(tmp_path):
    game = campaign(tmp_path)
    with pytest.raises(RuntimeError, match="locked"):
        game.complete_mission("two")


def test_unknown_mission_is_explicit(tmp_path):
    game = campaign(tmp_path)
    with pytest.raises(KeyError, match="Unknown mission"):
        game.complete_mission("missing")


def test_finale_has_no_next_mission(tmp_path):
    game = campaign(tmp_path)
    game.complete_mission("one")
    game.complete_mission("two")
    game.complete_mission("three")
    assert game.next_mission("three") is None


def test_rewards_are_available_only_after_completion(tmp_path):
    game = campaign(tmp_path)
    with pytest.raises(RuntimeError, match="not complete"):
        game.rewards_for("one")
    game.complete_mission("one")
    assert game.rewards_for("one") == ("salt_circle",)


def test_ability_rewards_unlock_loadout(tmp_path):
    game = campaign(tmp_path)
    loadout = AbilityLoadout()
    assert not loadout.is_unlocked("salt_circle")
    game.complete_mission("one")
    assert game.grant_rewards("one", loadout) == ("salt_circle",)
    assert loadout.is_unlocked("salt_circle")
