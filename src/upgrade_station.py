"""In-world upgrade station rules for Genesis Protocol."""
from __future__ import annotations

from dataclasses import dataclass

from .profile import CampaignProfile


@dataclass(frozen=True)
class UpgradeOption:
    upgrade_id: str
    name: str
    description: str


UPGRADE_OPTIONS = (
    UpgradeOption("max_health", "Hardened Frame", "+10 maximum health per point."),
    UpgradeOption("hashrate", "Hotter Hash", "+5 hashrate per point."),
    UpgradeOption("corruption_resistance", "Salted Core", "Reduce corruption gain by 1 per point."),
)


class UpgradeStation:
    """Spend level-up points at a safe-node upgrade station."""

    def __init__(self, profile: CampaignProfile) -> None:
        self.profile = profile

    @property
    def available_points(self) -> int:
        return self.profile.progression.upgrade_points

    def options(self) -> tuple[UpgradeOption, ...]:
        return UPGRADE_OPTIONS

    def purchase(self, upgrade_id: str) -> UpgradeOption:
        option = next((item for item in UPGRADE_OPTIONS if item.upgrade_id == upgrade_id), None)
        if option is None:
            raise KeyError(f"Unknown upgrade: {upgrade_id}")
        self.profile.upgrades.spend(self.profile.progression, upgrade_id)
        self.profile.apply_upgrades()
        return option
