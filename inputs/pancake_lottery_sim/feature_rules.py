
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import numpy as np

from assumptions import FeatureSet


@dataclass
class SegmentRoundStats:
    name: str
    active_players: int
    paid_tickets: int
    free_tickets: int
    paid_revenue: float
    losing_paid_tickets: float
    winning_paid_tickets: float


def apply_ticket_lift(base_paid_tickets: np.ndarray, lift: float, rng: np.random.Generator) -> np.ndarray:
    if lift <= 0:
        return np.zeros_like(base_paid_tickets)
    expected_extra = np.maximum(base_paid_tickets, 0) * lift
    integer = np.floor(expected_extra).astype(int)
    frac = expected_extra - integer
    extra = integer + rng.binomial(1, frac)
    return extra


def free_tickets_from_ratio(paid_tickets: np.ndarray, ratio: float, rng: np.random.Generator) -> np.ndarray:
    if ratio <= 0:
        return np.zeros_like(paid_tickets)
    expected = np.maximum(paid_tickets, 0) * ratio
    integer = np.floor(expected).astype(int)
    frac = expected - integer
    free = integer + rng.binomial(1, frac)
    return free


def spend_subsidy(revenue: np.ndarray, rate: float) -> np.ndarray:
    if rate <= 0:
        return np.zeros_like(revenue, dtype=float)
    return revenue * rate


def fixed_reward_per_active(active_players: np.ndarray, reward: float) -> np.ndarray:
    if reward <= 0:
        return np.zeros_like(active_players, dtype=float)
    return active_players.astype(float) * reward


def loss_rebate(losing_paid_spend: np.ndarray, rate: float) -> np.ndarray:
    if rate <= 0:
        return np.zeros_like(losing_paid_spend, dtype=float)
    return losing_paid_spend * rate


def multiplier_treasury_topup(
    base_paid_prize: np.ndarray,
    paid_ticket_share_of_total: np.ndarray,
    prob: float,
    multiplier_value: float,
) -> np.ndarray:
    if prob <= 0 or multiplier_value <= 1.0:
        return np.zeros_like(base_paid_prize, dtype=float)
    return base_paid_prize * paid_ticket_share_of_total * prob * (multiplier_value - 1.0)


def combine_segment_subsidies(
    feature_set: FeatureSet,
    segment_name: str,
    active_players: np.ndarray,
    paid_revenue: np.ndarray,
    losing_paid_spend: np.ndarray,
    base_paid_prize: np.ndarray,
    paid_ticket_share_of_total: np.ndarray,
) -> Dict[str, np.ndarray]:
    cashback = spend_subsidy(paid_revenue, feature_set.cashback_rate.get(segment_name, 0.0))
    loyalty = spend_subsidy(paid_revenue, feature_set.loyalty_rebate_rate.get(segment_name, 0.0))
    referrals = fixed_reward_per_active(active_players, feature_set.referral_reward_per_active.get(segment_name, 0.0))
    rebates = loss_rebate(losing_paid_spend, feature_set.loss_rebate_rate.get(segment_name, 0.0))
    multiplier = multiplier_treasury_topup(
        base_paid_prize=base_paid_prize,
        paid_ticket_share_of_total=paid_ticket_share_of_total,
        prob=feature_set.multiplier_prob.get(segment_name, 0.0),
        multiplier_value=feature_set.multiplier_value.get(segment_name, 1.0),
    )
    total = cashback + loyalty + referrals + rebates + multiplier
    return {
        "cashback": cashback,
        "loyalty": loyalty,
        "referrals": referrals,
        "loss_rebates": rebates,
        "multiplier_topup": multiplier,
        "total": total,
    }
