"""
Tier 2/3 — Model configuration dataclasses.

Tier 2 (Fixed):   econ_class, rollover_mode, matching_direction — model-class choices.
Tier 3 (Tunable): n_players, bracket_allocations, inject_amount, burn_rate — swept in scenarios.

Labels used throughout:
  CONFIRMED  — verified against primary source SRC-013 (Round 1949, Apr 2026)
  ASSUMPTION — modeling choice; not yet verified against official PancakeSwap docs
  OPEN       — not yet decided by the team; Baseline B cannot be instantiated

AC-2 (prize pool consistency) runs inside ModelConfig.validate().
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


# ---------------------------------------------------------------------------
# Economic layer — branches at the fee/burn split
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TokenBurnEcon:
    """Baseline A economic layer.

    The protocol destroys burn_rate of the pool each round as a token sink.
    Protocol retains zero cash from ticket sales.
    Source: docs/problem_statement_math.md §3.2 Model A
    """
    burn_rate: float  # CONFIRMED: 0.20 from SRC-013

    @property
    def prize_pool_fraction(self) -> float:
        return 1.0 - self.burn_rate

    def validate(self) -> None:
        assert 0.0 < self.burn_rate < 1.0, (
            f"burn_rate must be in (0, 1); got {self.burn_rate}"
        )


@dataclass(frozen=True)
class FiatMarginEcon:
    """Baseline B economic layer (stablecoin variant).

    The protocol retains fee_rate of ticket revenue as cash.
    No burn mechanic. Reserve and referral are additional deductions.
    Source: docs/problem_statement_math.md §3.2 Model B
    OPEN: All values below are per SRC-018; none are confirmed by team decision.
    """
    fee_rate:      float  # OPEN: 0.15 per SRC-018
    reserve_rate:  float  # OPEN: 0.05 per SRC-018
    referral_rate: float  # OPEN: 0.10 when referral active; use 0.0 as default

    @property
    def prize_pool_fraction(self) -> float:
        return 1.0 - self.fee_rate - self.reserve_rate - self.referral_rate

    def validate(self) -> None:
        total = self.fee_rate + self.reserve_rate + self.referral_rate
        assert 0.0 < total < 1.0, (
            f"Total deductions must be in (0, 1); got {total:.4f}"
        )
        assert self.prize_pool_fraction > 0.0, (
            f"prize_pool_fraction must be positive; got {self.prize_pool_fraction:.4f}"
        )


EconConfig = TokenBurnEcon | FiatMarginEcon


# ---------------------------------------------------------------------------
# Model configuration — fixed choices for a given model run
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ModelConfig:
    """Complete lottery model specification.

    bracket_allocations: fractions of TOTAL pool (revenue + injection) going to each bracket.
    They must sum to prize_pool_fraction (= 1 - burn_rate for TokenBurnEcon).
    Example: PCS [0.02, ..., 0.40] sum to 0.80; burn gets the remaining 0.20.

    Internally, the simulator normalizes these to "fractions of prize pool" by dividing
    by their sum. This matches the approach in inputs/pancake_lottery_sim/engine.py.
    """
    name:                     str
    econ:                     EconConfig
    bracket_allocations:      tuple[float, ...]  # 6 values summing to prize_pool_fraction
    rollover_mode:            Literal["global", "per_bracket"]
    matching_direction:       Literal["L", "R"]
    inject_amount:            float
    inject_schedule:          tuple[int, ...]    # binary flags per round in repeating cycle
    burn_applies_to_injection: bool
    ticket_price:             float

    def validate(self) -> None:
        self.econ.validate()

        # AC-2 — prize pool consistency
        alloc_sum = sum(self.bracket_allocations)
        ppf = self.econ.prize_pool_fraction
        assert abs(alloc_sum - ppf) < 1e-9, (
            f"AC-2 FAIL: bracket_allocations sum {alloc_sum:.6f} != "
            f"prize_pool_fraction {ppf:.6f} for {self.name!r}"
        )
        assert len(self.bracket_allocations) == 6, (
            f"Must have exactly 6 bracket allocations; got {len(self.bracket_allocations)}"
        )


# ---------------------------------------------------------------------------
# Simulation parameters — tunable per run
# ---------------------------------------------------------------------------

@dataclass
class SimParams:
    """Parameters controlling the Monte Carlo simulation."""
    n_players:              int    # Primary sensitivity axis
    mean_tickets_per_player: float = 1.0   # ASSUMPTION: 1 ticket/player as default
    rounds:                 int    = 500
    simulations:            int    = 2_000
    seed:                   int    = 42


@dataclass
class RunConfig:
    """Complete specification for one simulation run."""
    model: ModelConfig
    sim:   SimParams
    label: str


# ---------------------------------------------------------------------------
# Baseline A — PancakeSwap confirmed parameters
# ---------------------------------------------------------------------------

BASELINE_A = ModelConfig(
    name                    = "Baseline A — PancakeSwap",
    econ                    = TokenBurnEcon(burn_rate=0.20),        # CONFIRMED: SRC-013
    bracket_allocations     = (0.02, 0.03, 0.05, 0.10, 0.20, 0.40), # CONFIRMED: SRC-013
    rollover_mode           = "global",                              # ASSUMPTION: unverified
    matching_direction      = "L",                                   # CONFIRMED: SRC-013
    inject_amount           = 8_000.0,                               # ASSUMPTION: sim README
    inject_schedule         = (1, 0, 1, 0, 1, 0, 1),                # ASSUMPTION: 4/7 rounds
    burn_applies_to_injection = True,                                # ASSUMPTION: unverified
    ticket_price            = 2.0,                                   # OPEN: no source confirms
)

BASELINE_A.validate()  # AC-2 gate runs at import


# ---------------------------------------------------------------------------
# D-3 bracket allocation candidates for comparison
#
# D-3A: PCS confirmed allocations (already in BASELINE_A).
# D-3B: SRC-017 diagram — sums to 1.00 in source; scaled to 0.80 here to match
#        Baseline A prize_pool_fraction. ASSUMPTION: burn_rate remains 0.20.
# D-3C: SRC-005 proposal — sums to 1.00 in source; scaled to 0.80 here.
#        ASSUMPTION: same burn structure as D-3A for a burn-normalized comparison.
#
# Alternative interpretation: D-3B and D-3C imply no burn (burn_rate=0); if so,
# remove the ×0.80 scaling and set burn_rate=0.0. This is OPEN pending D-2 resolution.
# ---------------------------------------------------------------------------

_D3B_RAW = (0.02, 0.03, 0.05, 0.15, 0.25, 0.50)  # SRC-017 as stated; sums to 1.00
_D3C_RAW = (0.15, 0.10, 0.10, 0.15, 0.20, 0.30)  # SRC-005 as stated; sums to 1.00

_SCALE = BASELINE_A.econ.prize_pool_fraction  # 0.80 — burn-normalization factor

_D3B_SCALED = tuple(round(v * _SCALE, 10) for v in _D3B_RAW)
_D3C_SCALED = tuple(round(v * _SCALE, 10) for v in _D3C_RAW)


def _make_d3_config(name: str, allocations: tuple[float, ...]) -> ModelConfig:
    cfg = ModelConfig(
        name                    = name,
        econ                    = TokenBurnEcon(burn_rate=0.20),
        bracket_allocations     = allocations,
        rollover_mode           = "global",
        matching_direction      = "L",
        inject_amount           = 8_000.0,
        inject_schedule         = (1, 0, 1, 0, 1, 0, 1),
        burn_applies_to_injection = True,
        ticket_price            = 2.0,
    )
    cfg.validate()
    return cfg


D3_CONFIGS: dict[str, ModelConfig] = {
    "D-3A (PCS)":     BASELINE_A,
    "D-3B (SRC-017)": _make_d3_config("D-3B SRC-017 scaled", _D3B_SCALED),
    "D-3C (SRC-005)": _make_d3_config("D-3C SRC-005 scaled", _D3C_SCALED),
}
