"""
Tier 1 — Immutable mathematical constants and analytical formulas.

All values are derived from the lottery structure, not assumed.
Source: docs/problem_statement_math.md §2.3 and §5.1

Correctness gates AC-1 and AC-3 run at import.
"""
from __future__ import annotations

from typing import Final

# ---------------------------------------------------------------------------
# Bracket probabilities — exact, direction-agnostic for uniform ticket picks
# Source: p_k = 0.9/10^k for k=1..5; p_6 = 10^{-6}
# docs/problem_statement_math.md §2.3
# ---------------------------------------------------------------------------

BRACKET_PROBS: Final[list[float]] = [
    0.9 / 10**1,   # k=1: 0.09
    0.9 / 10**2,   # k=2: 0.009
    0.9 / 10**3,   # k=3: 0.0009
    0.9 / 10**4,   # k=4: 0.00009
    0.9 / 10**5,   # k=5: 0.000009
    1.0 / 10**6,   # k=6: 0.000001  (jackpot)
]

N_DIGITS:     Final[int] = 6
DIGIT_BASE:   Final[int] = 10
TICKET_SPACE: Final[int] = DIGIT_BASE ** N_DIGITS  # 1,000,000

# AC-1 — probability normalization gate (runs at import)
_prob_sum = sum(BRACKET_PROBS)
assert abs(_prob_sum - 0.1) < 1e-9, (
    f"AC-1 FAIL: BRACKET_PROBS must sum to 0.1; got {_prob_sum:.15f}"
)


# ---------------------------------------------------------------------------
# Analytical formulas
# ---------------------------------------------------------------------------

def e_tau(k: int, n: float) -> float:
    """Expected rounds until bracket k is first hit, given n tickets per round.

    Formula: 1 / (1 - (1 - p_k)^n)
    Approximation: ~10^k / (0.9 * n) for k=1..5; ~10^6 / n for k=6.
    Source: docs/problem_statement_math.md §5.1
    """
    if n <= 0:
        return float("inf")
    p_k = BRACKET_PROBS[k - 1]
    p_hit = 1.0 - (1.0 - p_k) ** n
    if p_hit <= 0:
        return float("inf")
    return 1.0 / p_hit


def p_bracket_pays(k: int, n: float) -> float:
    """Probability bracket k is won in a given round with n tickets.

    Formula: 1 - (1 - p_k)^n
    """
    p_k = BRACKET_PROBS[k - 1]
    return 1.0 - (1.0 - p_k) ** n


def ev_per_ticket_approx(k: int, alpha_k: float, prize_pool: float, n: float) -> float:
    """Approximate per-ticket expected value for bracket k.

    Formula: alpha_k * prize_pool / (n * p_k)
    Source: Ziemba et al. parimutuel approximation — see docs/SOURCE_MAP.md
    ASSUMPTION: Valid only when n >> 1/p_k (bracket k wins almost every round).
    Degrades for brackets 4-6 at small n. Use only for sanity checks, not precise EV.
    """
    if n <= 0:
        return 0.0
    p_k = BRACKET_PROBS[k - 1]
    return alpha_k * prize_pool / (n * p_k)


# ---------------------------------------------------------------------------
# Named calibration constants — used in AC-3 and comparison outputs
# ---------------------------------------------------------------------------

E_TAU_6_AT_N38:    Final[float] = e_tau(6, 38)     # ≈ 26,316 rounds
E_TAU_6_AT_N10600: Final[float] = e_tau(6, 10_600) # ≈ 94 rounds

# AC-3 — scale formula calibration gate (runs at import)
assert 26_000 < E_TAU_6_AT_N38 < 27_000, (
    f"AC-3 FAIL: E[tau_6] at N=38 out of expected range [26000, 27000]; got {E_TAU_6_AT_N38:.1f}"
)
assert 90 < E_TAU_6_AT_N10600 < 100, (
    f"AC-3 FAIL: E[tau_6] at N=10600 out of expected range [90, 100]; got {E_TAU_6_AT_N10600:.1f}"
)
