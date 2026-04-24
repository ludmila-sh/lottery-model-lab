
from __future__ import annotations

from typing import Dict, List

import numpy as np
import pandas as pd

from assumptions import ScenarioConfig, SegmentConfig
from feature_rules import (
    apply_ticket_lift,
    combine_segment_subsidies,
    free_tickets_from_ratio,
)


EXACT_MATCH_PROBS = np.array([0.09, 0.009, 0.0009, 0.00009, 0.000009, 0.000001], dtype=float)


def pcs_bulk_cost(ticket_price: float, ticket_counts: np.ndarray, discount_divisor: int, max_batch: int) -> np.ndarray:
    counts = np.maximum(ticket_counts.astype(int), 0)
    full_batches = counts // max_batch
    rem = counts % max_batch

    full_batch_cost = ticket_price * max_batch * discount_divisor / (discount_divisor + 1 - max_batch)
    rem_cost = np.where(
        rem > 0,
        ticket_price * rem * discount_divisor / (discount_divisor + 1 - rem),
        0.0,
    )
    return full_batches * full_batch_cost + rem_cost


def sample_paid_tickets(segment: SegmentConfig, simulations: int, rng: np.random.Generator) -> Dict[str, np.ndarray]:
    active = rng.binomial(segment.population, min(max(segment.participation_rate, 0.0), 1.0), size=simulations)
    if segment.ticket_count_distribution == "fixed":
        paid = active * int(round(segment.mean_tickets_when_active))
    elif segment.ticket_count_distribution == "poisson_shifted":
        lam_extra = np.maximum(active.astype(float) * max(segment.mean_tickets_when_active - 1.0, 0.0), 0.0)
        paid = active + rng.poisson(lam_extra)
    else:
        raise ValueError(f"Unsupported ticket_count_distribution={segment.ticket_count_distribution}")
    return {"active_players": active.astype(int), "paid_tickets": paid.astype(int)}


def effective_ticket_counts_by_bracket(total_tickets: np.ndarray, manual_tickets: np.ndarray, entropy: float) -> np.ndarray:
    """
    Exact random selectors are assumed to cover the ticket space uniformly.
    Manual/clustering behavior is approximated by reducing effective unique coverage
    more aggressively for deeper match brackets.
    """
    random_tickets = total_tickets - manual_tickets
    effective = []
    entropy = min(max(entropy, 0.0), 1.0)
    for bracket in range(1, 7):
        factor = entropy ** bracket
        effective.append(random_tickets + manual_tickets * factor)
    return np.vstack(effective)  # shape (6, sims)


def bracket_hit_probabilities(effective_tickets: np.ndarray) -> np.ndarray:
    probs = EXACT_MATCH_PROBS[:, None]
    return 1.0 - np.power(1.0 - probs, effective_tickets)


def simulate_scenario(config: ScenarioConfig) -> pd.DataFrame:
    config.lottery.validate()
    sims = config.simulation.simulations
    rounds = config.simulation.rounds
    rng = np.random.default_rng(config.simulation.seed)

    rel_prize_weights = np.array(config.lottery.bracket_allocations) / sum(config.lottery.bracket_allocations)

    carry_global = np.zeros(sims, dtype=float)
    carry_by_bracket = np.zeros((6, sims), dtype=float)

    results: List[dict] = []

    for round_idx in range(rounds):
        prev_carry = carry_global.copy() if config.lottery.rollover_mode == "global" else carry_by_bracket.sum(axis=0).copy()

        injection_flag = config.lottery.weekly_injection_cycle[round_idx % len(config.lottery.weekly_injection_cycle)]
        baseline_injection = injection_flag * config.lottery.injection_amount
        jackpot_boost = config.features.jackpot_boost_per_round
        external_injection = baseline_injection + jackpot_boost

        total_paid_tickets = np.zeros(sims, dtype=int)
        total_free_tickets = np.zeros(sims, dtype=int)
        total_revenue = np.zeros(sims, dtype=float)
        segment_outputs: Dict[str, Dict[str, np.ndarray]] = {}

        for segment in config.segments:
            sampled = sample_paid_tickets(segment, sims, rng)
            base_paid = sampled["paid_tickets"]
            active = sampled["active_players"]

            lift = max(config.features.get_lift(segment.name), 0.0)
            extra_paid = apply_ticket_lift(base_paid, lift, rng)
            paid = base_paid + extra_paid

            if config.lottery.bulk_discount.enabled and config.lottery.bulk_discount.method == "pcs_formula":
                revenue = pcs_bulk_cost(
                    ticket_price=config.lottery.ticket_price,
                    ticket_counts=paid,
                    discount_divisor=config.lottery.bulk_discount.discount_divisor,
                    max_batch=config.lottery.bulk_discount.max_tickets_per_purchase,
                )
            else:
                revenue = paid.astype(float) * config.lottery.ticket_price

            bonus_ratio = config.features.bonus_ticket_ratio.get(segment.name, 0.0)
            streak_ratio = config.features.streak_bonus_ticket_ratio.get(segment.name, 0.0)
            free = free_tickets_from_ratio(paid, bonus_ratio + streak_ratio, rng)

            manual_tickets = rng.binomial(paid + free, min(max(segment.manual_share, 0.0), 1.0))

            segment_outputs[segment.name] = {
                "active": active,
                "paid": paid,
                "free": free,
                "revenue": revenue,
                "manual": manual_tickets.astype(float),
            }

            total_paid_tickets += paid
            total_free_tickets += free
            total_revenue += revenue

        total_tickets = total_paid_tickets + total_free_tickets
        fresh_pool = total_revenue + external_injection
        burn_base = fresh_pool if config.lottery.burn_applies_to_injections else total_revenue
        burn = config.lottery.burn_rate * burn_base
        spendable_from_fresh = fresh_pool - burn

        if config.lottery.rollover_mode == "global":
            spendable_budget = spendable_from_fresh + carry_global
            bracket_pools = rel_prize_weights[:, None] * spendable_budget[None, :]
        elif config.lottery.rollover_mode == "same_bracket":
            bracket_pools = rel_prize_weights[:, None] * spendable_from_fresh[None, :] + carry_by_bracket
        else:
            raise ValueError("rollover_mode must be 'global' or 'same_bracket'")

        effective_tickets_total = np.zeros((6, sims), dtype=float)

        for segment in config.segments:
            out = segment_outputs[segment.name]
            eff = effective_ticket_counts_by_bracket(
                total_tickets=out["paid"] + out["free"],
                manual_tickets=out["manual"],
                entropy=segment.entropy,
            )
            effective_tickets_total += eff

        hit_probs = bracket_hit_probabilities(effective_tickets_total)
        hits = rng.binomial(1, np.clip(hit_probs, 0.0, 1.0))
        payout_by_bracket = bracket_pools * hits * config.lottery.claim_rate
        payout_from_pool = payout_by_bracket.sum(axis=0)

        if config.lottery.rollover_mode == "global":
            carry_global = (bracket_pools * (1 - hits)).sum(axis=0)
            carry_out = carry_global.copy()
        else:
            carry_by_bracket = bracket_pools * (1 - hits)
            carry_out = carry_by_bracket.sum(axis=0)

        treasury_feature_cost = np.zeros(sims, dtype=float)
        feature_cash_cost = np.zeros(sims, dtype=float)
        gross_player_value = payout_from_pool.copy()

        paid_ticket_share_of_total = np.divide(
            total_paid_tickets,
            np.maximum(total_tickets, 1),
            out=np.zeros_like(total_paid_tickets, dtype=float),
            where=total_tickets > 0,
        )

        for segment in config.segments:
            out = segment_outputs[segment.name]
            seg_paid_share = np.divide(
                out["paid"],
                np.maximum(total_paid_tickets, 1),
                out=np.zeros_like(out["paid"], dtype=float),
                where=total_paid_tickets > 0,
            )
            seg_base_paid_prize = payout_from_pool * seg_paid_share * paid_ticket_share_of_total

            # For loss rebates, the baseline ticket-level winning probability is 10%.
            losing_paid_spend = out["revenue"] * 0.90

            subsidies = combine_segment_subsidies(
                feature_set=config.features,
                segment_name=segment.name,
                active_players=out["active"],
                paid_revenue=out["revenue"],
                losing_paid_spend=losing_paid_spend,
                base_paid_prize=seg_base_paid_prize,
                paid_ticket_share_of_total=paid_ticket_share_of_total,
            )
            seg_cost = subsidies["total"]
            treasury_feature_cost += seg_cost
            feature_cash_cost += seg_cost
            gross_player_value += seg_cost

        incremental_unit_margin_ex_burn = total_revenue - (baseline_injection + jackpot_boost + feature_cash_cost)

        for sim_id in range(sims):
            results.append(
                {
                    "round_index": round_idx + 1,
                    "simulation_id": sim_id,
                    "total_paid_tickets": int(total_paid_tickets[sim_id]),
                    "total_free_tickets": int(total_free_tickets[sim_id]),
                    "total_tickets": int(total_tickets[sim_id]),
                    "player_revenue": float(total_revenue[sim_id]),
                    "injection": float(external_injection),
                    "treasury_feature_cost": float(treasury_feature_cost[sim_id] + baseline_injection + jackpot_boost),
                    "feature_cash_cost": float(feature_cash_cost[sim_id]),
                    "burn": float(burn[sim_id]),
                    "payout_from_pool": float(payout_from_pool[sim_id]),
                    "carry_in": float(prev_carry[sim_id]),
                    "carry_out": float(carry_out[sim_id]),
                    "gross_player_value": float(gross_player_value[sim_id]),
                    "incremental_unit_margin_ex_burn": float(incremental_unit_margin_ex_burn[sim_id]),
                }
            )

    return pd.DataFrame(results)
