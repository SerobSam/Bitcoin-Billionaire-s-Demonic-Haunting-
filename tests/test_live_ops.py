import pytest

from src.live_ops import LiveOpsWallet
from src.runtime import PlayerState


def test_premium_offer_is_pay_to_win_but_capped_and_deterministic():
    wallet = LiveOpsWallet(credits=500)
    player = PlayerState()

    offer = wallet.purchase_offer("infernal_armor")
    wallet.apply_premium_power(player)

    assert offer.name == "Infernal Armor"
    assert wallet.credits == 0
    assert player.max_health == 125
    assert player.health == 125
    assert player.corruption_resistance == 3


def test_premium_purchase_requires_enough_credits():
    wallet = LiveOpsWallet(credits=100)
    with pytest.raises(ValueError, match="Insufficient premium credits"):
        wallet.purchase_offer("genesis_overclock")


def test_content_add_on_unlocks_missions():
    wallet = LiveOpsWallet(credits=900)
    add_on = wallet.purchase_add_on("neon_tokyo")

    assert add_on.name == "Neon Tokyo"
    assert wallet.available_missions() == ("neon_tokyo_blackout", "shibuya_wraith_hunt")
    assert wallet.credits == 0


def test_add_on_cannot_be_purchased_twice():
    wallet = LiveOpsWallet(credits=1800)
    wallet.purchase_add_on("neon_tokyo")
    with pytest.raises(ValueError, match="already owned"):
        wallet.purchase_add_on("neon_tokyo")
