"""
Aggregate metrics computed from a simulate() output DataFrame.

All monetary values are in [price_units] — the unit of ticket_price in the ModelConfig.
ticket_price is OPEN (no confirmed source). Interpret monetary metrics accordingly.

Usage:
    from metrics import compute_metrics
    df = simulate(config)
    m  = compute_metrics(df, config)
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from model_config import RunConfig
from constants import p_bracket_pays


def compute_metrics(df: pd.DataFrame, config: RunConfig) -> dict:
    """Return a flat dict of aggregate metrics over all simulations.

    Carry metrics
    -------------
    carry_ratio_mean        mean(carry_out / revenue) per round, averaged over sims
    carry_ratio_p50         median carry-to-revenue ratio
    carry_ratio_p95         95th-percentile carry-to-revenue ratio
    p_carry_gt_10x_rev      fraction of (round, sim) pairs where carry_out > 10× revenue

    Bracket hit rates  (per round, averaged across sims)
    ---------------------------------------------------
    hit_rate_k{1..6}        empirical P(bracket k pays in a given round)
    hit_rate_k{1..6}_theo   theoretical P(bracket k pays), using mean n_tickets

    Payout metrics
    --------------
    payout_mean             mean total payout per round [price_units]
    payout_cv               coefficient of variation of payout across all (round, sim) pairs
    payout_fraction_mean    mean(payout / prize_pool) — fraction of pool paid out each round

    PnL metrics (FiatMarginEcon only; NaN for TokenBurnEcon)
    --------------------------------------------------------
    protocol_pnl_mean       mean protocol PnL per round [price_units]
    protocol_pnl_cumulative mean cumulative PnL at end of last round

    Jackpot (bracket 6) metrics
    ---------------------------
    jackpot_carry_mean      mean carry_out attributable to bracket 6 (approximated)
    p_jackpot_hits_by_T     fraction of simulations where bracket 6 hit at least once
    """
    sims  = config.sim.simulations
    rnds  = config.sim.rounds
    model = config.model

    import model_config as mc
    is_fiat = isinstance(model.econ, mc.FiatMarginEcon)

    # --- Carry metrics ---
    ratio = df["carry_out"] / df["revenue"].replace(0, np.nan)
    carry_ratio_mean  = float(ratio.mean())
    carry_ratio_p50   = float(ratio.quantile(0.50))
    carry_ratio_p95   = float(ratio.quantile(0.95))
    p_carry_gt_10x    = float((df["carry_out"] > 10.0 * df["revenue"]).mean())

    # --- Bracket hit rates ---
    mean_n = float(df["n_tickets"].mean())
    hit_rates_emp  = {}
    hit_rates_theo = {}
    for k in range(1, 7):
        col = f"hit_k{k}"
        hit_rates_emp[f"hit_rate_k{k}"]      = float(df[col].mean())
        hit_rates_theo[f"hit_rate_k{k}_theo"] = p_bracket_pays(k, mean_n)

    # --- Payout metrics ---
    payout_mean     = float(df["payout"].mean())
    payout_cv       = float(df["payout"].std() / df["payout"].mean()) if df["payout"].mean() != 0 else float("nan")
    payout_fraction = float((df["payout"] / df["prize_pool"].replace(0, np.nan)).mean())

    # --- PnL metrics ---
    if is_fiat:
        protocol_pnl_mean = float(df["protocol_pnl"].mean())
        # Sum PnL per simulation path, then average
        cum_pnl = df.groupby("simulation_id")["protocol_pnl"].sum()
        protocol_pnl_cum  = float(cum_pnl.mean())
    else:
        protocol_pnl_mean = float("nan")
        protocol_pnl_cum  = float("nan")

    # --- Jackpot (bracket 6) metrics ---
    # Approximate jackpot carry = hit_k6==0 fraction × bracket-6 pool share
    alloc  = np.array(model.bracket_allocations, dtype=np.float64)
    w6     = alloc[-1] / alloc.sum()  # bracket-6 weight of prize pool
    jackpot_carry_mean = float(
        ((1 - df["hit_k6"]) * w6 * df["prize_pool"]).mean()
    )
    # P(at least one jackpot hit per sim)
    jackpot_hits_per_sim = df.groupby("simulation_id")["hit_k6"].sum()
    p_jackpot_hits_by_T  = float((jackpot_hits_per_sim > 0).mean())

    return {
        # carry
        "carry_ratio_mean":     carry_ratio_mean,
        "carry_ratio_p50":      carry_ratio_p50,
        "carry_ratio_p95":      carry_ratio_p95,
        "p_carry_gt_10x_rev":   p_carry_gt_10x,
        # bracket hit rates
        **hit_rates_emp,
        **hit_rates_theo,
        # payout
        "payout_mean":          payout_mean,
        "payout_cv":            payout_cv,
        "payout_fraction_mean": payout_fraction,
        # pnl
        "protocol_pnl_mean":    protocol_pnl_mean,
        "protocol_pnl_cumulative": protocol_pnl_cum,
        # jackpot
        "jackpot_carry_mean":   jackpot_carry_mean,
        "p_jackpot_hits_by_T":  p_jackpot_hits_by_T,
    }
