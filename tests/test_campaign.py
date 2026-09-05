import json

import pytest

from src.campaign import Campaign


def campaign(tmp_path):
    path = tmp_path / "campaign.json"
    path.write_text(json.dumps({
        "missions": [
            {"id": "one", "title": "One", "region": "A", "unlock": None, "next": "two"},
            {"id": "two", "title": "Two", "region": "B", "unlock": "one", "next": "three"},
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
