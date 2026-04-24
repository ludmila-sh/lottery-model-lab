# Implementation Plan — Research Tool v1

## Goal of v1

A minimal Python framework that:
1. Runs Baseline A at any N — specifically N=38 and N=10,600.
2. Runs the D-3 bracket allocation comparison at a fixed N.
3. Passes all required correctness gates before any result is reported.
4. Produces a clear comparison table from multiple `RunConfig` objects.

Not in v1: sensitivity analysis, Quarto, Marimo, behavioral/segment overlays, Baseline B
(blocked on D-1..D-5), per-bracket rollover mode, on-chain data ingestion.

---

## Architecture

```
research/
├── constants.py        # Tier 1 — immutable math constants + analytical formulas
├── model_config.py     # Tier 2/3 — dataclass hierarchy, two baselines, D-3 configs
├── simulator.py        # Monte Carlo engine — branches on econ_class
├── metrics.py          # compute_metrics(df, config) → dict
├── compare.py          # run_set(configs) → comparison DataFrame
└── notebooks/
    └── 01_baseline_comparison.ipynb
```

---

## Three-tier parameter hierarchy

| Tier | Contents | Mutable? |
|---|---|---|
| 1 — Constants | `BRACKET_PROBS`, `TICKET_SPACE`, analytical formulas | Never |
| 2 — Fixed | `econ_class`, `rollover_mode`, `matching_direction` — model-class choices | Per model definition |
| 3 — Tunable | `n_players`, `bracket_allocations`, `inject_amount`, `burn_rate` | Swept in scenarios / sensitivity |

---

## Build order

### Phase 1 — Foundation  `COMPLETE`
1. `constants.py` — bracket probs, assertions, analytical formulas
2. `model_config.py` — dataclasses, BASELINE_A, D-3 configs

**Gate:** AC-1, AC-2, AC-3 pass on import. ✓

### Phase 2 — Engine + Analysis + Notebook  `COMPLETE`
3. `simulator.py` — Monte Carlo engine, token_burn and fiat_margin branches; `hit_k1`…`hit_k6` columns added
4. `metrics.py` — compute_metrics(df, config) → dict (carry, bracket, payout, PnL, jackpot groups)
5. `compare.py` — run_set(configs) → comparison DataFrame
6. `notebooks/01_baseline_comparison.ipynb` — assumptions block, AC-1..4, SC-3, A1vsA2, SC-1, D-3 comparison

**Gates verified:**
- SC-3 (payout + carry_out == prize_pool): ✓
- Scale reversal (A1 carry/rev ≈ 237×, A2 ≈ 2×; ratio > 10×): ✓
- SC-1 bracket frequencies at N=10,000 vs theoretical: ✓ (in notebook)
- All hit_k1…hit_k6 columns present in simulator output: ✓

### Phase 3 — Sensitivity (deferred — not v1)
7. `sensitivity.py` — SALib Morris + Sobol wrapper
8. `notebooks/02_scale_sensitivity.ipynb`

---

## File specifications

### `constants.py`

Must contain:
- `BRACKET_PROBS: list[float]` — exact values computed as `0.9/10^k`
- `N_DIGITS = 6`, `DIGIT_BASE = 10`, `TICKET_SPACE = 10**6`
- `e_tau(k, n)` — expected rounds to first hit in bracket k
- `p_bracket_pays(k, n)` — P(bracket k pays in round t)
- `ev_per_ticket_approx(k, alpha_k, prize_pool, n)` — Ziemba approximation
- Named calibration constants: `E_TAU_6_AT_N38`, `E_TAU_6_AT_N10600`
- Assertions (AC-1, AC-3) that run at import

### `model_config.py`

Must contain:
- `TokenBurnEcon(burn_rate)` — Baseline A economic layer
- `FiatMarginEcon(fee_rate, reserve_rate, referral_rate)` — Baseline B economic layer
- `ModelConfig` — frozen dataclass: econ, bracket_allocations, rollover_mode,
  matching_direction, inject_amount, inject_schedule, burn_applies_to_injection, ticket_price
- `SimParams` — n_players, mean_tickets_per_player, rounds, simulations, seed
- `RunConfig` — model + sim + label
- `ModelConfig.validate()` — checks AC-2 (allocations sum to prize_pool_fraction)
- `BASELINE_A` — PCS confirmed parameters with ASSUMPTION labels on unverified fields
- `D3_CONFIGS` — dict of three RunConfig objects for D-3 comparison at N=500

**D-3 allocation note:** D-3A allocations sum to 0.80 (with 20% burn). D-3B and D-3C
allocations as stated in sources sum to 1.00, implying no burn. For a burn-normalized
comparison (same burn rate), rescale D-3B and D-3C by 0.80. Mark this as ASSUMPTION.

### `simulator.py`

Entry point: `simulate(config: RunConfig) -> pd.DataFrame`

Core loop (vectorized over simulations, sequential over rounds):
1. Sample n_tickets ~ n_players + Poisson((mean_tix - 1) × n_players)
2. Compute revenue = n_tickets × ticket_price
3. Compute injection from schedule
4. Branch on econ_class:
   - `token_burn`: burn = rate × (revenue + injection); fresh_prize = (1-rate) × (revenue + injection)
   - `fiat_margin`: fee = rate × revenue; fresh_prize = prize_fraction × revenue + injection
5. prize_pool = fresh_prize + carry_in
6. bracket_pools = alloc × prize_pool  (shape: 6 × sims)
7. hit_probs = 1 - (1 - p_k)^n_tickets  (shape: 6 × sims)
8. hits = Bernoulli(hit_probs)
9. payout = sum_k(bracket_pools_k × hits_k)
10. carry_out = sum_k(bracket_pools_k × (1 - hits_k))
11. carry = carry_out  (state update)

Output columns: `round_index, simulation_id, n_tickets, revenue, injection,
burn_or_fee, prize_pool, payout, carry_in, carry_out, protocol_pnl, hit_k1…hit_k6`

ASSUMPTION: No segment behavioral overlay. N is a direct SimParams input.
ASSUMPTION: Tickets per player ~ Poisson (minimum 1 per player).
ASSUMPTION: All ticket picks uniform (no entropy/clustering in v1).

### `metrics.py`

`compute_metrics(df: pd.DataFrame, config: RunConfig) -> dict`

Output groups (computed across simulations, averaged over rounds unless noted):
- **Prize pool**: `E_prize_pool`, `std_prize_pool`, `E_carry`, `carry_to_revenue_ratio`
- **Protocol PnL**: `E_pnl_per_round`, `E_cumulative_pnl`, `P_cumulative_pnl_negative`
- **Scale**: `rounds_to_first_bracket_k_hit` (per bracket, from simulation)
- **Tail**: `P_carry_exceeds_10x_revenue`, `max_carry_observed`

### `compare.py`

`run_set(configs: list[RunConfig]) -> pd.DataFrame`

- Runs each config via `simulate()`, calls `compute_metrics()`, pivots to comparison table
- Index: `config.label`; columns: metric names
- Returns one row per config

---

## Required baseline runs

| Run ID | Config | N | Purpose |
|---|---|---|---|
| A1 | BASELINE_A | 38 | Real observed PCS scale — correctness reference |
| A2 | BASELINE_A | 10,600 | Existing simulator fictional scale — divergence check |
| D3-A | D-3A, N=500 | 500 | PCS allocation — jackpot-heavy |
| D3-B | D-3B, N=500 | 500 | SRC-017 — even more jackpot-heavy |
| D3-C | D-3C, N=500 | 500 | SRC-005 — frequency-balanced |

---

## Required comparison outputs

**From A1 vs A2:**
- `E[carry after T=500 rounds]` — must diverge significantly (A1 >> A2)
- `P(bracket 6 pays in T=500 rounds)` — A1 ≈ 0, A2 ≈ 1
- `P(bracket 4 pays per round)` — A1 ≈ 0, A2 ≈ 0.62
- `E[per-ticket EV, bracket 1]` — both computable; A1 much higher due to pool inflation

**From D3 comparison at N=500:**
- `P(bracket 1 pays per round)` — all three
- `P(bracket 6 pays per round)` — all three
- `E[per-ticket EV by bracket]` — all three
- `E[carry after T=500 rounds]` — D-3C expected to have lowest carry (more pays out)

---

## Sensitivity analysis order (Phase 5 — deferred)

Use SALib. Morris first, then Sobol on survivors.

1. **N** — 10 to 100,000 (log scale). Most important axis. Run first.
2. **α₆** — 0.20 to 0.60. Jackpot allocation fraction.
3. **Injection amount** — 0 to 20,000. Largest controllable cost.
4. **Burn/fee rate** — 0.10 to 0.30.

Morris screen: ~200 evaluations (4 parameters × 50 trajectories).
Sobol: ~6,000 evaluations on Morris survivors only.

---

## Deferred items

- Behavioral segment overlay (entropy, manual share)
- Per-bracket rollover mode
- Baseline B instantiation (blocked on D-1..D-5)
- SALib sensitivity analysis
- `frefrik/pancakeswap-lottery` on-chain data ingestion
- Quarto / Marimo
- Multiplier features, free tickets, cashback, referral cost overlays

---

## Definition of done (v1)

- [x] `constants.py`: imports cleanly; AC-1 and AC-3 pass on import
- [x] `model_config.py`: BASELINE_A and D3_CONFIGS defined; AC-2 passes on import
- [x] `simulator.py`: runs BASELINE_A, returns expected column schema (incl. hit_k1…hit_k6)
- [x] SC-3: single-round hand-verification passes
- [ ] EV-1 (intermediate): prize pool recurrence reproduces 18,529 CAKE for known carry-in — deferred (requires Round 1948/1949 on-chain data)
- [x] A1 vs A2: qualitative scale reversal confirmed (carry/rev 237× vs 2×)
- [x] D-3 comparison table: three allocation candidates at N=38 and N=10,600
- [x] Notebook: `01_baseline_comparison.ipynb` created; runs clean top-to-bottom

---

## Stop / go criteria

**STOP and diagnose if:**
- `sum(BRACKET_PROBS)` deviates from 0.1 by more than 1e-9
- EV-1 fails (engine is computing wrong prize pool)
- A1 and A2 produce the same carry dynamics (N not wired into winner counts)
- `ModelConfig.validate()` raises on BASELINE_A (config is internally inconsistent)

**GO to Phase 5 only after:**
- All v1 definition-of-done items checked
- Scale reversal (A1 vs A2) is confirmed and documented
- At least one team decision (D-1 through D-5) has been made
