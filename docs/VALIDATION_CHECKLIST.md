# Validation Checklist

## Minimum gate before any result is reported

**EV-1 must pass** (even in intermediate form).
**AC-1, AC-2, AC-3, SC-3 must pass.**

If EV-1 fails: the engine is computing the wrong prize pool. No result should be shared.
If AC-1 fails: bracket probability constants are wrong. Do not run simulations.

---

## Analytical checks (no simulation — run at import or in a test cell)

### AC-1 — Probability normalization `[REQUIRED]`

```python
assert abs(sum(BRACKET_PROBS) - 0.1) < 1e-9
```

Source: Mathematical identity from non-stacking exact-bracket design.
Expected: `sum ≈ 0.09 + 0.009 + 0.0009 + 0.00009 + 0.000009 + 0.000001 = 0.100000`
Fail means: Bracket probability constants are wrong. All downstream math is invalid.

---

### AC-2 — Prize pool consistency `[REQUIRED]`

```python
# For TokenBurnEcon:
assert abs(sum(model.bracket_allocations) - (1 - model.econ.burn_rate)) < 1e-9

# For FiatMarginEcon:
assert abs(sum(model.bracket_allocations) -
           (1 - model.econ.fee_rate - model.econ.reserve_rate - model.econ.referral_rate)) < 1e-9
```

Source: Bracket allocations must partition the prize pool fraction exactly.
Fail means: ModelConfig is internally inconsistent. Simulation will mis-account prize pools.

---

### AC-3 — Scale formula calibration `[REQUIRED]`

```python
from constants import e_tau
assert 26000 < e_tau(6, 38)    < 27000   # Expected: ≈ 26,316
assert    90 < e_tau(6, 10600) <    100  # Expected: ≈ 94
```

Source: `E[τ_6] = 1 / (1 - (1 - 10^{-6})^N)` from problem_statement_math.md §5.1.
Fail means: `e_tau` formula is implemented incorrectly.

---

### AC-4 — Per-ticket EV order of magnitude `[REQUIRED]`

At N=10,000, prize_pool=100,000, Baseline A (α₁=0.02, p₁=0.09):

```python
ev = ev_per_ticket_approx(k=1, alpha_k=0.02, prize_pool=100_000, n=10_000)
assert 2.0 < ev < 2.5   # Expected: 0.02 × 100,000 / (10,000 × 0.09) ≈ 2.22
```

At N=38, same pool:

```python
ev_small = ev_per_ticket_approx(k=1, alpha_k=0.02, prize_pool=100_000, n=38)
assert 500 < ev_small < 700   # Expected: ≈ 584 — large because pool dominated by carry
```

Source: Ziemba approximation from SOURCE_MAP.md; valid when N >> 1/p_k.
Note: The N=38 value appears large because the pool is dominated by injection/carry from prior
rounds (38 players cannot generate $24,745 organically — confirmed by Round 1949 observation).
Fail means: EV formula has wrong units, sign, or coefficient.

---

## Simulation sanity checks

### SC-1 — Bracket hit frequency convergence `[REQUIRED]`

Run 1,000 simulations, T=100 rounds, BASELINE_A.

At N=10,000:

| Bracket | Theoretical P(pays/round) | Acceptable simulated range |
|---|---|---|
| 1 | 1 − (1−0.09)^10000 ≈ 1.000 | [0.995, 1.000] |
| 2 | ≈ 1.000 | [0.995, 1.000] |
| 3 | ≈ 1.000 | [0.990, 1.000] |
| 4 | ≈ 0.593 | [0.55, 0.64] |
| 5 | ≈ 0.086 | [0.07, 0.11] |
| 6 | ≈ 0.010 | [0.005, 0.015] |

At N=38:

| Bracket | Theoretical P(pays/round) | Acceptable simulated range |
|---|---|---|
| 1 | ≈ 0.970 | [0.95, 0.99] |
| 2 | ≈ 0.302 | [0.26, 0.35] |
| 3 | ≈ 0.034 | [0.02, 0.05] |
| 4–6 | < 0.0035 | [0, 0.01] |

Fail means: Winner count sampling or hit probability calculation is wrong.

---

### SC-2 — Carry monotonicity under no winners `[OPTIONAL for v1]`

Run 100 rounds with N=1, no injection, Baseline A.
Expected: carry is non-decreasing over all rounds (no bracket can be won with 1 ticket
and p_k < 0.1; carry only grows).

```python
# carry_out column must be monotonically non-decreasing per simulation path
```

Fail means: Rollover accounting has a sign error.

---

### SC-3 — Single-round hand-verification `[REQUIRED]`

Fix seed=0, n_players=10, mean_tickets=1, prize_pool_carry_in=0.
Run exactly 1 round of BASELINE_A. Record RNG output.

Expected bracket pools (assuming fresh_prize = 10 × ticket_price × 0.80):
- If ticket_price=2.0 and injection=0: revenue=20, fresh_prize=16
- B_1=0.32, B_2=0.48, B_3=0.80, B_4=1.60, B_5=3.20, B_6=6.40

Check by hand:
1. Which brackets had `hits[k]=1`?
2. `payout = sum(B_k for k where hits[k]=1)`
3. `carry_out = sum(B_k for k where hits[k]=0)`
4. `payout + carry_out = fresh_prize = 16.0` — must hold exactly.

Fail means: Off-by-one, sign error, or carry/payout split is wrong.

---

### SC-4 — Long-run prize pool stability `[OPTIONAL for v1]`

At N=10,600, BASELINE_A, T=10,000 rounds, 500 simulations:

```python
# time-average(payout / prize_pool) should converge to approximately:
# sum_k P(bracket k pays) weighted by allocation
# ≈ sum_k alpha_k × (1 - (1-p_k)^10600)
```

Fail means: Carry accounting diverges (pool grows unboundedly or collapses to zero).

---

## Empirical validation checks

### EV-1 — Round 1949 back-check `[REQUIRED — single most diagnostic test]`

**Observed:** Round 1949, Apr 2, 2026, N=38, prize pot = 18,529 CAKE ≈ $24,745.

**Intermediate form (runnable now):**
The prize pool recurrence is: `P_t = 0.80 × (revenue_t + injection_t) + C_{t-1}`

Find the `carry_in` value that satisfies:
```
18,529 = 0.80 × (revenue_t + injection_t) + carry_in
```
With `injection_t = 8,000 × 0.80 = 6,400` (if burn applies) and `revenue_t` unknown
(ticket price unknown). This intermediate form tests the recurrence equation for sign and
coefficient correctness even without knowing ticket price.

**Full form (requires additional data):**
- Ticket price in CAKE — OPEN
- Carry entering Round 1949 — OPEN (requires Round 1948 data)
- Whether burn applies to injection — ASSUMPTION

Action: Use `frefrik/pancakeswap-lottery` to fetch Round 1948 carry_out and Round 1949
revenue. Then run one simulation round with those inputs and compare to 18,529 CAKE.

Fail means: Prize pool recurrence is implemented with wrong coefficient, wrong burn base,
or wrong carry-forward logic. All simulation results are unreliable.

---

### EV-2 — Historical bracket hit rate calibration `[OPTIONAL — deferred to Phase 5]`

Pull last 50 PCS rounds via `frefrik/pancakeswap-lottery`.
Compare empirical P(bracket k pays per round) vs Binomial prediction at real N_t.

OPEN: Requires BSC node / API key and frefrik client setup.

---

### EV-3 — Carry-forward accounting `[OPTIONAL — deferred to Phase 5]`

For any two consecutive historical rounds: `carry_in(t+1) == carry_out(t)`.
OPEN: Requires same data source as EV-2.

---

## Decision criteria

**Accept** model output for reporting when:
- AC-1 through AC-4 all pass
- SC-1, SC-3 pass
- EV-1 passes (intermediate form acceptable for v1)
- A1 vs A2 comparison shows qualitative scale reversal with correct direction

**Reject and diagnose** when:
- EV-1 fails — do not proceed; find the structural error
- A1 and A2 produce similar carry dynamics — N is not correctly entering winner count sampling
- SC-1 bracket frequencies deviate by more than 5 percentage points from theoretical predictions
- `payout + carry_out ≠ prize_pool` in any round (SC-3 arithmetic check)

---

## Open risks

| Risk | Severity | Mitigation |
|---|---|---|
| Ticket price unknown — blocks full EV-1 | High | Run EV-1 intermediate form; defer full EV-1 |
| Rollover mode (global vs per-bracket) unverified | High | Run both modes; report difference |
| Burn on injections unverified | Medium | Run with both True/False; show sensitivity |
| All N values other than 38 are assumed | High | Report all results as conditional on N assumption |
| D-3B and D-3C allocation pool base ambiguous | Medium | Normalize to prize_pool_fraction=0.80 for comparison |
| Baseline B uninstantiatable until D-1..D-5 resolved | Critical | Do not simulate; keep configs as stubs |
