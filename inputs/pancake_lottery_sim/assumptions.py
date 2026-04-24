
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class BulkDiscountConfig:
    enabled: bool = True
    method: str = "pcs_formula"  # pcs_formula | none
    discount_divisor: int = 2000
    max_tickets_per_purchase: int = 100


@dataclass
class SegmentConfig:
    name: str
    population: int
    participation_rate: float
    mean_tickets_when_active: float
    ticket_count_distribution: str = "poisson_shifted"  # poisson_shifted | fixed
    manual_share: float = 0.0
    entropy: float = 1.0  # 1.0 means uniform/random, lower means clustered manual picks.
    demand_multiplier: float = 1.0


@dataclass
class BaselineLotteryConfig:
    digits: int = 6
    digit_base: int = 10
    ticket_price: float = 2.0
    burn_rate: float = 0.20
    bracket_allocations: List[float] = field(
        default_factory=lambda: [0.02, 0.03, 0.05, 0.10, 0.20, 0.40]
    )
    weekly_injection_cycle: List[int] = field(default_factory=lambda: [1, 0, 1, 0, 1, 0, 1])
    injection_amount: float = 8000.0
    burn_applies_to_injections: bool = True
    rollover_mode: str = "global"  # global | same_bracket
    claim_rate: float = 1.0
    bulk_discount: BulkDiscountConfig = field(default_factory=BulkDiscountConfig)

    def validate(self) -> None:
        if self.digits != 6:
            raise ValueError("This implementation currently assumes a 6-digit lottery.")
        total = sum(self.bracket_allocations)
        if abs(total - (1.0 - self.burn_rate)) > 1e-9:
            raise ValueError(
                f"Bracket allocations ({total:.4f}) must sum to 1 - burn_rate ({1.0 - self.burn_rate:.4f})."
            )
        if self.claim_rate <= 0 or self.claim_rate > 1:
            raise ValueError("claim_rate must be within (0, 1].")


@dataclass
class FeatureSet:
    name: str = "baseline"
    segment_ticket_lift: Dict[str, float] = field(default_factory=dict)
    bonus_ticket_ratio: Dict[str, float] = field(default_factory=dict)  # free tickets / paid tickets
    cashback_rate: Dict[str, float] = field(default_factory=dict)  # % of paid spend refunded
    loyalty_rebate_rate: Dict[str, float] = field(default_factory=dict)  # % of paid spend returned
    streak_bonus_ticket_ratio: Dict[str, float] = field(default_factory=dict)  # proxy for streak awards
    referral_reward_per_active: Dict[str, float] = field(default_factory=dict)
    loss_rebate_rate: Dict[str, float] = field(default_factory=dict)  # % of losing paid spend
    multiplier_prob: Dict[str, float] = field(default_factory=dict)  # probability a ticket gets boosted
    multiplier_value: Dict[str, float] = field(default_factory=dict)  # e.g. 2.0 means 2x payout
    jackpot_boost_per_round: float = 0.0  # direct treasury-funded prize add to bracket 6
    applies_to_free_tickets_for_multiplier: bool = False

    def get_lift(self, segment_name: str) -> float:
        return self.segment_ticket_lift.get(segment_name, 0.0)


@dataclass
class SimulationConfig:
    rounds: int = 104
    simulations: int = 2000
    seed: int = 42


@dataclass
class ScenarioConfig:
    name: str
    lottery: BaselineLotteryConfig
    segments: List[SegmentConfig]
    features: FeatureSet = field(default_factory=FeatureSet)
    simulation: SimulationConfig = field(default_factory=SimulationConfig)
