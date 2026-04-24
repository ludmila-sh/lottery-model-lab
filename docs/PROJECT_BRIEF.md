# Project Brief — Lottery Model Lab

## Problem statement

A discrete-round, 6-digit bracketed prize lottery. Players buy tickets; a winning number is
drawn uniformly each round. Each ticket wins at most one of six prize brackets based on
consecutive digit matches from a fixed end. Each bracket's pool is split equally among its
winners (parimutuel). If a bracket has no winners, its allocation carries forward and
enlarges the next round's pool. A periodic external injection supplements ticket revenue.
A fixed fraction is either burned (token model) or redirected as protocol fee (stablecoin model).

Two structurally distinct candidate baselines exist. They are not parameter variants of each
other and cannot be collapsed into a single model until the team resolves D-1.

---

## Mathematical object

Prize pool recurrence:

    P_t = (1 − r) × (revenue_t + I_t) + C_{t−1}

Winner counts (uniform i.i.d. ticket picks):

    N_{k,t} | N_t ~ Binomial(N_t, p_k)
    p_k = 0.9 / 10^k  for k = 1..5
    p_6 = 10^{−6}

Per-winner payout (parimutuel):

    π_{k,t} = B_{k,t} / N_{k,t}   if N_{k,t} > 0
             = rolls forward        if N_{k,t} = 0

Carry-forward (global rollover):

    C_{t+1} = Σ_k B_{k,t} × 1[N_{k,t} = 0]

The carry process is a Markov chain. The jackpot sub-pool {C_{6,t}} is a renewal process
with geometric inter-arrival times.

---

## Why N is critical

    P(bracket k pays in round t) = 1 − (1 − p_k)^N
    E[rounds to first jackpot] ≈ 10^6 / N

| N | E[τ_6] | Interpretation |
|---|---|---|
| 38 (observed PCS) | ~26,316 rounds | ~72 years at 1 round/day. Jackpot never pays organically. |
| 500 | ~2,000 rounds | Jackpot rare; brackets 4–5 still mostly frozen. |
| 10,000 | ~100 rounds | Brackets 4–5 pay regularly; bracket 6 resets ~quarterly. |
| 10,600 (sim assumption) | ~94 rounds | Fictional — no data support. |

At N=38: 70% of prize pool (brackets 4–6) freezes in rollover indefinitely.
At N=10,000: brackets 4–5 pay in 63% and 8.6% of rounds respectively.

All existing simulation results assume N ≈ 10,600. Observed PCS (Round 1949, Apr 2026): 38 players.
**All economic conclusions from prior simulation runs are conditional on this fictional assumption.**

---

## Candidate model classes

| Class | When applicable |
|---|---|
| Discrete probability | Bracket probabilities, per-round EV |
| Binomial | Winner counts N_{k,t} \| N_t |
| Renewal process (geometric inter-arrivals) | Jackpot sub-pool between hits |
| Markov chain (scalar or 6-vector) | Prize pool carry dynamics |
| Monte Carlo simulation | Path-dependent carry distribution, tail risk, non-stationary N |
| Stochastic comparative statics | Feature break-even under uncertain demand response |

---

## Two candidate baselines

### Baseline A — PancakeSwap (confirmed from SRC-013, Round 1949)

| Parameter | Value | Status |
|---|---|---|
| Currency | CAKE (volatile token) | CONFIRMED |
| Prize pool fraction | 80% | CONFIRMED |
| Burn rate | 20% of (revenue + injection) | CONFIRMED |
| Bracket allocations | 2/3/5/10/20/40% | CONFIRMED |
| Matching direction | Left-to-right | CONFIRMED |
| Protocol cash margin | Zero (benefit = token burn) | CONFIRMED |
| Injection amount | ~8,000 CAKE | ASSUMPTION — unverified against docs |
| Injection schedule | [1,0,1,0,1,0,1] per 7 rounds | ASSUMPTION — unverified |
| Burn on injections | Yes | ASSUMPTION — unverified |
| Rollover mode | Global | ASSUMPTION — unverified |
| Ticket price | OPEN | Not confirmed in any source |
| Observed scale | 38 players/round | CONFIRMED |

### Baseline B — Team-target product (most specific source: SRC-018)

All fields are OPEN until D-1 through D-5 are resolved. Baseline B cannot be instantiated.

| Parameter | Candidate values | Conflict |
|---|---|---|
| Currency | USDT (SRC-018) vs CAKE (implied SRC-006) | C-004 |
| Ticket price | $1 (SRC-005) / $2 (sim) / $5 USDT (SRC-018) | C-003 |
| Prize pool fraction | 70% if stablecoin (SRC-018) | OPEN |
| Protocol cash margin | 15% per ticket (SRC-018) | OPEN |
| Bracket allocations | Three candidates — see D-3 | C-002 |
| Injection model | Fixed / dynamic shortfall / none | OPEN |
| Target scale | Not stated anywhere | OPEN |

---

## Five open decisions

D-1 is prior to all others. All others can be decided in parallel once D-1 is fixed.

| ID | Decision | Candidates | Consequence if wrong |
|---|---|---|---|
| D-1 | Token vs stablecoin | Token (burn logic) / Stablecoin (cash fee, no burn) | Determines entire economic model class |
| D-2 | Fee/burn structure | PCS 80/20 / SRC-018 70/15/5 / custom | Sets prize pool equation |
| D-3 | Bracket allocations | PCS 2/3/5/10/20/40% / SRC-017 2/3/5/15/25/50% / SRC-005 15/10/10/15/20/30% | Qualitatively changes EV at small N |
| D-4 | Matching direction | Left-to-right / Right-to-left | Implementation spec; probability math unchanged |
| D-5 | Injection model | Fixed / Dynamic shortfall / None | Largest controllable cost driver |

---

## Success criteria

1. Simulator reproduces Round 1949 prize pool (18,529 CAKE) to within rounding given real inputs. **(EV-1)**
2. Simulated bracket hit frequencies at N=10,000 match Binomial predictions within 2 standard errors. **(SC-1)**
3. A1 (N=38) vs A2 (N=10,600) produce qualitatively different carry dynamics and bracket payout rates. **(scale reversal)**
4. D-3 bracket allocation comparison produces clear, traceable output table for three candidates. **(D-3 decision support)**
5. Morris sensitivity screen confirms N as the dominant parameter across protocol PnL and carry metrics.

---

## Known assumptions

| ID | Statement | Risk if wrong |
|---|---|---|
| A-1 | Winning number uniform i.i.d. | All bracket probabilities invalid |
| A-2 | Ticket picks approximately uniform | Effective p_k per ticket shifts; low-bracket EV changes |
| A-3 | N_t exogenous and stationary per scenario | Endogenous churn invalidates all closed-form EV |
| A-4 | Claim rate = 100% | Prize pool grows faster; EV per claiming ticket increases |
| A-5 | Injection = 8,000 CAKE at [1,0,1,0,1,0,1] cycle | Largest cost driver; 20% error propagates through all scenarios |
| A-6 | Burn applies to injections | 20% error per injection per round |
| A-7 | Rollover mode = global | Jackpot growth dynamics differ under per-bracket mode |

---

## Known unknowns

- PCS ticket price in CAKE — blocks per-ticket EV for Baseline A
- Whether burn applies to injections — changes financial model by 20% of injection
- Real PCS rollover mode — changes jackpot sub-pool dynamics
- D-1 through D-5 — block Baseline B entirely
- Team's target player count — blocks all scenario calibration

---

## What is reused

| Source | What is reused |
|---|---|
| `inputs/pancake_lottery_sim/engine.py` | Vectorized MC engine, bracket probability model, analytics pattern |
| Garvey et al. LGGR (arXiv 2311.04826) | Closed-form stationary distribution of bracket-6 carry — validation reference |
| Ziemba et al. (parimutuel) | Per-ticket EV approximation: `E[B_{k,t}/N_{k,t}] ≈ α_k × P_t / (N_t × p_k)` |
| Walker & Young (2001) | Bracket allocation design reasoning at small N |
| SALib | Morris + Sobol sensitivity analysis (Phase 5) |
| `frefrik/pancakeswap-lottery` | On-chain historical data for EV-1 empirical validation |

## What must be built from scratch

- Three-tier parameter hierarchy replacing `assumptions.py`
- Two-branch economic layer (`token_burn` vs `fiat_margin`) — not in existing simulator
- Analytical closed-form module (`E[τ_k]`, `P(bracket pays)`, per-ticket EV)
- Comparison runner (`run_set` → metrics → comparison DataFrame)
- SALib sensitivity wrapper (Phase 5)
