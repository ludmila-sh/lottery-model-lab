
from __future__ import annotations

from typing import Dict

import numpy as np
import pandas as pd

from engine import EXACT_MATCH_PROBS


def exact_match_probabilities() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "bracket": [1, 2, 3, 4, 5, 6],
            "probability_exact_match": EXACT_MATCH_PROBS,
            "formula": [
                "0.9 / 10",
                "0.9 / 10^2",
                "0.9 / 10^3",
                "0.9 / 10^4",
                "0.9 / 10^5",
                "1 / 10^6",
            ],
        }
    )


def theoretical_bracket_hit_probabilities(ticket_count: float) -> pd.DataFrame:
    hit = 1.0 - np.power(1.0 - EXACT_MATCH_PROBS, ticket_count)
    return pd.DataFrame({"bracket": [1, 2, 3, 4, 5, 6], "ticket_count": ticket_count, "prob_any_winner": hit})


def validate_random_ticket_frequencies(samples: int = 2_000_000, seed: int = 123) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    winning = rng.integers(0, 10, size=(samples, 6))
    tickets = rng.integers(0, 10, size=(samples, 6))
    matches = (winning == tickets)
    exact = np.zeros(samples, dtype=int)
    for i in range(samples):
        if matches[i, 0] == 0:
            exact[i] = 0
        else:
            k = 1
            while k < 6 and matches[i, k] == 1:
                k += 1
            exact[i] = k
    observed = np.array([(exact == k).mean() for k in range(1, 7)])
    expected = EXACT_MATCH_PROBS
    return pd.DataFrame(
        {
            "bracket": [1, 2, 3, 4, 5, 6],
            "expected": expected,
            "observed": observed,
            "abs_error": np.abs(observed - expected),
        }
    )


def summarize_scenario(df: pd.DataFrame, scenario_name: str) -> pd.DataFrame:
    by_sim = (
        df.groupby("simulation_id")
        .agg(
            total_revenue=("player_revenue", "sum"),
            total_burn=("burn", "sum"),
            total_injection=("injection", "sum"),
            total_treasury_feature_cost=("treasury_feature_cost", "sum"),
            total_feature_cash_cost=("feature_cash_cost", "sum"),
            total_payout=("payout_from_pool", "sum"),
            final_carry=("carry_out", "last"),
            avg_paid_tickets=("total_paid_tickets", "mean"),
            avg_free_tickets=("total_free_tickets", "mean"),
            avg_revenue_per_round=("player_revenue", "mean"),
            avg_payout_per_round=("payout_from_pool", "mean"),
            avg_burn_per_round=("burn", "mean"),
            avg_treasury_cost_per_round=("treasury_feature_cost", "mean"),
            avg_gross_player_value_per_round=("gross_player_value", "mean"),
            cumulative_margin_ex_burn=("incremental_unit_margin_ex_burn", "sum"),
        )
        .reset_index()
    )

    metrics = {
        "scenario": scenario_name,
        "avg_paid_tickets_per_round": by_sim["avg_paid_tickets"].mean(),
        "avg_free_tickets_per_round": by_sim["avg_free_tickets"].mean(),
        "avg_revenue_per_round": by_sim["avg_revenue_per_round"].mean(),
        "avg_payout_per_round": by_sim["avg_payout_per_round"].mean(),
        "avg_burn_per_round": by_sim["avg_burn_per_round"].mean(),
        "avg_treasury_cost_per_round": by_sim["avg_treasury_cost_per_round"].mean(),
        "avg_gross_player_value_per_round": by_sim["avg_gross_player_value_per_round"].mean(),
        "mean_final_carry": by_sim["final_carry"].mean(),
        "std_final_carry": by_sim["final_carry"].std(ddof=1),
    }
    return pd.DataFrame([metrics])


def compare_to_baseline(summaries: Dict[str, pd.DataFrame], baseline_name: str) -> pd.DataFrame:
    baseline = summaries[baseline_name].iloc[0]
    rows = []
    for name, df in summaries.items():
        row = df.iloc[0].copy()
        row["delta_revenue_per_round_vs_baseline"] = row["avg_revenue_per_round"] - baseline["avg_revenue_per_round"]
        row["delta_treasury_cost_per_round_vs_baseline"] = row["avg_treasury_cost_per_round"] - baseline["avg_treasury_cost_per_round"]
        row["delta_burn_per_round_vs_baseline"] = row["avg_burn_per_round"] - baseline["avg_burn_per_round"]
        row["delta_paid_tickets_per_round_vs_baseline"] = row["avg_paid_tickets_per_round"] - baseline["avg_paid_tickets_per_round"]
        row["incremental_margin_ex_burn_vs_baseline"] = (
            row["delta_revenue_per_round_vs_baseline"] - row["delta_treasury_cost_per_round_vs_baseline"]
        )
        row["incremental_margin_including_burn_vs_baseline"] = (
            row["delta_revenue_per_round_vs_baseline"]
            + row["delta_burn_per_round_vs_baseline"]
            - row["delta_treasury_cost_per_round_vs_baseline"]
        )
        rows.append(row)
    return pd.DataFrame(rows)


def attach_path_delta_metrics(summary_df: pd.DataFrame, path_results: Dict[str, pd.DataFrame], baseline_name: str) -> pd.DataFrame:
    baseline = (
        path_results[baseline_name]
        .groupby("simulation_id")
        .agg(
            cumulative_revenue=("player_revenue", "sum"),
            cumulative_treasury_cost=("treasury_feature_cost", "sum"),
            cumulative_burn=("burn", "sum"),
            cumulative_margin_ex_burn=("incremental_unit_margin_ex_burn", "sum"),
        )
        .reset_index()
    )

    out = summary_df.copy()
    p1s = []
    p5s = []
    worsts = []
    pneg = []

    for _, row in out.iterrows():
        if row["scenario"] == baseline_name:
            deltas = np.zeros(len(baseline), dtype=float)
        else:
            cur = (
                path_results[row["scenario"]]
                .groupby("simulation_id")
                .agg(
                    cumulative_margin_ex_burn=("incremental_unit_margin_ex_burn", "sum"),
                )
                .reset_index()
            )
            merged = baseline.merge(cur, on="simulation_id", suffixes=("_base", "_cur"))
            deltas = merged["cumulative_margin_ex_burn_cur"] - merged["cumulative_margin_ex_burn_base"]
        p1s.append(np.quantile(deltas, 0.01))
        p5s.append(np.quantile(deltas, 0.05))
        worsts.append(np.min(deltas))
        pneg.append(np.mean(deltas < 0))

    out["p1_cumulative_incremental_margin_ex_burn_vs_baseline"] = p1s
    out["p5_cumulative_incremental_margin_ex_burn_vs_baseline"] = p5s
    out["worst_cumulative_incremental_margin_ex_burn_vs_baseline"] = worsts
    out["prob_negative_unit_margin_ex_burn"] = pneg
    return out


def classify_safety(row: pd.Series) -> str:
    margin = row["incremental_margin_ex_burn_vs_baseline"]
    pneg = row["prob_negative_unit_margin_ex_burn"]
    if row["scenario"] == "baseline":
        return "baseline"
    if margin > 0 and pneg < 0.25:
        return "safe"
    if margin > -0.02 * max(row["avg_revenue_per_round"], 1.0) and pneg < 0.75:
        return "risky / parameter-sensitive"
    return "structurally loss-making"


def add_safety_labels(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["safety_label"] = out.apply(classify_safety, axis=1)
    return out
