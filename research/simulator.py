"""
Monte Carlo simulator — research tool v1.

Refactored from inputs/pancake_lottery_sim/engine.py.

Key differences from the original:
  - Takes RunConfig (not ScenarioConfig); N is a direct SimParams input.
  - No segment population model; no behavioral feature rules.
  - Two economic branches: TokenBurnEcon and FiatMarginEcon.
  - Pre-allocated numpy arrays; no Python list-of-dicts accumulation.

ASSUMPTION: No segment behavioral overlay in v1.
ASSUMPTION: Ticket picks are uniform (no entropy/clustering model).
ASSUMPTION: Tickets per round ~ n_players + Poisson((mean_tix - 1) × n_players).
ASSUMPTION: Global rollover only in v1; per_bracket mode is a stub.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from constants import BRACKET_PROBS
from model_config import RunConfig, TokenBurnEcon, FiatMarginEcon

_PROBS = np.array(BRACKET_PROBS, dtype=np.float64)  # shape (6,)


def simulate(config: RunConfig) -> pd.DataFrame:
    """Run a Monte Carlo simulation and return one row per (round, simulation).

    Output columns:
        round_index    — 1-indexed round number
        simulation_id  — 0-indexed simulation path
        n_tickets      — total tickets in this round
        revenue        — ticket sales revenue
        injection      — external injection this round (same across all sims)
        burn_or_fee    — burn amount (TokenBurnEcon) or protocol fee (FiatMarginEcon)
        prize_pool     — total prize pool available = fresh_prize + carry_in
        payout         — total paid out to winners this round
        carry_in       — carry entering this round
        carry_out      — carry leaving this round (rolled forward)
        protocol_pnl   — protocol cash position this round
    """
    config.model.validate()

    rng   = np.random.default_rng(config.sim.seed)
    sims  = config.sim.simulations
    rnds  = config.sim.rounds
    model = config.model

    alloc   = np.array(model.bracket_allocations, dtype=np.float64)
    weights = alloc / alloc.sum()  # normalise to "fraction of prize pool"

    # Pre-allocate output arrays
    n_rows = sims * rnds
    col_round      = np.empty(n_rows, dtype=np.int32)
    col_sim        = np.tile(np.arange(sims, dtype=np.int32), rnds)
    col_n_tickets  = np.empty(n_rows, dtype=np.int32)
    col_revenue    = np.empty(n_rows, dtype=np.float64)
    col_injection  = np.empty(n_rows, dtype=np.float64)
    col_burn_fee   = np.empty(n_rows, dtype=np.float64)
    col_prize_pool = np.empty(n_rows, dtype=np.float64)
    col_payout     = np.empty(n_rows, dtype=np.float64)
    col_carry_in   = np.empty(n_rows, dtype=np.float64)
    col_carry_out  = np.empty(n_rows, dtype=np.float64)
    col_pnl        = np.empty(n_rows, dtype=np.float64)
    col_hit_k      = [np.empty(n_rows, dtype=np.int8) for _ in range(6)]

    carry = np.zeros(sims, dtype=np.float64)  # global rollover state

    for r in range(rnds):
        sl = slice(r * sims, (r + 1) * sims)

        # --- Ticket sampling ---
        # ASSUMPTION: total tickets = n_players + Poisson((mean-1)*n_players)
        lam = max(config.sim.mean_tickets_per_player - 1.0, 0.0) * config.sim.n_players
        n_tickets = (
            config.sim.n_players
            + rng.poisson(lam, size=sims).astype(np.int32)
        )

        # --- Revenue ---
        revenue = n_tickets.astype(np.float64) * model.ticket_price

        # --- Injection ---
        flag      = model.inject_schedule[r % len(model.inject_schedule)]
        injection = float(flag) * model.inject_amount  # scalar; same for all sims

        # --- Economic layer ---
        fresh_total = revenue + injection  # shape (sims,)

        if isinstance(model.econ, TokenBurnEcon):
            burn_base   = fresh_total if model.burn_applies_to_injection else revenue
            burn        = model.econ.burn_rate * burn_base
            fresh_prize = fresh_total - burn
            pnl         = np.full(sims, -injection, dtype=np.float64)
            burn_or_fee = burn

        elif isinstance(model.econ, FiatMarginEcon):
            fee         = model.econ.fee_rate * revenue
            fresh_prize = model.econ.prize_pool_fraction * revenue + injection
            pnl         = fee - injection
            burn_or_fee = fee

        else:
            raise TypeError(f"Unknown econ type: {type(model.econ)}")

        # --- Prize pool (post-burn, with carry) ---
        carry_in   = carry.copy()
        prize_pool = fresh_prize + carry_in  # shape (sims,)

        # --- Bracket pools and winner sampling ---
        # bracket_pools[k, sim] = weights[k] * prize_pool[sim]
        bracket_pools = weights[:, None] * prize_pool[None, :]  # shape (6, sims)

        # hit_probs[k, sim] = 1 - (1 - p_k)^n_tickets[sim]
        # ASSUMPTION: uniform i.i.d. tickets → Binomial approximation for hit probability
        hit_probs = 1.0 - np.power(
            1.0 - _PROBS[:, None],
            n_tickets[None, :].astype(np.float64),
        )  # shape (6, sims)

        hits = rng.binomial(1, np.clip(hit_probs, 0.0, 1.0))  # shape (6, sims); Bernoulli

        # --- Payout and carry ---
        payout    = (bracket_pools * hits).sum(axis=0)           # shape (sims,)
        carry_out = (bracket_pools * (1 - hits)).sum(axis=0)     # shape (sims,)
        carry     = carry_out                                     # state update

        # SC-3 invariant: payout + carry_out == prize_pool (within floating-point tolerance)
        # Uncomment during debugging:
        # assert np.allclose(payout + carry_out, prize_pool, rtol=1e-9), "Payout+carry != prize_pool"

        # --- Store ---
        col_round[sl]      = r + 1
        col_n_tickets[sl]  = n_tickets
        col_revenue[sl]    = revenue
        col_injection[sl]  = injection
        col_burn_fee[sl]   = burn_or_fee
        col_prize_pool[sl] = prize_pool
        col_payout[sl]     = payout
        col_carry_in[sl]   = carry_in
        col_carry_out[sl]  = carry_out
        col_pnl[sl]        = pnl
        for k in range(6):
            col_hit_k[k][sl] = hits[k]

    return pd.DataFrame({
        "round_index":    col_round,
        "simulation_id":  col_sim,
        "n_tickets":      col_n_tickets,
        "revenue":        col_revenue,
        "injection":      col_injection,
        "burn_or_fee":    col_burn_fee,
        "prize_pool":     col_prize_pool,
        "payout":         col_payout,
        "carry_in":       col_carry_in,
        "carry_out":      col_carry_out,
        "protocol_pnl":   col_pnl,
        **{f"hit_k{k+1}": col_hit_k[k] for k in range(6)},
    })
