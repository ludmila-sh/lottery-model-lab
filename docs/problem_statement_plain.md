# Problem Statement — Plain Language

## Status
**Draft. Dual-baseline version.** The team has not yet committed to a canonical baseline. This document presents both known baselines in parallel and marks every place where a choice must be made before the statement can be collapsed to a single model.

---

## What is the system

A fixed-format lottery operating in discrete rounds. In each round:

1. Players purchase tickets. Each ticket is a 6-digit number, each digit independently chosen from {0, …, 9}.
2. A winning number — also a 6-digit sequence — is drawn at random.
3. Each ticket is assigned to exactly one prize bracket (or to no bracket) based on how many of its digits match the winning number in a fixed direction, starting from one end. The number of consecutive matching digits from that end determines the bracket level, from 1 (one match) to 6 (jackpot — all digits match). A ticket can win at most one bracket. These brackets are mutually exclusive and non-stacking.
4. The prize pool for that round is divided among bracket winners. Each bracket's pool is shared equally among all tickets in that bracket.
5. If no ticket wins a given bracket, that bracket's allocated pool is not paid out. It carries forward and enlarges the prize pool in the next round.
6. After paying prizes, a portion of the pool is either destroyed (burn, in the token baseline) or redirected to protocol accounts (fee, in the cash-margin baseline).

The process repeats indefinitely. Over time, bracket 6 (jackpot) accumulates because a full 6-digit match is extremely rare at low player counts. The expected number of rounds before the jackpot is first won depends on how many tickets are sold per round.

---

## What is known with confidence

**About the PancakeSwap (PCS) baseline, from direct product observation:**
- 6 digits per ticket, each from {0, …, 9}. Confirmed.
- Matching is left-to-right: "Match first N." Confirmed by UI (Round 1949, Apr 2026).
- Bracket allocations: 2% / 3% / 5% / 10% / 20% / 40% of prize pool. Confirmed by Round 1949 arithmetic.
- Burn rate: 20% of the total pool (ticket revenue + injection). Confirmed.
- The protocol retains zero cash from ticket sales. The economic benefit to the protocol is token deflation.
- In Round 1949: 38 total players, prize pot ~$24,745 (18,529 CAKE). The prize pot was heavily inflated by prior rollover and injection — 38 players at any reasonable ticket price cannot generate $24,745 organically.

**About the probability structure, from the underlying math:**
- Exact-bracket probabilities are: P(1) = 9%, P(2) = 0.9%, P(3) = 0.09%, P(4) = 0.009%, P(5) = 0.0009%, P(6) = 0.0001%. These hold under either matching direction (left-to-right or right-to-left) as long as both the ticket and the winning number are drawn uniformly.
- At the observed scale (38 players buying a handful of tickets each), brackets 4, 5, and 6 will almost never be won organically. Their prize pools accumulate indefinitely via rollover.
- When no player wins bracket 6, the 40% jackpot allocation rolls forward, compounding over many rounds. The jackpot can grow large relative to organic ticket revenue.

---

## What is unknown or unresolved

Three types of unknowns exist and must be distinguished.

**Type 1 — Factual gaps about PCS that can be resolved by reading the official docs:**
- Exact ticket price in CAKE
- Whether the 20% burn applies to injections as well as ticket revenue
- Whether rollover is global (all unhit amounts merge) or per-bracket (each bracket carries separately)
- Exact injection amount and weekly schedule
- Claim window: how long winners have to collect, and what happens to unclaimed prizes

**Type 2 — Unresolved decisions about the team's own product:**
- Whether the product uses a token (like PCS) or a stablecoin (e.g., USDT). This is the most consequential open question — it determines the entire economic structure.
- Ticket price. Three conflicting values exist across team sources: $1, $2, $5 USDT.
- Bracket allocations for the team's product. At least three candidate distributions exist.
- Matching direction for the team's product (though PCS confirms left-to-right, team notes say right-to-left in several places).
- Injection model: fixed schedule, dynamic shortfall subsidy, or none.
- Fee structure: how is the non-prize portion of each ticket sale split?

**Type 3 — Empirical gaps that require real data to fill:**
- Target player count and ticket volume at launch and at scale. The simulator assumes ~10,000 tickets per round; the observed PCS round had 38 players. The economic dynamics are qualitatively different at these two scales.
- Whether pick distributions are approximately uniform or clustered (affects which brackets are actually won).
- Actual claim rates (the simulator assumes 100%).

---

## What we want to understand

The core question is:

> *Can this lottery be made economically self-sustaining, or attractive enough to players that the team's cost of subsidizing it (via injections or features) is offset by the value it generates — without the lottery becoming structurally loss-making over time?*

More specifically, we want to answer:

1. **Sustainability of the baseline**: Under realistic player volume and behavior, does the baseline lottery — without any features — generate enough ticket revenue to keep the prize pool attractive, or does it require indefinite subsidy?

2. **Per-bracket viability at scale**: At what player count does each bracket pay out in a meaningful fraction of rounds? Below this threshold, high-bracket prizes are frozen in rollover and provide no player value.

3. **Feature economics**: For each proposed retention feature (free tickets, cashback, rollover modifications, reserve funds, referral rewards), under what conditions does the incremental increase in ticket sales offset the incremental cost of the feature? What is the probability and magnitude of downside if the assumed player response does not materialize?

4. **Tail risk**: What is the worst-case cumulative economic loss over a planning horizon (e.g., 50 or 100 rounds) for each proposed configuration? Under which configurations does the probability of cumulative loss remain below an acceptable threshold?

5. **Comparative baseline economics**: How do the PCS-baseline and team-target baseline differ in their structural viability — not just in parameter values, but in the economic logic of the system?

---

## Two candidate baselines

These are presented in parallel. They must not be collapsed until the team makes the decisions in Section 7.

### Baseline A — PCS official

The lottery as PancakeSwap currently operates it.

- Currency: CAKE (volatile token)
- Ticket price: unverified (~1–5 CAKE; to be confirmed from official docs)
- Prize pool fraction: 80% of (ticket revenue + injection)
- Burn: 20% of (ticket revenue + injection), removed from token supply
- Protocol cash revenue: zero
- Bracket allocations: 2 / 3 / 5 / 10 / 20 / 40% of prize pool
- Matching direction: left-to-right
- Injection: ~8,000 CAKE on ~4 of every 7 rounds [to be verified]
- Rollover: unhit brackets carry forward [mode unverified]
- Observed scale: ~38 players per round (one observation; may not be typical)
- Protocol economic logic: token deflation. The lottery destroys CAKE. The protocol benefits through token appreciation or scarcity, not through retained cash.

### Baseline B — Team-target product

What the team intends to build. Parameters are partially specified and internally inconsistent across sources.

- Currency: **unresolved** — SRC-018 uses USDT throughout; other sources use CAKE or generic "$"
- Ticket price: **unresolved** — three conflicting values ($1, $2, $5 USDT)
- Prize pool fraction: **unresolved** — if USDT: possibly 70% (SRC-018); if token with burn: possibly 80% or modified
- Burn: **unresolved** — may be absent if USDT; if token, rate unspecified
- Protocol cash revenue: **unresolved** — SRC-018 implies 15% of ticket revenue; other sources unclear
- Bracket allocations: **unresolved** — three candidate sets (PCS 2/3/5/10/20/40%; diagram 2/3/5/15/25/50%; proposed 15/10/10/15/20/30%)
- Matching direction: **unresolved** — PCS convention (L→R) conflicts with team notes (R→L)
- Injection model: **unresolved** — fixed schedule, dynamic shortfall subsidy, or none
- Rollover mode: **unresolved**
- Target player count: **unspecified**
- Additional fee layers proposed in team sources: referral (5–25%), losers reserve (5%), XP/loyalty system

The most structurally significant open question is whether the team's product has a burn mechanic (implying a token-based design) or a cash-margin structure (implying a stablecoin-based design). These two paths lead to different economic models, not merely different parameter values.

---

## Where there is no canonical choice yet

The following five structural choices have not been made. Until they are, no single formal model can be written:

| Decision | Choices |
|---|---|
| **D-1**: Currency and economic model class | Token (burn-based, like PCS) vs stablecoin (cash-margin) |
| **D-2**: Protocol fee structure | Inherit PCS 80/20 burn vs custom split (e.g., 70/15/5 cash + reserve) |
| **D-3**: Bracket allocations | PCS 2/3/5/10/20/40% vs diagram 2/3/5/15/25/50% vs proposed 15/10/10/15/20/30% |
| **D-4**: Matching direction | Left-to-right (PCS) vs right-to-left (team notes) |
| **D-5**: Injection model | Fixed schedule vs dynamic shortfall subsidy vs none |

D-1 is prior to all others. If D-1 = token, then the PCS baseline applies with specific parameter overrides for D-2 through D-5. If D-1 = stablecoin, the PCS economic machinery does not apply and the team-target baseline must be fully re-specified.

---

## Scope

**Included in the analysis:**
- Baseline lottery mechanics (ticket structure, brackets, prize pool, rollover, burn/fee)
- Economic viability of the baseline and feature variants over a multi-round horizon
- Per-ticket expected value under each bracket allocation
- Probability and severity of cumulative financial loss

**Excluded (for now):**
- Smart-contract implementation details (gas costs, EVM specifics)
- Regulatory or legal analysis
- Token price modeling (CAKE price trajectory)
- Detailed player acquisition and churn dynamics

---

## Assumptions (explicitly labeled)

- **[A-1]** The winning number is drawn uniformly at random from {000000–999999} each round, independently of all prior rounds and of ticket choices.
- **[A-2]** Ticket picks are approximately uniform for random pickers. Manual pickers create clustering, which reduces effective bracket coverage but does not change the probability formulas per ticket.
- **[A-3]** Rounds are independent conditional on player count: the number of players does not depend on prior round outcomes (no modeled churn or streak effects at baseline).
- **[A-4]** All prize winners claim their prizes (claim rate = 100%). This assumption affects long-run carry dynamics and must be revisited if claim rates are low.
- **[A-5]** Matching direction determines which end of the ticket is compared first. It does not change the probability of winning each bracket but does change which specific digit combinations qualify, and therefore affects the experience of manual pickers who choose "meaningful" numbers.

---

## Open questions inherited from contradictions register

- C-001: Matching direction (team notes vs PCS UI)
- C-002: Bracket allocations B4–B6 (three candidate sets)
- C-003: Ticket price (three conflicting values)
- C-004: Currency (CAKE vs USDT)
- C-005: Burn on injections (PCS unverified)
- C-006: Rollover mode (PCS unverified)
- C-007: Injection amount and schedule (sim assumption, unverified)
- C-008: Player scale (sim ~10,600/round vs observed 38/round)
