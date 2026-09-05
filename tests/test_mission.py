import pytest

from src.mission import BelAirBlackoutMission, ObjectiveStatus
from src.runtime import Choice


def test_bel_air_objectives_progress_in_order():
    mission = BelAirBlackoutMission()
    assert mission.current_objective.objective_id == "reach_estate"

    mission.reach_estate()
    assert mission.current_objective.objective_id == "scan_terminal"

    digest = mission.scan_terminal()
    assert len(digest) == 64
    assert mission.current_objective.objective_id == "survive_wraith"

    assert mission.survive_wraith(40) is True
    assert mission.current_objective.objective_id == "decode_fragment"

    mission.decode_fragment()
    assert mission.current_objective.objective_id == "make_choice"

    mission.make_choice(Choice.QUARANTINE)
    assert mission.current_objective.objective_id == "extract"

    mission.extract()
    assert mission.complete is True
    assert all(o.status is ObjectiveStatus.COMPLETE for o in mission.objectives)


def test_mission_rejects_out_of_order_actions():
    mission = BelAirBlackoutMission()
    with pytest.raises(RuntimeError):
        mission.scan_terminal()

    mission.reach_estate()
    with pytest.raises(RuntimeError):
        mission.decode_fragment()


def test_corrupted_terminal_requires_genesis_key():
    mission = BelAirBlackoutMission()
    mission.reach_estate()
    mission.scan_terminal()
    mission.survive_wraith(40)

    with pytest.raises(ValueError):
        mission.decode_fragment("wrong-key")

    mission.decode_fragment("genesis")
    assert mission.merkle.completion == 1.0
