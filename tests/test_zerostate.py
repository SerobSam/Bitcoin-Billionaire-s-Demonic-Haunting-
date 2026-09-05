from src.runtime import Choice
from src.zerostate import ZeroStateRelayMission


def test_zero_state_finale_progression():
    mission = ZeroStateRelayMission()
    mission.reach_relay()
    digest = mission.stabilize_relay()
    assert len(digest) == 64

    while not mission.break_entity(40):
        pass

    mission.decode_genesis()
    mission.make_choice(Choice.QUARANTINE)
    mission.extract()

    assert mission.complete
    assert mission.game.mission == "zero_state_relay"
    assert mission.game.player.hashrate == 80


def test_zero_state_rejects_wrong_genesis_key():
    mission = ZeroStateRelayMission()
    mission.reach_relay()
    mission.stabilize_relay()
    while not mission.break_entity(40):
        pass

    try:
        mission.decode_genesis("wrong-key")
    except ValueError as exc:
        assert "corrupted" in str(exc)
    else:
        raise AssertionError("Expected corrupted genesis signal to reject wrong key")
