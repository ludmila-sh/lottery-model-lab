# Open Questions

## Purpose
Minimum set of questions that must be answered before the canonical baseline for the team's own product can be fixed. Until these are answered, problem_statement_plain.md and problem_statement_math.md must not be finalized.

Questions are in three tiers:

- **Tier 1 — Baseline-blocking.** Answer required before any formal spec can be written. Unresolved = no canonical baseline.
- **Tier 2 — Formalization-blocking.** Answer required before the mathematical formulation can be written. Does not block plain-language description.
- **Tier 3 — Deferred.** Relevant to feature design and validation but do not block the baseline specification.

---

## Tier 1 — Baseline-blocking (7 questions)

| ID | Question | Conflict resolved | Why it cannot be deferred |
|---|---|---|---|
| Q-001 | Is the team's product a PancakeSwap fork, or an independent lottery that uses PancakeSwap only as inspiration? | M-001 | Determines whether PCS mechanics apply by default or must be re-specified from scratch. Every other question depends on this answer. |
| Q-002 | What is the ticket price and denomination? ($1 / $2 / $5 USDT / other) | C-003 | Three conflicting values exist. All per-ticket EV, all scenario margins, and all subsidy calculations depend on it. |
| Q-003 | What currency does the team's product use? (CAKE / USDT / other stablecoin) | C-004 | Determines whether "burn" has meaning as a token-sink or is simply a fee deduction. Determines whether injection is a CAKE treasury cost or a USDT spend. Changes the entire economic framing. |
| Q-004 | What are the bracket allocations for the team's product? (PCS 2/3/5/10/20/40% or different?) | C-002, M-005 | SRC-017 shows a different allocation (2/3/5/15/25/50%). SRC-005 proposes yet another. This is the primary prize-pool distribution parameter. |
| Q-005 | What is the matching direction for the team's product — left-to-right or right-to-left? | C-001, M-006 | Affects smart-contract specification and UX. The probability model is direction-agnostic, but the implementation and description are not. |
| Q-006 | What is the team's injection budget and schedule? (PCS 8,000 CAKE / 4-of-7 rounds, or something different?) | C-007, M-004 | Injection is the single largest cost component in the baseline. If the team sets a different amount or frequency, every scenario margin changes. |
| Q-007 | Does burn apply to injections? (Is 20% of the injected amount burned before entering the prize pool?) | C-005, M-008 | A 20% error on every injection. If burn does not apply to injections, the simulator baseline treasury cost is overstated and all scenario comparisons shift. |

---

## Tier 2 — Formalization-blocking (3 questions)

These do not block the plain-language problem statement but block the mathematical formulation.

| ID | Question | Conflict resolved | Why it matters for math |
|---|---|---|---|
| Q-008 | What is the rollover mode — global (all unhit amounts pool together) or per-bracket (each bracket accumulates separately)? | C-006, M-007 | The carry-forward term in the prize pool equation differs. Under global rollover, the prize pool grows uniformly; under per-bracket, jackpot accumulates independently. The stochastic process for jackpot size is different in each case. |
| Q-009 | What is the claim window, and what happens to unclaimed prizes? | — | Determines whether unclaimed prizes re-enter the carry or are forfeited. The simulator assumes 100% claim rate. If claim rate is lower, prize pool carry dynamics and effective payout rate both change. |
| Q-010 | What does diagram SRC-017 represent — a draft baseline, a proposed variant, or a separate product? | C-002 | If SRC-017 describes the team's intended baseline (not PCS), the bracket allocations in the formal model must use its values. If it is a proposed variant, it belongs only in hypotheses. |

---

## Tier 3 — Deferred (feature design and calibration)

These questions matter for scenario analysis and feature design but do not block the canonical baseline specification.

| ID | Question | Blocks |
|---|---|---|
| Q-011 | What is the target active-user count and ticket volume per round at launch vs at scale? | All scenario calibration; the R&D.md "dead money" critique applies at <100 players/round but not at 10,000+. |
| Q-012 | For the referral program (SRC-018 "Golden Link"), what is the funding source for the 5–25% referral payments? | Unit economics of referral feature scenarios. |
| Q-013 | Is the "10% pool for losers" in handwritten note SRC-014 an intended feature or arithmetic scratch? | Whether to include it in feature hypothesis list. |
| Q-014 | What is the current CAKE ticket price in USD? | Translation of CAKE-denominated PCS benchmarks into USD-comparable figures. |
| Q-015 | Has PancakeSwap changed injection amount or bracket allocations since the official docs were last verified? | Baseline calibration against current PCS state; Round 1949 data (Apr 2, 2026) confirms allocations but not the injection schedule. |

---

## Decision gate

**Before writing problem_statement_plain.md:** Q-001 through Q-005 must be answered.
**Before writing problem_statement_math.md:** Q-001 through Q-010 must be answered.
**Before writing hypotheses.md:** All Tier 1 and Tier 2 questions must be answered.
