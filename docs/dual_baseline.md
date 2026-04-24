# Dual-Baseline Problem Framing

## Purpose
Present two parallel baseline specifications — one fully known, one partially known — without collapsing them into a single model. Identify the minimum explicit decisions the team must make to resolve which baseline governs the formal model, or to define the axes on which the two baselines should be compared.

This document is a pre-formalization step. It does not finalize problem_statement_plain.md.

## Inputs
- canonical classification: INPUT_SOURCES.md (2026-04-24)
- confirmed conflicts: notes/contradictions.md (C-001 through C-008)
- canonical vocabulary: notes/glossary.md
- open blocking questions: docs/open_questions.md (Q-001 through Q-010)

---

## Baseline A — Official PancakeSwap (PCS)

### What is confirmed

All items below are confirmed by at least one primary-source observation (SRC-013, Round 1949, Apr 2, 2026) or internally consistent arithmetic. Items flagged `[verify]` need cross-checking against official current docs (SRC-001–SRC-004) but are not contradicted by anything in the dataset.

**Structure:**
- Ticket: a 6-digit number, each digit independently drawn from {0, …, 9}. Total combinatorial space: 10^6 = 1,000,000.
- Round: one lottery cycle. A winning number is drawn uniformly at random. Prizes are paid. Unhit amounts roll forward.
- Brackets: six, mutually exclusive, non-stacking. A ticket is in bracket k if its first k digits match the winning number left-to-right, and its (k+1)-th digit does not. Bracket 6 = all 6 match (jackpot).

**Probability per ticket (exact-bracket):**
```
P(bracket 1) = 0.9 / 10   = 0.09
P(bracket 2) = 0.9 / 10²  = 0.009
P(bracket 3) = 0.9 / 10³  = 0.0009
P(bracket 4) = 0.9 / 10⁴  = 0.00009
P(bracket 5) = 0.9 / 10⁵  = 0.000009
P(bracket 6) = 1   / 10⁶  = 0.000001
```
These are confirmed by the simulator validation (SRC-011) and implied by the non-stacking exact-bracket design.

**Pool and fee structure** (confirmed from Round 1949 arithmetic):
```
total_pool  = ticket_revenue + injection
burn        = 0.20 × total_pool
prize_pool  = 0.80 × total_pool + carry_from_prior_round
```
Bracket allocation of prize_pool (confirmed, exact to 4 sig figs from Round 1949 data):
```
bracket 1: 2%    bracket 4: 10%
bracket 2: 3%    bracket 5: 20%
bracket 3: 5%    bracket 6: 40%
```
Sum = 80% of prize_pool (which is itself 80% of total_pool — see "pool" note below).
Burn = 20%. No cash retained by protocol from ticket sales.

**Pool arithmetic note:** The bracket percentages apply to the prize_pool, which is already 80% of total_pool. So brackets collectively receive 100% of prize_pool = 80% of total_pool. Burn gets the remaining 20%. The protocol retains 0% as cash.

**Injection** [verify against SRC-002/SRC-003]:
- 8,000 CAKE injected on a subset of rounds following a weekly cycle
- Cycle appears to be [1,0,1,0,1,0,1] per 7 rounds → 4 injection rounds per week
- Whether the 20% burn applies to the injected amount is unverified

**Currency:** CAKE (volatile token denominated on BNB Chain).

**Protocol PnL model:** The protocol does not extract cash from ticket sales. Its economic benefit is the deflationary effect of burning 20% of CAKE per round. Injection is a cost from the CAKE treasury.

**Observable scale (one round):**
- Round 1949: 38 total players, prize pot ~$24,745 (18,529 CAKE at ~$1.34/CAKE)
- The prize pot far exceeds what 38 players could generate from sales alone — the majority came from rollover and injection

**Rollover mode** [verify against SRC-002/SRC-004]:
- Confirmed: unhit brackets roll forward
- Mode (global vs per-bracket) not verified in-session

### What remains unverified for PCS

| Item | Why unverified | Source to check |
|---|---|---|
| Ticket price in CAKE | Not stated in Round 1949 screenshot | SRC-002, SRC-004 |
| Injection amount (8,000 CAKE) and exact schedule | From simulator README only | SRC-002, SRC-003 |
| Whether burn applies to injections | Simulator choice, not confirmed | SRC-003 |
| Rollover mode (global vs per-bracket) | Not stated in any source | SRC-002, SRC-004 |
| Round frequency (daily / twice-daily) | Not confirmed | SRC-002 |
| Claim window and unclaim behavior | Not in any source | SRC-002 |

---

## Baseline B — Team-Target Product

### What is partially specified

The team's own product is incompletely specified across multiple conflicting sources. The most specific source is Retention_Team_comments.md (SRC-018). Where sources conflict, the conflict ID is cited.

**Structure (agreed):**
- 6-digit tickets, digits 0–9 (consistent across all team sources)
- Round structure: matches PCS (assumed, not contradicted)
- 6 non-stacking prize brackets (assumed)

**Structure (disputed):**
- Matching direction: right-to-left in SRC-005/SRC-006/SRC-017; left-to-right in PCS and simulator. **→ C-001**
- Bracket allocations: three candidate sets exist. **→ C-002**

**Candidate bracket allocation sets:**

| Bracket | PCS (confirmed) | SRC-017 (diagram) | SRC-005 (proposed) |
|---|---|---|---|
| 1 | 2% | 2% | 15% |
| 2 | 3% | 3% | 10% |
| 3 | 5% | 5% | 10% |
| 4 | 10% | 15% | 15% |
| 5 | 20% | 25% | 20% |
| 6 | 40% | 50% | 30% |
| **Sum** | **80%** | **100%** | **100%** |
| Applied to | prize_pool | unknown base | prize_pool |

Note: SRC-017 percentages sum to 100% while PCS's sum to 80% (with burn taking the remaining 20%). Either the SRC-017 diagram uses a different pool base, or it describes a product with no burn. This is unresolved.

**Fee and pool structure (most specific from SRC-018):**
```
Per ticket revenue ($5 USDT):
  70% → prize pool
  15% → team (cash revenue)
   5% → losers reserve fund (separate contract)
  10% → referrer (when referral is active)
  ─────
  100%
```
This split applies per ticket when a referral is active. Without referral, the destination of the 10% is unspecified.

**Critical differences from PCS fee structure:**
- Prize pool is 70% of revenue, not 80%
- Team extracts 15% cash per ticket (PCS extracts 0%)
- There is no burn (no token-destruction mechanic)
- There is no injection from a token treasury (injection, if any, is a USDT promotional expense)
- A separate 5% reserve fund exists for loss compensation

**Currency:** USDT (SRC-018 is explicit throughout). **→ C-004**

**Ticket price:** $5 USDT (SRC-018). Conflicts with $1 (SRC-005, SRC-014) and $2 (SRC-019). **→ C-003**

**Injection:** Budget, schedule, and form are unspecified. SRC-005 proposes "Dynamic Inject" (targeted shortfall subsidy). SRC-006 proposes jackpot-only injection. No fixed amount exists in team sources.

**Rollover:** Assumed yes, mode unspecified.

**Scale:** Not stated in any team source.

**Proposed retention features** (not in either baseline; for later phases):
Roll-Down, pity timer, XP tiers, Syndicate, LUCK token, risk-level choice, referral program. Each has separate documentation in SRC-005, SRC-006, SRC-018.

---

## Structural comparison

| Dimension | Baseline A (PCS) | Baseline B (Team-target) |
|---|---|---|
| **Currency** | CAKE (volatile, on-chain token) | USDT (stablecoin) |
| **Ticket price** | Unknown (unverified from docs) | $5 USDT (SRC-018) — disputed |
| **Prize pool fraction** | 80% of (revenue + injection) | 70% of revenue (SRC-018) — burn absent |
| **Protocol cash revenue** | 0% (burn only) | 15% of revenue per ticket |
| **Burn** | 20% of total pool — token destruction | None defined |
| **Referral cost** | None | 10% per ticket when referral active |
| **Losers reserve** | None | 5% per ticket |
| **Injection form** | Fixed CAKE amount on schedule | Undefined (SRC-005: dynamic; SRC-006: jackpot-only) |
| **Injection burn** | Unverified (sim: yes) | N/A — no burn mechanic |
| **Bracket allocations** | 2/3/5/10/20/40% (confirmed) | Three candidates (disputed) |
| **Matching direction** | Left-to-right (confirmed) | Disputed (C-001) |
| **Rollover mode** | Unverified (sim: global) | Unspecified |
| **Observed scale** | 38 players/round | Not specified |
| **Protocol PnL** | Token deflation (CAKE burn) | Cash margin (15%/ticket) |
| **Economic model class** | Token-subsidized, zero-cash-margin | Cash-positive fiat lottery |

---

## The critical structural divergence

The comparison above is not merely a table of different parameter values. It reveals a **model-class split**.

**PCS is a token-burn lottery.** The protocol generates no retained cash. Its economic purpose is CAKE deflation: 20% of all pool value is destroyed each round. External injection subsidizes prize attractiveness. The lottery is structurally zero-margin in cash terms — it runs at a loss in cash (injection outflows) and a gain in tokenomic terms (burn inflows). This model cannot be evaluated by standard cash-margin analysis.

**The team-target product (from SRC-018) is a fiat-margin lottery.** The protocol generates 15% cash per ticket. There is no burn mechanic. The structural question is whether the 15% cash margin can fund injections and retention features while remaining profitable. This model is evaluable by standard unit economics.

**This difference cannot be resolved by setting parameter values.** It requires a categorical decision: which economic model is the team building?

If the answer is "fiat-margin lottery (USDT)," the entire PCS token-economic machinery — burn, CAKE treasury, CAKE price exposure — is irrelevant to the team's baseline. The correct reference class is a stablecoin prize game with fixed payout fractions and a cash-positive protocol fee.

If the answer is "token lottery (CAKE or equivalent)," the PCS mechanics apply with parameter overrides, and the burn mechanic is a load-bearing part of the economics.

---

## Minimum decision set

The following decisions are the minimum required to collapse Baseline A and Baseline B into a single canonical model, or to fix the axes of a formal comparison. They are ordered by dependency: later decisions depend on earlier ones.

Each decision is presented as a set of mutually exclusive choices, not as open questions.

---

### D-1 — Economic model class

**The first and prior decision. All others depend on it.**

| Choice | Description | Consequence |
|---|---|---|
| **D-1A — Token lottery** | The team's product uses a native or borrowed token (CAKE or other). Burn is the primary protocol economic benefit. | PCS mechanics apply as the starting point. D-2 becomes: which parameters to override. |
| **D-1B — Fiat-margin lottery** | The team's product uses USDT. Burn does not apply. Protocol extracts a cash percentage of each ticket. | PCS is only a structural template. Injection, burn, and treasury must be re-specified from scratch. |

*Current evidence favors D-1B: SRC-018 (most specific team source) uses USDT explicitly throughout.*

---

### D-2 — Protocol fee structure

Depends on D-1.

**If D-1A (token):**

| Choice | Description |
|---|---|
| **D-2A** | Inherit PCS: 80% prize pool, 20% burn. No retained cash. |
| **D-2B** | Modify burn rate (e.g., 15% burn + 5% reserve, as partially suggested in SRC-006). |

**If D-1B (fiat):**

| Choice | Description |
|---|---|
| **D-2C** | SRC-018 split: 70% prize pool / 15% team / 5% reserve / 10% referral when active |
| **D-2D** | PCS-style 80/20 applied as a fiat fee: 80% prize pool, 20% protocol fee (no burn). |
| **D-2E** | Custom split — must be stated explicitly. |

*SRC-018 implies D-2C is the team's current working assumption. This must be confirmed.*

---

### D-3 — Bracket allocations

Can be decided independently of D-1/D-2 once the pool base is fixed.

| Choice | Source | Economic character |
|---|---|---|
| **D-3A — PCS** | 2/3/5/10/20/40% of prize pool | Jackpot-concentrated; at low player counts, 70% of prize pool sits in brackets 4–6 which are rarely won |
| **D-3B — SRC-017** | 2/3/5/15/25/50% of unknown base | Even more jackpot-concentrated; brackets 4–6 together = 90% |
| **D-3C — SRC-005 proposal** | 15/10/10/15/20/30% of prize pool | Frequency-balanced; brackets 1–3 together = 35% instead of PCS's 10%; frequent small wins |

*D-3C is the most different from PCS. It is a design choice, not a fact claim. D-3A and D-3B look similar but D-3B further concentrates value in the jackpot.*

---

### D-4 — Matching direction

| Choice | Description | Implementation note |
|---|---|---|
| **D-4A — Left-to-right** | Match the first N digits of the winning number. "Match first N." PCS convention. | Confirmed by PCS UI; simulator implements this. |
| **D-4B — Right-to-left** | Match the last N digits. "Совпала последняя цифра." Stated in team notes. | Probability model unchanged; Solidity implementation differs. |

*This decision has zero effect on probability math. It is a UX and implementation choice. It can be made last.*

---

### D-5 — Injection model

| Choice | Description | Economic character |
|---|---|---|
| **D-5A — Fixed schedule (PCS-style)** | A fixed amount injected every N rounds from a pre-committed budget. Predictable cost. | Treasury cost is deterministic per round. May be wasted when few players participate. |
| **D-5B — Dynamic inject** | Only injects the shortfall needed to guarantee a minimum payout for brackets 1–2 each round. | Treasury cost scales with player count and outcome; zero waste in high-volume rounds. Harder to budget. |
| **D-5C — No injection** | Prize pool funded solely by ticket revenue + rollover. | Pure self-funding. At low player counts, high brackets never pay out; rollover dominates. |

*D-5 cannot be resolved until D-2 is fixed (to know whether injection is CAKE or USDT) and the team has stated a promotional budget.*

---

### Summary: decision ordering

```
D-1 (model class: token vs fiat)
  └─► D-2 (fee structure: how is the non-prize portion split)
        └─► D-5 (injection: fixed / dynamic / none, and how much)
D-3 (bracket allocations: which set)   ← can be decided in parallel with D-1/D-2
D-4 (matching direction)               ← can be decided last; no math consequence
```

Until D-1 is answered, no mathematical formulation is possible because the core economic structure — what the protocol is maximizing, what "burn" means, how injection is costed — is undefined.

Until D-3 is answered, no prize-pool distribution model can be written.

Until D-5 is answered, no baseline round-level financial model can be written.

D-4 can be deferred until smart-contract specification.
