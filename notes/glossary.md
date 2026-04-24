# Glossary

## Purpose
Canonical vocabulary. For each core term, the definition is split across three columns:
- **PCS-baseline**: what PancakeSwap defines or does, sourced from SRC-013 and official docs
- **Team-target**: what the team's own product specifies (or "unresolved" if not yet decided)
- **Sim-assumption**: what the simulator assumes (may match PCS-baseline or be fictional)

Conflicts are flagged inline with their conflict ID.

---

## Core mechanics terms

---

### Ticket

| Context | Definition |
|---|---|
| **PCS-baseline** | A 6-digit number in the range 000000–999999, purchased by a player for one entry in a lottery round. Displayed as a sequence of 6 colored balls. Denomination: CAKE. |
| **Team-target** | Intended to be a 6-digit entry. Currency unresolved: SRC-018 states $5 USDT; SRC-005 uses $1; SRC-019 uses $2. **→ See C-003 (price), C-004 (currency).** |
| **Sim-assumption** | 6-digit entry. Price = $2.00 (default in `BaselineLotteryConfig`). Currency treated as generic USD-equivalent. |
| **Conflicts** | C-003 (ticket price), C-004 (currency) |

---

### Round

| Context | Definition |
|---|---|
| **PCS-baseline** | A single lottery cycle: ticket sales open, a winning number is drawn, prizes are paid, unawarded amounts roll over. PancakeSwap runs rounds on a fixed schedule (approximately daily or twice-daily; exact schedule to be verified against SRC-002). SRC-013 shows rounds are numbered sequentially (Round 1949). |
| **Team-target** | Not specified in team sources. Assumed to follow the same round structure as PCS. |
| **Sim-assumption** | One discrete time step in the simulation. The simulator runs 104 rounds per simulation path (representing ~2 years of rounds at ~1/day). Injection eligibility is determined per round by `weekly_injection_cycle`. |
| **Conflicts** | None. Round structure is uncontested. |

---

### Bracket

| Context | Definition |
|---|---|
| **PCS-baseline** | One of six mutually exclusive prize tiers. A ticket is in bracket k if exactly its first k digits match the winning number in the same order, and its (k+1)-th digit does not match. Bracket 6 = jackpot (all 6 match). Non-stacking: a ticket wins at most one bracket. Confirmed by SRC-013. |
| **Team-target** | Same structure assumed. Matching direction disputed: SRC-005/SRC-006/SRC-017 say right-to-left; PCS evidence says left-to-right. **→ See C-001.** Bracket allocations disputed: PCS = 2/3/5/10/20/40%; SRC-017 = 2/3/5/15/25/50%. **→ See C-002.** |
| **Sim-assumption** | Six brackets, left-to-right matching, allocations `[0.02, 0.03, 0.05, 0.10, 0.20, 0.40]`. Non-stacking. Implemented as exact-bracket hit using `EXACT_MATCH_PROBS`. |
| **Exact-bracket probabilities** | P(k) = 0.9 / 10^k for k = 1…5; P(6) = 10^−6. These are direction-agnostic and agreed across all sources. |
| **Conflicts** | C-001 (direction), C-002 (allocations for B4–B6) |

---

### Burn

| Context | Definition |
|---|---|
| **PCS-baseline** | 20% of the total pool (ticket revenue + injection) is destroyed — removed from token supply — each round. It is not a cash revenue item for the protocol. Confirmed by SRC-013: burn = 3,706 CAKE = 20% of 18,529 CAKE total. |
| **Team-target** | SRC-006 and SRC-018 mention "20% Treasury fee" but conflate burn with the project's operating cut. SRC-006 proposes splitting: 15% project + 5% Retention Reserve (no explicit burn). If the team uses USDT, the burn mechanic has no on-chain token-destruction meaning — it would be a fee or redistribution. **→ See C-004 (currency).** |
| **Sim-assumption** | `burn_rate = 0.20`. Applied to `fresh_pool = total_revenue + external_injection`, so burn consumes 20% of both ticket sales and injection. The simulator correctly excludes burn from treasury PnL. Whether burn applies to injections is unverified. **→ See C-005.** |
| **Conflicts** | C-004 (if currency is USDT, burn loses its token-sink meaning), C-005 (burn on injections) |

---

### Prize pool

| Context | Definition |
|---|---|
| **PCS-baseline** | The total fund available for prize distribution in a round. Equals: (ticket revenue + injection) × (1 − burn_rate) + carry from prior round. This is what is divided among the six brackets. SRC-013 example: ~$24,745 = 18,529 CAKE in Round 1949, which included significant rollover (38 players at any plausible ticket price cannot generate $24,745 from sales alone). |
| **Team-target** | Not explicitly defined. The term "pool" is used inconsistently across team sources — sometimes meaning gross ticket revenue, sometimes the prize sub-pool. **→ See "pool" in Ambiguous terms.** |
| **Sim-assumption** | `spendable_budget = spendable_from_fresh + carry_global` (under global rollover mode). `spendable_from_fresh = fresh_pool − burn`. The prize pool is then allocated across brackets by `rel_prize_weights`. |
| **Conflicts** | C-005 (burn on injections changes pool size), C-006 (rollover mode changes how carry enters the pool) |

---

### Rollover

| Context | Definition |
|---|---|
| **PCS-baseline** | When no ticket matches a given bracket in a round, the prize allocated to that bracket is not paid out. It is carried forward to the next round, increasing the prize pool. Exact carry mechanism (global vs per-bracket) not verified in-session against SRC-002/SRC-004. |
| **Team-target** | Not specified. Assumed to follow PCS convention. |
| **Sim-assumption** | Two modes implemented. Default: `rollover_mode = "global"` — all unhit bracket amounts merge into `carry_global`, which is redistributed proportionally across all brackets in the next round. Alternative: `rollover_mode = "same_bracket"` — each bracket's unhit amount carries only into that bracket. **→ See C-006.** |
| **Conflicts** | C-006 (rollover mode unverified against PCS) |

---

### Injection

| Context | Definition |
|---|---|
| **PCS-baseline** | Protocol-funded CAKE added to the prize pool from the PancakeSwap treasury, independent of ticket sales. Stated in simulator sources as 8,000 CAKE on injection rounds (4 of every 7 rounds). This schedule is not yet verified against official current docs (SRC-002/SRC-003). **→ See C-007.** |
| **Team-target** | The team uses "inject" to mean a budget allocation to artificially boost the prize pool. SRC-005 proposes replacing fixed injection with "Dynamic Inject" — a targeted top-up covering only the shortfall to guarantee minimum bracket-1/2 payouts. SRC-006 proposes injecting only into the jackpot bracket. The team's injection budget, schedule, and form are all unspecified. **→ See M-004.** |
| **Sim-assumption** | `injection_amount = 8000.0` CAKE. Cycle `[1, 0, 1, 0, 1, 0, 1]` per 7-round week = 4 injections/week. `burn_applies_to_injections = True` (burn deducted from injection before it enters prize pool). **→ See C-005, C-007.** |
| **Conflicts** | C-005 (burn on injection), C-007 (amount and schedule unverified) |

---

### Treasury cost

| Context | Definition |
|---|---|
| **PCS-baseline** | The direct financial cost to the protocol treasury per round = injection amount (CAKE) + any other funded subsidies. The 20% burn is NOT treasury cost — it is a token-supply reduction and does not represent cash outflow from treasury. |
| **Team-target** | Not precisely defined. SRC-018 mentions "15% team + 5% reserve" from each ticket sale. If the team's product charges 20% of revenue as protocol fees instead of burning, the "treasury" is revenue (15%) plus a reserve (5%). Whether injections are an additional cost is unspecified. |
| **Sim-assumption** | `treasury_feature_cost` per round = `baseline_injection + jackpot_boost + direct feature cash costs` (cashback, loss rebates, referrals, multiplier top-ups). Burn is tracked separately. The simulator's economic viability metric is `incremental_unit_margin_ex_burn = total_revenue − treasury_cost`. |
| **Conflicts** | C-004 (currency), C-005 (burn treatment), C-007 (injection amount) |

---

### Protocol PnL

| Context | Definition |
|---|---|
| **PCS-baseline** | PancakeSwap's lottery is designed to return 80% of pool to prizes and burn 20%. The protocol has no retained cash margin from ticket sales — its benefit is the token burn (deflationary pressure on CAKE). External injections are a cost, not a revenue source. The lottery is structurally a zero-margin product with an injection subsidy and a burn mechanic. |
| **Team-target** | Undefined. If the team charges 15% fee (SRC-018) and uses USDT, the lottery becomes a positive-margin product (15% of ticket revenue as cash), with injection as a promotional cost. This is a fundamentally different economic structure from PCS. |
| **Sim-assumption** | Uses `incremental_unit_margin_ex_burn = total_revenue − (injection + jackpot_boost + feature_cash_costs)` as the economic viability measure. In the baseline scenario, this is positive (revenue > injection) — but only because the simulator's ticket volume (~10,605/round × $2 = ~$21,210 revenue) substantially exceeds the injection (~$4,538/round at 4 of 7 rounds). At real PancakeSwap scale (38 players), revenue would be much lower and injection would dominate. |
| **Key distinction** | Burn ≠ revenue. Any analysis that treats burn as treasury income is wrong. This is correctly implemented in the simulator. |
| **Conflicts** | C-004 (currency determines whether burn is meaningful), C-008 (scale determines whether revenue > injection) |

---

## Proposed / non-baseline terms

These are mentioned in team-target sources only. Not in PCS-baseline. Not implemented in the simulator unless noted.

| Term | Synonyms | Definition | Source |
|---|---|---|---|
| Roll-Down (Waterfall) | "Водопад" | If jackpot unawarded, a portion of its allocation cascades to lower brackets in the same round rather than rolling over. | SRC-006 |
| Dynamic Inject | "Субсидирование гарантий", "targeted inject" | Injection covers only the shortfall needed to guarantee a minimum payout multiplier for brackets 1–2 per round. No fixed schedule. | SRC-005 |
| Pity timer | "Pity-таймер", "free spin" | After N consecutive losing rounds per user, a free ticket is issued from the Retention Reserve. | SRC-006 |
| LUCK token | "Dust", "Осколки" | Soulbound in-game token accruing from losing tickets. Redeemable for free tickets, insurance, or multipliers. | SRC-006 |
| Syndicate | "Синдикат", "Совместный пул" | Group-play smart contract: multiple wallets pool to buy a ticket batch; winnings split by contribution. Minimum 3 unique wallets. | SRC-006, SRC-018 |
| Box matching | "Дробовик (Box)" | Win if ticket digits appear in the winning number in any order. Proposed bitmask implementation in Solidity. | SRC-006 |
| Lotto Points / XP | "XP", "поинты" | Loyalty points: 1 ticket = 100 XP; redeemable for free tickets at defined tier thresholds. | SRC-018 |
| Reserve fund (losers) | "Резервный фонд", "Retention Reserve" | 5% of each ticket → separate contract; paid monthly to qualifying losing users who meet activity thresholds. | SRC-006, SRC-018 |
| Golden Link | — | 3-tier referral program: 5% (basic), 10% (ambassador), 20–25% (KOL). Paid in USDT. Funding source unspecified. | SRC-018 |
| Self-buy | "самовыкуп" | Protocol buys tickets in its own lottery. R&D.md (SRC-005) argues this is economically useless: it dilutes per-winner payouts proportionally. Not modeled in simulator. | SRC-005 |
| Entropy (model) | — | Sim parameter (0–1) per segment: 1.0 = uniform random picks; lower = clustered manual picks. Heuristic; not calibrated. | SRC-019 |
| Segment | "casual / repeat / whales" | Sim population groups with different participation rates and ticket volumes. All values are fictional. | SRC-019 |

---

## Ambiguous terms

Terms whose meaning differs by source and must be pinned before formalization.

| Term | Ambiguity | Resolution needed |
|---|---|---|
| "pool" | (a) gross ticket revenue; (b) prize sub-pool = 80% of revenue; (c) total including injection. SRC-005 and SRC-014 use (a). SRC-013 and SRC-019 align with (c) minus burn = prize pool. | Pin before writing problem_statement_math. **Canonical choice: "prize pool" = (revenue + injection) × (1 − burn_rate) + carry.** |
| "inject" | (a) PCS protocol injection (8,000 CAKE / schedule); (b) team's own promotional budget; (c) Dynamic Inject (targeted shortfall subsidy). | Distinguish by context. Team's injection budget unspecified → C-007, M-004. |
| "treasury" | (a) the 20% burn (incorrect usage); (b) protocol operating budget funded by fees; (c) both. SRC-005 conflates burn and treasury in some arguments. | Canonical: treasury ≠ burn. Burn = token sink. Treasury = protocol operational cash. |
| Currency | CAKE (PCS), generic "$" (sim), USDT (SRC-018). | Critical unresolved question. **→ See C-004, Q-002.** |
