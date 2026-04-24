
from __future__ import annotations

from assumptions import BaselineLotteryConfig, FeatureSet, ScenarioConfig, SegmentConfig, SimulationConfig


def default_segments():
    return [
        SegmentConfig(
            name="casual",
            population=22000,
            participation_rate=0.08,
            mean_tickets_when_active=1.3,
            manual_share=0.65,
            entropy=0.92,
        ),
        SegmentConfig(
            name="repeat",
            population=5000,
            participation_rate=0.34,
            mean_tickets_when_active=2.8,
            manual_share=0.45,
            entropy=0.96,
        ),
        SegmentConfig(
            name="whales",
            population=120,
            participation_rate=0.78,
            mean_tickets_when_active=38.0,
            manual_share=0.10,
            entropy=0.995,
        ),
    ]


def baseline_lottery():
    return BaselineLotteryConfig(
        ticket_price=2.0,
        burn_rate=0.20,
        bracket_allocations=[0.02, 0.03, 0.05, 0.10, 0.20, 0.40],
        weekly_injection_cycle=[1, 0, 1, 0, 1, 0, 1],
        injection_amount=8000.0,
        burn_applies_to_injections=True,
        rollover_mode="global",
        claim_rate=1.0,
    )


def simulation_config():
    return SimulationConfig(rounds=104, simulations=2000, seed=42)


def build_scenarios():
    lottery = baseline_lottery()
    segments = default_segments()
    sim = simulation_config()

    scenarios = [
        ScenarioConfig(
            name="baseline",
            lottery=lottery,
            segments=segments,
            features=FeatureSet(name="baseline"),
            simulation=sim,
        ),
        ScenarioConfig(
            name="bonus_tickets_light",
            lottery=lottery,
            segments=segments,
            features=FeatureSet(
                name="bonus_tickets_light",
                segment_ticket_lift={"repeat": 0.08, "casual": 0.02},
                bonus_ticket_ratio={"repeat": 0.04},
                streak_bonus_ticket_ratio={"repeat": 0.01},
            ),
            simulation=sim,
        ),
        ScenarioConfig(
            name="cashback_5pct",
            lottery=lottery,
            segments=segments,
            features=FeatureSet(
                name="cashback_5pct",
                segment_ticket_lift={"casual": 0.03, "repeat": 0.07, "whales": 0.05},
                cashback_rate={"casual": 0.05, "repeat": 0.05, "whales": 0.05},
            ),
            simulation=sim,
        ),
        ScenarioConfig(
            name="loss_rebate_whales_20pct",
            lottery=lottery,
            segments=segments,
            features=FeatureSet(
                name="loss_rebate_whales_20pct",
                segment_ticket_lift={"whales": 0.10, "repeat": 0.02},
                loss_rebate_rate={"whales": 0.20},
            ),
            simulation=sim,
        ),
        ScenarioConfig(
            name="jackpot_boost_2k",
            lottery=lottery,
            segments=segments,
            features=FeatureSet(
                name="jackpot_boost_2k",
                segment_ticket_lift={"casual": 0.01, "repeat": 0.04, "whales": 0.03},
                jackpot_boost_per_round=2000.0,
            ),
            simulation=sim,
        ),
        ScenarioConfig(
            name="loyalty_rebate_2pct",
            lottery=lottery,
            segments=segments,
            features=FeatureSet(
                name="loyalty_rebate_2pct",
                segment_ticket_lift={"repeat": 0.05, "casual": 0.01},
                loyalty_rebate_rate={"repeat": 0.02},
            ),
            simulation=sim,
        ),
        ScenarioConfig(
            name="multiplier_rewards",
            lottery=lottery,
            segments=segments,
            features=FeatureSet(
                name="multiplier_rewards",
                segment_ticket_lift={"casual": 0.02, "repeat": 0.04},
                multiplier_prob={"repeat": 0.10},
                multiplier_value={"repeat": 2.0},
            ),
            simulation=sim,
        ),
    ]
    return scenarios
