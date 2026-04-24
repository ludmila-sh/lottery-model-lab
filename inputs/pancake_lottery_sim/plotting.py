
from __future__ import annotations

from pathlib import Path
from typing import Dict

import matplotlib.pyplot as plt
import pandas as pd


def plot_cumulative_mean_margin(paths: Dict[str, pd.DataFrame], output_path: Path) -> None:
    plt.figure(figsize=(10, 6))
    for name, df in paths.items():
        curve = (
            df.groupby(["round_index", "simulation_id"])["incremental_unit_margin_ex_burn"]
            .sum()
            .groupby("round_index")
            .mean()
            .cumsum()
        )
        plt.plot(curve.index, curve.values, label=name)
    plt.axhline(0.0, linewidth=1)
    plt.xlabel("Round")
    plt.ylabel("Cumulative unit margin ex burn")
    plt.title("Mean cumulative unit margin by scenario")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()


def plot_summary_bars(summary_df: pd.DataFrame, output_path: Path) -> None:
    plt.figure(figsize=(10, 6))
    ordered = summary_df.sort_values("incremental_margin_ex_burn_vs_baseline")
    plt.bar(ordered["scenario"], ordered["incremental_margin_ex_burn_vs_baseline"])
    plt.axhline(0.0, linewidth=1)
    plt.xticks(rotation=20, ha="right")
    plt.ylabel("Incremental margin ex burn vs baseline / round")
    plt.title("Feature economics versus baseline")
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()


def plot_tail_risk(summary_df: pd.DataFrame, output_path: Path) -> None:
    plt.figure(figsize=(10, 6))
    ordered = summary_df[summary_df["scenario"] != "baseline"].sort_values("p1_cumulative_incremental_margin_ex_burn_vs_baseline")
    plt.bar(ordered["scenario"], ordered["p1_cumulative_incremental_margin_ex_burn_vs_baseline"])
    plt.xticks(rotation=20, ha="right")
    plt.ylabel("1st percentile cumulative margin ex burn")
    plt.title("Tail downside after full horizon")
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()


def plot_validation(validation_df: pd.DataFrame, output_path: Path) -> None:
    plt.figure(figsize=(10, 6))
    x = validation_df["bracket"]
    plt.plot(x, validation_df["expected"], marker="o", label="Expected")
    plt.plot(x, validation_df["observed"], marker="o", label="Observed")
    plt.yscale("log")
    plt.xlabel("Bracket")
    plt.ylabel("Probability (log scale)")
    plt.title("Theoretical vs observed exact-match probabilities")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()
