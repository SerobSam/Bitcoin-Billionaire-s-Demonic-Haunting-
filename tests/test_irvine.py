from src.irvine import IrvineConsensusMission
from src.runtime import Choice


def test_irvine_consensus_progression():
    mission = IrvineConsensusMission()

    mission.enter_suburbs()
    mission.trace_consensus()
    while not mission.break_vanguard(25):
        pass
    mission.decode_vote()
    mission.make_choice(Choice.QUARANTINE)
    mission.extract()

    assert mission.complete
    assert mission.game.mission == "irvine_consensus"
    assert mission.game.player.choices == ["quarantine"]
    assert "corrupted_fragment" in mission.game.player.inventory


def test_irvine_consensus_rejects_out_of_order_objective():
    mission = IrvineConsensusMission()

    try:
        mission.decode_vote()
    except RuntimeError as error:
        assert "not ready" in str(error)
    else:
        raise AssertionError("Expected decode to reject out-of-order progression")
