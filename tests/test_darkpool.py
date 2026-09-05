from src.darkpool import DarkPoolDescentMission
from src.runtime import Choice


def test_dark_pool_progresses_to_completion():
    mission = DarkPoolDescentMission()
    mission.enter_dungeons()
    digest = mission.find_choir()
    assert len(digest) == 64

    while not mission.break_warden(30):
        pass

    assert mission.game.player.inventory["corrupted_fragment"] == 1
    mission.decode_liturgy()
    mission.make_choice(Choice.QUARANTINE)
    mission.extract()

    assert mission.complete
    assert mission.game.phase == "complete"
    assert mission.game.player.choices[-1] == Choice.QUARANTINE.value


def test_dark_pool_rejects_out_of_order_actions():
    mission = DarkPoolDescentMission()

    try:
        mission.decode_liturgy()
    except RuntimeError as exc:
        assert "not ready" in str(exc)
    else:
        raise AssertionError("Expected decode_liturgy to reject the locked objective")
