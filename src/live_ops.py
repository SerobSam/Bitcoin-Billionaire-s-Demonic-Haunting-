"""Deterministic premium, season, event, and content-add-on systems."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta


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
    "neon_tokyo": ContentAddOn("neon_tokyo", "Neon Tokyo", 900, ("neon_tokyo_blackout", "shibuya_wraith_hunt"), "Two cyber-occult missions beneath a citywide crypto blackout."),
    "hells_datacenter": ContentAddOn("hells_datacenter", "Hell's Datacenter", 1100, ("datacenter_descent", "server_cathedral"), "A dungeon chain inside a possessed quantum mining facility."),
    "genesis_epilogue": ContentAddOn("genesis_epilogue", "Genesis: Aftermath", 650, ("aftershock", "zero_day_epilogue"), "A post-finale epilogue with new consequences and an alternate extraction."),
}


@dataclass(frozen=True)
class DLCMission:
    mission_id: str
    add_on_id: str
    title: str
    enemy_name: str
    enemy_health: int
    enemy_damage: int
    corruption_on_hit: int
    investigation_xp: int
    completion_xp: int
    evidence_reward: int
    loot_item: str


DLC_MISSIONS = {
    "neon_tokyo_blackout": DLCMission("neon_tokyo_blackout", "neon_tokyo", "Neon Tokyo Blackout", "Chrome Oni", 45, 11, 6, 35, 120, 2, "neon_shard"),
    "shibuya_wraith_hunt": DLCMission("shibuya_wraith_hunt", "neon_tokyo", "Shibuya Wraith Hunt", "Shibuya Wraith", 55, 13, 8, 40, 140, 3, "wraith_mask"),
    "datacenter_descent": DLCMission("datacenter_descent", "hells_datacenter", "Datacenter Descent", "Firewall Revenant", 65, 15, 10, 45, 160, 3, "infernal_hash"),
    "server_cathedral": DLCMission("server_cathedral", "hells_datacenter", "Server Cathedral", "Cathedral Process", 75, 17, 12, 50, 180, 4, "cathedral_key"),
    "aftershock": DLCMission("aftershock", "genesis_epilogue", "Aftershock", "Genesis Echo", 85, 18, 13, 55, 200, 4, "genesis_echo"),
    "zero_day_epilogue": DLCMission("zero_day_epilogue", "genesis_epilogue", "Zero-Day Epilogue", "Zero-Day Seraph", 95, 20, 15, 60, 240, 5, "zero_day_relic"),
}


@dataclass(frozen=True)
class SeasonReward:
    tier: int
    free_item: str | None = None
    premium_item: str | None = None


@dataclass(frozen=True)
class LiveEvent:
    event_id: str
    name: str
    description: str
    xp_multiplier: float
    reward_item: str


SEASON_REWARDS = tuple(
    SeasonReward(i, free_item=f"season_cache_{i}", premium_item=f"premium_cache_{i}")
    for i in range(1, 11)
)

ROTATING_EVENTS = (
    LiveEvent("blood_moon", "Blood Moon Protocol", "Corruption surges through every hostile node.", 1.5, "blood_moon_cache"),
    LiveEvent("hash_rush", "Hash Rush", "Mining anomalies amplify progression rewards.", 2.0, "hash_rush_cache"),
    LiveEvent("ghost_signal", "Ghost Signal", "Spectral traffic reveals rare encrypted loot.", 1.25, "ghost_signal_cache"),
)


@dataclass
class SeasonPass:
    """A deterministic ten-tier free/premium reward track."""

    season_id: str = "genesis-season-1"
    xp: int = 0
    premium_unlocked: bool = False
    claimed_free: set[int] = field(default_factory=set)
    claimed_premium: set[int] = field(default_factory=set)

    XP_PER_TIER = 250

    @property
    def tier(self) -> int:
        return min(len(SEASON_REWARDS), self.xp // self.XP_PER_TIER + 1)

    @property
    def maxed(self) -> bool:
        return self.xp >= len(SEASON_REWARDS) * self.XP_PER_TIER

    def add_xp(self, amount: int, multiplier: float = 1.0) -> int:
        if amount < 0 or multiplier < 0:
            raise ValueError("season XP and multiplier must be non-negative")
        self.xp = min(len(SEASON_REWARDS) * self.XP_PER_TIER, self.xp + int(amount * multiplier))
        return self.tier

    def unlock_premium(self) -> None:
        self.premium_unlocked = True

    def claim(self, tier: int, premium: bool = False) -> str:
        if tier < 1 or tier > len(SEASON_REWARDS):
            raise ValueError("Invalid season tier")
        if self.xp < tier * self.XP_PER_TIER:
            raise ValueError("Season tier is not unlocked")
        claimed = self.claimed_premium if premium else self.claimed_free
        if tier in claimed:
            raise ValueError("Season reward is already claimed")
        if premium and not self.premium_unlocked:
            raise ValueError("Premium reward track is locked")
        reward = SEASON_REWARDS[tier - 1]
        item = reward.premium_item if premium else reward.free_item
        claimed.add(tier)
        assert item is not None
        return item

    def to_dict(self) -> dict[str, object]:
        return {"season_id": self.season_id, "xp": self.xp, "premium_unlocked": self.premium_unlocked, "claimed_free": sorted(self.claimed_free), "claimed_premium": sorted(self.claimed_premium)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "SeasonPass":
        return cls(
            season_id=str(data.get("season_id", "genesis-season-1")),
            xp=int(data.get("xp", 0)),
            premium_unlocked=bool(data.get("premium_unlocked", False)),
            claimed_free={int(value) for value in data.get("claimed_free", [])},
            claimed_premium={int(value) for value in data.get("claimed_premium", [])},
        )


class RotatingEventSchedule:
    """Selects the same event for every client on the same UTC date."""

    def __init__(self, anchor: date = date(2026, 1, 1)) -> None:
        self.anchor = anchor

    def event_for(self, when: date) -> LiveEvent:
        offset = (when - self.anchor).days
        return ROTATING_EVENTS[offset % len(ROTATING_EVENTS)]

    def window(self, when: date) -> tuple[date, date]:
        start = when - timedelta(days=when.weekday())
        return start, start + timedelta(days=6)


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

    def owns_mission(self, mission_id: str) -> bool:
        mission = DLC_MISSIONS.get(mission_id)
        return mission is not None and mission.add_on_id in self.owned_add_ons

    def available_missions(self) -> tuple[str, ...]:
        missions: list[str] = []
        for add_on_id in sorted(self.owned_add_ons):
            missions.extend(CONTENT_ADD_ONS[add_on_id].missions)
        return tuple(missions)

    def apply_premium_power(self, player: object) -> None:
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
