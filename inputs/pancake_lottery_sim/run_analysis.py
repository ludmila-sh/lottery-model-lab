
from __future__ import annotations

from pathlib import Path

import pandas as pd

from analytics import (
    add_safety_labels,
    compare_to_baseline,
    exact_match_probabilities,
    summarize_scenario,
    theoretical_bracket_hit_probabilities,
    validate_random_ticket_frequencies,
)
from engine import simulate_scenario
from plotting import plot_cumulative_mean_margin, plot_summary_bars, plot_tail_risk, plot_validation
from scenarios import build_scenarios


def main(output_dir: str = "outputs") -> None:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    scenarios = build_scenarios()
    path_results = {}
    summaries = {}
    round_means = []

    for scenario in scenarios:
        df = simulate_scenario(scenario)
        path_results[scenario.name] = df
        summaries[scenario.name] = summarize_scenario(df, scenario.name)
        round_mean = df.groupby("round_index").agg(
            mean_revenue=("player_revenue", "mean"),
            mean_payout=("payout_from_pool", "mean"),
            mean_burn=("burn", "mean"),
            mean_treasury_cost=("treasury_feature_cost", "mean"),
            mean_carry=("carry_out", "mean"),
            mean_margin_ex_burn=("incremental_unit_margin_ex_burn", "mean"),
        ).reset_index()
        round_mean["scenario"] = scenario.name
        round_means.append(round_mean)

    summary_df = compare_to_baseline(summaries, baseline_name="baseline")
    from analytics import attach_path_delta_metrics
    summary_df = attach_path_delta_metrics(summary_df, path_results, baseline_name="baseline")
    summary_df = add_safety_labels(summary_df)
    summary_df.to_csv(out / "scenario_summary.csv", index=False)

    pd.concat(round_means, ignore_index=True).to_csv(out / "scenario_round_means.csv", index=False)

    validation_df = validate_random_ticket_frequencies(samples=1_000_000)
    validation_df.to_csv(out / "validation_exact_match_frequencies.csv", index=False)

    exact_match_probabilities().to_csv(out / "theoretical_exact_match_probabilities.csv", index=False)
    theoretical_bracket_hit_probabilities(ticket_count=10000).to_csv(out / "theoretical_hit_probabilities_10k_tickets.csv", index=False)

    plot_cumulative_mean_margin(path_results, out / "cumulative_mean_margin.png")
    plot_summary_bars(summary_df, out / "scenario_margin_bars.png")
    plot_tail_risk(summary_df, out / "scenario_tail_risk.png")
    plot_validation(validation_df, out / "validation_exact_match.png")

    top_cols = [
        "scenario",
        "avg_paid_tickets_per_round",
        "avg_free_tickets_per_round",
        "avg_revenue_per_round",
        "avg_payout_per_round",
        "avg_burn_per_round",
        "avg_treasury_cost_per_round",
        "incremental_margin_ex_burn_vs_baseline",
        "incremental_margin_including_burn_vs_baseline",
        "prob_negative_unit_margin_ex_burn",
        "safety_label",
    ]
    md = ["# Scenario comparison", "", summary_df[top_cols].round(4).to_markdown(index=False), ""]
    (out / "scenario_comparison.md").write_text("\n".join(md), encoding="utf-8")


if __name__ == "__main__":
    main()
