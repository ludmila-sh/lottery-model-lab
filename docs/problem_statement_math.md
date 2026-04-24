# Mathematical Formulation

## Status
**Draft. Dual-baseline version.** Parameters marked `[open]` cannot be fixed until the team makes the decisions listed in docs/dual_baseline.md (D-1 through D-5). The probability structure is shared across both baselines and is written once. The economic layer branches into two candidate models (M-A and M-B) that are kept separate.

---

## 1. Sets and indices

| Symbol | Description |
|---|---|
| t ∈ {1, 2, …, T} | Round index. T is the planning horizon (finite for analysis; ∞ for long-run questions). |
| k ∈ {1, …, 6} | Bracket index. k = 6 is the jackpot. |
| i ∈ {1, …, N_t} | Ticket index within round t. |
| d = 6 | Number of digits per ticket. Fixed. |
| b = 10 | Digit base. Fixed. |
| n = b^d = 10^6 | Total ticket space. Fixed. |

---

## 2. Shared probability structure (both baselines)

### 2.1 Ticket and winning number

A ticket is a number x ∈ {0, 1, …, n − 1}. Equivalently x = (x₁, x₂, x₃, x₄, x₅, x₆) with each digit xⱼ ∈ {0, …, 9}.

The winning number w_t ∈ {0, …, n − 1} is drawn i.i.d. each round:

    w_t ~ Uniform{0, …, 999999}

### 2.2 Bracket assignment — direction-dependent

The bracket function K(x, w, δ) assigns ticket x to a bracket level given winning number w and direction parameter δ.

**Direction parameter δ [open — see D-4]:**
- δ = L (left-to-right): the PCS convention, confirmed by UI
- δ = R (right-to-left): stated in team notes (SRC-005, SRC-006, SRC-017)

**Under δ = L (left-to-right):**

    Define prefix_k(x) = ⌊x / 10^(6−k)⌋   for k = 1, …, 6

    K_L(x, w) = max{ k ∈ {0,…,6} : prefix_k(x) = prefix_k(w) }

Interpretation: K_L = k means the first k digits of x match w, and the (k+1)-th does not (for k < 6). K_L = 6 means all six digits match.

**Under δ = R (right-to-left):**

    Define suffix_k(x) = x mod 10^k   for k = 1, …, 6

    K_R(x, w) = max{ k ∈ {0,…,6} : suffix_k(x) = suffix_k(w) }

Interpretation: K_R = k means the last k digits of x match w, and the (k+1)-th from the right does not.

**Note on direction:** The probability distribution P(K = k) is identical under both conventions when x and w are both uniform. However, the events {K_L = k} and {K_R = k} are different subsets of the (x, w) product space. For non-uniform ticket choices (manual pickers who choose "round" or "meaningful" numbers), the two directions produce different realized bracket distributions depending on which end of the ticket the clustering occurs. Direction cannot be treated as irrelevant to a full model.

### 2.3 Exact-bracket probabilities

For a uniformly distributed ticket x and uniform winning number w:

    p_k = P(K(x, w, δ) = k) = 0.9 / 10^k   for k = 1, …, 5
    p_6 = 1 / 10^6

These values are confirmed numerically by the simulator validation (SRC-011) and follow directly from the non-stacking exact-bracket definition. They are independent of direction δ under uniform draws.

    Σ_{k=1}^{6} p_k = 0.9(1/10 + 1/100 + … + 1/10^5) + 1/10^6
                    = 0.9 × (1 − 10^{−5}) / 9 + 10^{−6}
                    ≈ 0.1 (approximately 10% win rate per ticket across all brackets)

### 2.4 Winner counts

Let N_t = total tickets in round t (paid + free). Define:

    N_{k,t} = number of tickets assigned to bracket k in round t
            = Σ_{i=1}^{N_t} 1[ K(x_{i,t}, w_t, δ) = k ]

Under uniform i.i.d. ticket picks:

    N_{k,t} | N_t ~ Binomial(N_t, p_k)   approximately

The approximation is tight when N_t << n = 10^6 (no collision effects). Tickets are not i.i.d. in practice — clustering via manual picking introduces correlation. This is modeled in the simulator with an entropy parameter but is not derived from data.

---

## 3. Prize pool dynamics

### 3.1 Parameters (shared structure, values differ by baseline)

| Parameter | Symbol | Baseline A (PCS) | Baseline B (team-target) | Status |
|---|---|---|---|---|
| Prize pool fraction | π | 1 − r_b = 0.80 | 1 − f [open] | open for B |
| Burn / deduction rate | r | 0.20 (token burn) | 0 or f [open] | open for B |
| Bracket allocations | α = (α₁,…,α₆) | (0.02, 0.03, 0.05, 0.10, 0.20, 0.40) | [open — three candidates] | open for B |
| Ticket price | p | unknown CAKE [verify] | [open — $1/$2/$5 USDT] | open |
| Injection per eligible round | I | ~8,000 CAKE [verify] | [open] | open |
| Injection schedule | s_t ∈ {0,1} | [1,0,1,0,1,0,1] per 7 rounds [verify] | [open] | open |
| Rollover mode | ρ ∈ {global, bracket} | [unverified] | [unspecified] | open |
| Claim rate | q | 1.0 (assumed) | [open] | open |
| Matching direction | δ | L (confirmed) | [open — L or R] | open for B |

Constraints on α: Σ_{k=1}^{6} α_k = 1 − r (bracket allocations partition the prize pool).

### 3.2 Revenue and fresh pool

    revenue_t = p × T^paid_t   (paid ticket revenue; T^paid_t ≤ N_t)
    fresh_t   = revenue_t + s_t × I

**Model A (PCS — token burn):**

    burn_t = r × fresh_t              (r = 0.20; token destroyed, not cash)
    F_t    = (1 − r) × fresh_t       (fresh funds entering the prize pool)

**Model B (team-target — cash-margin, if stablecoin):**

    fee_t  = f × revenue_t            (f = team protocol fee rate, e.g., 0.15)
    res_t  = g × revenue_t            (g = reserve fund rate, e.g., 0.05)
    F_t    = (1 − f − g) × revenue_t + s_t × I_t   (fresh prize funds)

*If D-1 resolves to token (not stablecoin), Model B reduces to a parameter override of Model A. Until D-1 is decided, both structures are in scope.*

### 3.3 Prize pool and bracket pools

Let C_t = carry entering round t.

    P_t  = F_t + C_t          (total prize pool available in round t)
    B_{k,t} = α_k × P_t       (allocation to bracket k)

### 3.4 Payouts

Per-winner payout in bracket k, round t:

    π_{k,t} = (B_{k,t} × q) / N_{k,t}    if N_{k,t} > 0
    π_{k,t} = undefined                    if N_{k,t} = 0

Total payout:

    Payout_t = Σ_k B_{k,t} × q × 1[N_{k,t} > 0]

### 3.5 Carry-forward (rollover)

**Global rollover (ρ = global):**

    C_{t+1} = Σ_k B_{k,t} × 1[N_{k,t} = 0]

All unhit bracket amounts pool together. They re-enter the prize pool next round and are redistributed across all brackets by α.

**Per-bracket rollover (ρ = bracket):**

    C_{k,t+1} = B_{k,t} × 1[N_{k,t} = 0]   for each k
    C_{t+1}   = Σ_k C_{k,t+1}

Under per-bracket rollover, each bracket accumulates its own carry. The jackpot bracket accumulates independently.

The two modes differ structurally: under global rollover, a large jackpot carry benefits all brackets proportionally; under per-bracket rollover, jackpot and lower brackets accumulate separately.

### 3.6 State representation

Under global rollover: the state is scalar — S_t = C_t ∈ ℝ₊.
Under per-bracket rollover: the state is a vector — S_t = (C_{1,t}, …, C_{6,t}) ∈ ℝ₊^6.

Given stationary N_t (i.i.d. player count), the process {S_t} is a time-homogeneous Markov chain on ℝ₊ (or ℝ₊^6).

---

## 4. Economic layer — protocol PnL

### 4.1 Model A (PCS — token burn)

Protocol cash position: zero. The protocol extracts no CAKE per round from ticket sales.

    PnL_A_t = − s_t × I    (injection is a cost; no cash revenue)

Benefit to protocol: deflationary effect of burn_t CAKE destroyed per round. This is not a cash flow and is not captured in PnL_A_t; it enters through the external market for the token.

### 4.2 Model B (team-target — cash-margin, if stablecoin)

Protocol cash position per round:

    PnL_B_t = fee_t − s_t × I_t − feature_cost_t
            = f × revenue_t − s_t × I_t − feature_cost_t

where feature_cost_t covers cashback, free tickets, referral payments, losers reserve drawdowns, and other direct subsidies.

Break-even condition per round:

    f × revenue_t > s_t × I_t + feature_cost_t

Over horizon T:

    Σ_{t=1}^{T} PnL_B_t > 0    (cumulative viability)

*If D-1 resolves to token (not stablecoin), Model B collapses to a parameter-override of Model A and the burn term reappears.*

---

## 5. Model class and structural analogues

### 5.1 Probability layer

The ticket-level probability structure is a **compound discrete lottery**:
- Bracket assignment is a categorical random variable with known probabilities {p_k}.
- Prize per winner is a random variable determined by both the bracket allocation and the number of co-winners (parimutuel structure).
- This is a variant of a **parimutuel prize game with multiple brackets**.

The jackpot (bracket 6) behaves as a **Geometric random variable for time-to-first-hit**:

    τ_6 = min{ t : N_{6,t} ≥ 1 }

Under constant N tickets per round:

    P(τ_6 = t) = (1 − p₆_eff)^{t−1} × p₆_eff    where p₆_eff = 1 − (1 − p_6)^N

    E[τ_6] = 1 / p₆_eff ≈ 10^6 / N   (for N << 10^6)

At N = 38 tickets: E[τ_6] ≈ 26,316 rounds ≈ 72 years at one round/day.
At N = 10,000 tickets: E[τ_6] ≈ 100 rounds ≈ 100 days.

This illustrates the scale-sensitivity of the model: the jackpot prize pool grows indefinitely at low scale and depletes regularly at high scale.

### 5.2 Prize pool dynamics

The prize pool process {P_t} is structurally similar to a **ruin process run in reverse**: it grows (from injections and rollover) and depletes (from payouts). It is not a standard random walk because payouts are proportional to the pool, not fixed.

Under per-bracket rollover, the jackpot sub-pool {C_{6,t}} follows a discrete-time process with:
- Increments: α₆ × (F_t + C_t) each round
- Resets to zero when bracket 6 is hit

This is a **renewal process** with Geometric inter-arrival times and a pool that grows between renewals. The distribution of the jackpot pool at the moment of first hit (the "jackpot at time of win") has a compound geometric distribution.

### 5.3 Feature economics layer

Feature analysis reduces to a **stochastic comparative statics problem**: given a feature that increases N_t by Δ_t and costs C_t per round, is:

    E[ p × Δ_t ] > E[ C_t ]

across all plausible realizations of demand response. This is tractable algebraically if Δ_t and C_t are assumed to be functions of N_t with known parameters. In practice, Δ_t is unknown and estimated with large uncertainty.

---

## 6. What is tractable analytically

The following results have closed-form or exact expressions and do not require simulation:

| Quantity | Formula | Notes |
|---|---|---|
| P(K = k) for uniform tickets | 0.9 / 10^k (k=1..5); 10^{-6} (k=6) | Direction-independent under uniform draws |
| E[N_{k,t}] | N_t × p_k | Expected bracket winners |
| P(at least one jackpot winner) | 1 − (1 − 10^{-6})^{N_t} | Per-round |
| E[τ_6] under constant N | 10^6 / N approximately | Expected rounds to first jackpot |
| P(bracket k pool is ever paid out in round t) | 1 − (1 − p_k)^{N_t} | Per-bracket, per round |
| Per-ticket EV at given pool | Σ_k p_k × E[B_{k,t} / N_{k,t} \| N_{k,t} > 0, N_t] | Requires approximation for E[1/N_{k,t}]; tractable for large N_t |
| Break-even condition for a feature (algebraic) | f × ΔN > ΔC per round | Deterministic form; requires Δ estimates |
| Expected jackpot pool at round T given no jackpot win | Geometric sum: Σ_{t=1}^{T} α_6 × F_t | Under deterministic F_t |

### Useful approximation for large N_t

When N_t >> 1/p_k (i.e., bracket k is won almost every round):

    E[B_{k,t} / N_{k,t}] ≈ α_k × P_t / (N_t × p_k) = α_k × P_t × 10^k / (0.9 × N_t)

This gives the expected per-ticket prize value in bracket k as proportional to P_t and inversely proportional to N_t. It holds for brackets 1–3 even at modest N_t; it fails for brackets 5–6 at any realistic scale.

---

## 7. What requires simulation

The following quantities are not tractable in closed form:

| Quantity | Why simulation is needed |
|---|---|
| Distribution of P_t over many rounds | Carry dynamics are path-dependent; prize pool is heavy-tailed at low scale |
| Joint distribution of (N_{k,t}, B_{k,t}) | Carry introduces inter-round dependence; not a simple product distribution |
| Tail risk: P(Σ_t PnL_t < threshold) | Requires full path distribution over T rounds |
| Effect of non-uniform ticket picks | Entropy parameter is a heuristic; validation requires Monte Carlo |
| Feature sensitivity: distribution of outcomes under uncertain demand response | Parameter uncertainty compounds over 50–100 rounds; analytical bounds are too loose |
| Rollover mode comparison (global vs per-bracket) | Impacts prize pool path; no closed-form comparison exists |

---

## 8. Parameters not yet fixed

The following parameters must be specified before the mathematical model can be used for any quantitative analysis. They are classified as structural (change the model class) or numeric (change parameter values within a fixed model).

**Structural — resolve D-1 first:**
- r (burn rate) vs f + g (fee + reserve): determines Model A or Model B. Cannot be bridged.
- Currency unit: determines what "value" means in all monetary quantities.

**Numeric — can be fixed independently once model class is chosen:**
- p (ticket price): blocks all unit economics [open, C-003]
- α = (α₁,…,α₆) (bracket allocations): blocks all prize-pool distribution math [open, C-002]
- I and s_t (injection amount and schedule): blocks baseline financial model [open, C-007]
- δ (matching direction): blocks the formal definition of K(x, w, δ) [open, C-001]
- ρ (rollover mode): blocks the carry-forward equation [open, C-006]
- q (claim rate): modifies Payout_t; can default to 1.0 with explicit caveat [assumed A-4]

---

## 9. Assumptions

| ID | Statement | Type | If violated |
|---|---|---|---|
| A-1 | w_t ~ Uniform{0,…,999999}, i.i.d. across rounds | Distributional | Probability formulas invalid; any non-uniformity or manipulability in RNG changes p_k |
| A-2 | Ticket picks are approximately uniform for random pickers | Approximation | Effective p_k per ticket varies; expected per-ticket value in low brackets changes |
| A-3 | N_t is exogenous and does not depend on prior round outcomes | Independence | Feature analysis must account for streak effects, dropout after losing runs |
| A-4 | Claim rate q = 1.0 (all winners claim) | Default | Unclaimed prizes remain in carry; prize pool grows faster; expected EV per claiming ticket increases |
| A-5 | Rounds are independent given N_t and C_t (no memory beyond carry) | Markov | If player behavior depends on prior payouts, the state space must be expanded |

---

## 10. Executive summary, key assumptions, and open decisions

### Executive summary

The lottery is a discrete-round parimutuel prize game with six prize brackets, an external funding injection, and a rollover mechanism that carries unhit prize amounts forward. The probability structure is well-defined and direction-agnostic for uniform ticket picks, but the economic layer has two structurally distinct candidate models — a token-burn model (PancakeSwap baseline) and a cash-margin model (team-target notes) — which cannot be treated as parameter variants of each other. Until the team decides whether the product is token-denominated or stablecoin-denominated, the formal model is necessarily two-layered. The most critical numerical risk is the scale assumption: at low player counts (tens of players per round, as observed on PancakeSwap), the upper three brackets almost never pay out organically, the jackpot accumulates without bound, and all feature economics are qualitatively different from the high-volume regime the simulator currently models.

### Five key assumptions

| # | Assumption | Risk if wrong |
|---|---|---|
| 1 | The winning number is drawn uniformly and independently each round | All bracket probabilities change; fairness analysis collapses |
| 2 | Ticket picks are approximately uniform (enough to use the i.i.d. binomial approximation for winner counts) | Non-uniform clustering reduces effective coverage of high brackets; per-ticket EV in low brackets increases |
| 3 | Player count per round is exogenous and stationary for baseline analysis | Endogenous churn invalidates all closed-form EV calculations |
| 4 | Claim rate is 100% | Unclaimed prizes silently inflate the carry; if claim rate is low, the prize pool grows faster than modeled and long-run EV calculations are optimistic |
| 5 | The simulator's ~10,000 tickets/round is the relevant operating scale for the team's product | This is unsupported by any team document; the observed PCS scale is 38 players/round; at 100× lower scale the economic conclusions reverse qualitatively |

### Five open decisions

| # | Decision | Binary or categorical choice required |
|---|---|---|
| 1 | **D-1 — Economic model class**: token-burn lottery or cash-margin fiat lottery | Determines whether the model has a burn term or a cash-fee term; cannot be bridged |
| 2 | **D-2 — Protocol fee structure**: what fraction of each ticket goes to prizes, protocol, reserve, and burn | Sets π, f, g in the prize pool equation; all per-ticket EV figures depend on it |
| 3 | **D-3 — Bracket allocations**: which of the three candidate distributions governs prize split | Sets α; high-bracket concentration (SRC-017) vs frequency-balanced (SRC-005 proposal) vs PCS default produce qualitatively different expected per-ticket returns at small scale |
| 4 | **D-4 — Matching direction** (δ = L or R): which end of the ticket is compared first | Determines the formal definition of K(x, w, δ); affects implementation and the realized bracket distribution for non-uniform pickers |
| 5 | **D-5 — Injection model**: fixed schedule / dynamic shortfall / none | Determines the injection term I_t in the prize pool equation; the largest controllable cost driver in the baseline financial model |
