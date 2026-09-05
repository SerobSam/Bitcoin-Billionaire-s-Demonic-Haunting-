"""Deterministic premium-store and content-add-on systems for the vertical slice.

This models purchases as an in-game economy only; payment processing is deliberately
outside the game runtime. Premium purchases are intentionally explicit and capped.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class PremiumOffer:
    offer_id: str
    name: str
    price_credits: int
    max_health_bonus: int = 0
    hashrate_bonus: int = 0
    corruption_resistance_bonus: int = 0


@dataclass(frozen=True)
class ContentAddOn:
    add_on_id: str
    name: str
    price_credits: int
    missions: tuple[str, ...]
    description: str


PREMIUM_OFFERS = {
    "infernal_armor": PremiumOffer("infernal_armor", "Infernal Armor", 500, max_health_bonus=25, corruption_resistance_bonus=3),
    "ghost_hashrate": PremiumOffer("ghost_hashrate", "Ghost Hashrate", 750, hashrate_bonus=35),
    "genesis_overclock": PremiumOffer("genesis_overclock", "Genesis Overclock", 1200, max_health_bonus=15, hashrate_bonus=50, corruption_resistance_bonus=2),
}

CONTENT_ADD_ONS = {
    "neon_tokyo": ContentAddOn(
        "neon_tokyo", "Neon Tokyo", 900,
        ("neon_tokyo_blackout", "shibuya_wraith_hunt"),
        "Two cyber-occult missions beneath a citywide crypto blackout.",
    ),
    "hells_datacenter": ContentAddOn(
        "hells_datacenter", "Hell's Datacenter", 1100,
        ("datacenter_descent", "server_cathedral"),
        "A new dungeon chain inside a possessed quantum mining facility.",
    ),
    "genesis_epilogue": ContentAddOn(
        "genesis_epilogue", "Genesis: Aftermath", 650,
        ("aftershock", "zero_day_epilogue"),
        "A post-finale epilogue with new consequences and an alternate extraction.",
    ),
}


@dataclass
class LiveOpsWallet:
    """Tracks premium credits and purchased content without handling real payments."""

    credits: int = 0
    owned_offers: set[str] = field(default_factory=set)
    owned_add_ons: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        if self.credits < 0:
            raise ValueError("credits cannot be negative")

    def grant_credits(self, amount: int) -> None:
        if amount < 0:
            raise ValueError("credit amount cannot be negative")
        self.credits += amount

    def purchase_offer(self, offer_id: str) -> PremiumOffer:
        offer = PREMIUM_OFFERS.get(offer_id)
        if offer is None:
            raise KeyError(f"Unknown premium offer: {offer_id}")
        if offer_id in self.owned_offers:
            raise ValueError("Premium offer is already owned")
        self._spend(offer.price_credits)
        self.owned_offers.add(offer_id)
        return offer

    def purchase_add_on(self, add_on_id: str) -> ContentAddOn:
        add_on = CONTENT_ADD_ONS.get(add_on_id)
        if add_on is None:
            raise KeyError(f"Unknown content add-on: {add_on_id}")
        if add_on_id in self.owned_add_ons:
            raise ValueError("Content add-on is already owned")
        self._spend(add_on.price_credits)
        self.owned_add_ons.add(add_on_id)
        return add_on

    def available_missions(self) -> tuple[str, ...]:
        missions: list[str] = []
        for add_on_id in sorted(self.owned_add_ons):
            missions.extend(CONTENT_ADD_ONS[add_on_id].missions)
        return tuple(missions)

    def apply_premium_power(self, player: object) -> None:
        """Apply every owned power offer to a PlayerState-like object."""
        for offer_id in sorted(self.owned_offers):
            offer = PREMIUM_OFFERS[offer_id]
            player.max_health += offer.max_health_bonus
            player.health = min(player.max_health, player.health + offer.max_health_bonus)
            player.hashrate += offer.hashrate_bonus
            player.corruption_resistance += offer.corruption_resistance_bonus

    def _spend(self, price: int) -> None:
        if self.credits < price:
            raise ValueError("Insufficient premium credits")
        self.credits -= price
