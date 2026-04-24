# Contradictions

## Purpose
Explicit register of conflicts between sources. Organized by the layer where the conflict lives.
Nothing is smoothed over. Each conflict must be resolved or explicitly carried as an open assumption before any formal artifact is finalized.

Classification shorthand used throughout:
- **PCS** = official PancakeSwap baseline (SRC-001–SRC-004, SRC-013)
- **team** = team-target product (SRC-005, SRC-006, SRC-014, SRC-017, SRC-018)
- **sim** = simulator assumptions (SRC-019 and derived outputs)

---

## Section 1 — Conflicts between PCS-baseline and team-target sources

These conflicts block the choice of canonical baseline for the team's own product.

---

### C-001 — Matching direction

| | |
|---|---|
| **PCS position** | Left-to-right. UI (SRC-013, Round 1949) displays "Match first 1 / Match first 2 / Match first 3 ...". Instruction text: "Match the winning number in the same order to share prizes." The winning number is read left-to-right. |
| **Team position** | Right-to-left. R&D.md (SRC-005) writes "Совпала последняя цифра" (last digit matched). Щедрая_лотерея.md (SRC-006) labels this direction "Классика (Справа налево)". Diagram SRC-017 is labeled "Match digits right-to-left". |
| **Math consequence** | The exact-bracket probability values are identical regardless of direction (0.9/10^k). The conflict affects UX description, smart-contract implementation, and which end of a 6-digit ticket is compared first — not the probability model. |
| **Status** | Open. PCS evidence is stronger (primary product observation). Team intent is unclear: the team may be adopting PCS direction without realizing the inconsistency in their notes, or may be intentionally choosing right-to-left for their own product. |
| **Blocks** | problem_statement_plain, smart-contract spec, any UI description |

---

### C-002 — Bracket allocations for brackets 4–6

| | |
|---|---|
| **PCS position** | Bracket 4 = 10%, Bracket 5 = 20%, Bracket 6 = 40%. Confirmed by SRC-013 arithmetic: 1853/18529 ≈ 10.0%, 3706/18529 ≈ 20.0%, 7411/18529 ≈ 40.0%. Brackets 1–3 = 2/3/5% (same in all sources). |
| **Team position (SRC-017)** | Bracket 4 = 15%, Bracket 5 = 25%, Bracket 6 = 50%. Source is the unregistered diagram. Status of this diagram is unknown (proposed variant? different product?). |
| **Team position (SRC-005)** | Proposes a different set: 15/10/10/15/20/30% for brackets 1–6. This is an explicit proposal to change the baseline, not a claim about what PCS does. |
| **Math consequence** | Higher B6 allocation concentrates prize pool in the jackpot; at low player counts, this money is never won and accumulates as rollover. At high player counts, jackpot hits become more valuable. The distribution choice has a large effect on expected per-ticket value across brackets. |
| **Status** | Open. SRC-017 allocation (15/25/50%) is unconfirmed as to origin. PCS allocation (10/20/40%) is confirmed. Team intent is not explicit. |
| **Blocks** | problem_statement_math, hypotheses, all scenario modeling |

---

## Section 2 — Conflicts within team-target sources

These reflect internal inconsistencies in the team's own materials.

---

### C-003 — Ticket price

| | |
|---|---|
| **Source A** | $1 per ticket. Used in R&D.md (SRC-005) working example and implied by handwritten note SRC-014 (100 players × $1 = $100 pool). |
| **Source B** | $2 per ticket. Used in simulator default (SRC-019: `ticket_price = 2.0`). |
| **Source C** | $5 USDT per ticket. Used throughout Retention_Team_comments.md (SRC-018): "Цена входа: 5 USDT". |
| **Status** | Open. Three values, no authoritative team decision. |
| **Blocks** | All unit economics; every per-ticket EV calculation; all scenario margins |

---

### C-004 — Currency

| | |
|---|---|
| **PCS position** | CAKE token. Prize pool denominated in CAKE. SRC-013 shows all values in CAKE with USD equivalents. |
| **Team position (SRC-019)** | USD-equivalent generic "$". Simulator is agnostic to currency but inherits PCS-style CAKE mechanics. |
| **Team position (SRC-018)** | USDT. Retention_Team_comments.md specifies "5 USDT" ticket price, "платим рефоводам в USDT" (we pay referrers in USDT), and "claim cashback [in USDT]". |
| **Consequence** | CAKE is volatile; USDT is stable. If the team's product uses USDT: (a) there is no token-burn mechanic in the same sense, (b) the economics are straightforward fiat-style, (c) the PCS injection mechanics (CAKE from treasury) do not directly apply. |
| **Status** | Open. This is the most consequential unresolved question: it determines whether the team is building a CAKE-denominated lottery or a stablecoin-denominated lottery. |
| **Blocks** | problem_statement_plain, problem_statement_math, burn definition, injection definition, all unit economics |

---

## Section 3 — Conflicts between sim-assumptions and unverified PCS behavior

The simulator made specific modeling choices for parameters where official PancakeSwap behavior was not verified in-session. These are not necessarily wrong, but they are unconfirmed against the official docs (SRC-001–SRC-004).

---

### C-005 — Burn on injections

| | |
|---|---|
| **Sim assumption** | `burn_applies_to_injections = True`. The 20% burn rate is applied to the total pool including the 8,000 CAKE injection. So 1,600 CAKE of each injection is burned; only 6,400 CAKE enters the prize pool. |
| **PCS status** | Not confirmed in-session. If PancakeSwap injects the full amount without burn, the effective injection into the prize pool is 8,000 CAKE, not 6,400. |
| **Consequence** | A 20% difference in effective injection per round. Over the sim's 104-round horizon this compounds. The baseline treasury cost figure in all scenarios shifts. |
| **Status** | Open. Must be verified against SRC-002/SRC-003. |
| **Blocks** | problem_statement_math (injection term), baseline treasury cost accounting |

---

### C-006 — Rollover mode

| | |
|---|---|
| **Sim assumption** | `rollover_mode = "global"`. All prize amounts from unhit brackets in a round merge into a single carry. The carry is redistributed proportionally across all brackets in the next round. |
| **Alternative** | `rollover_mode = "same_bracket"`. Each bracket's unhit amount carries forward only into that same bracket in the next round. |
| **PCS status** | Not confirmed in-session. The simulator README explicitly flags this as a modeling choice: "no re-burn of prior carry". |
| **Consequence** | Under global rollover, a large carry from many unhit jackpot rounds benefits all brackets proportionally. Under same-bracket rollover, the jackpot accumulates independently and jackpot winners win a much larger amount. The growth trajectory of the prize pool and the per-bracket expected value both differ. |
| **Status** | Open. Must be verified against SRC-002/SRC-004. |
| **Blocks** | problem_statement_math (carry-forward dynamics), hypotheses about jackpot growth |

---

### C-007 — Injection amount and schedule

| | |
|---|---|
| **Sim assumption** | 8,000 CAKE injected on rounds where `weekly_injection_cycle[round % 7] == 1`. The cycle is `[1, 0, 1, 0, 1, 0, 1]`, yielding 4 injection rounds per 7-round week. |
| **PCS status** | The 8,000 CAKE figure and the 4-of-7 schedule are stated in the simulator README as "Lottery injections: 8,000 CAKE every other round on a 7-round weekly cycle" (SRC-009). Not cross-verified against live official docs in-session. PancakeSwap may have changed injection parameters since this was last documented. |
| **Consequence** | Injection is the largest single component of the treasury cost baseline (~$4,538/round in simulation). An error here distorts all scenario comparisons relative to the true baseline. |
| **Status** | Open. Must be verified against SRC-002/SRC-003. |
| **Blocks** | Baseline financial calibration; all scenario margin figures |

---

### C-008 — Player count and scale

| | |
|---|---|
| **Sim assumption** | ~3,500 active players per round, ~10,600 total tickets per round. Derived from segment parameters: 22,000 casual × 8% + 5,000 repeat × 34% + 120 whales × 78% ≈ 3,554 active players. |
| **PCS observation** | Round 1949 (SRC-013, Apr 2, 2026): 38 total players. |
| **Team intent** | Unspecified. The simulator is plausibly modeling the team's hypothetical future product, but this is never stated explicitly in any source. |
| **Consequence** | At 38 players, brackets 4–6 are almost never hit organically. At 10,600 tickets, bracket 4 hits with P ≈ 1 − (1 − 9×10⁻⁵)^10600 ≈ 62% per round. The R&D.md critique ("dead money in high brackets") applies fully at 38 players; it does not apply at 10,600. All feature scenario conclusions are conditional on ~10,600 tickets/round. |
| **Status** | Open. This is the single largest source of fragility in all simulation outputs. |
| **Blocks** | Scenario calibration; all hypothesis testing; any quantitative conclusion about feature viability |

---

## Resolved conflicts

| ID | Topic | Resolution |
|---|---|---|
| C-R01 | Source type classification | Four .png files were misclassified as UI screenshots; they are simulation charts. SRC-013 was misclassified as a handwritten note; it is the PancakeSwap UI screenshot. Corrected 2026-04-24. |
| C-R02 | Pool base for bracket percentages | Confirmed by SRC-013 arithmetic: bracket percentages apply to the total pool (revenue + injection), not to a sub-pool. "2% of pool" = 2% of (tickets revenue + injection), with burn deducted first. Sum of bracket allocations + burn = 100%. |

---

## Missing definitions that block formalization

| ID | Item | Why it blocks | Status |
|---|---|---|---|
| M-001 | Is the team building a PancakeSwap fork or an independent product? | Determines which mechanics are inherited vs re-specified | open |
| M-002 | Ticket price for team's product | All per-ticket EV calculations depend on it | open |
| M-003 | Currency for team's product (CAKE / USDT / other) | Determines whether burn, injection, and treasury are token-based or fiat-based | open |
| M-004 | Injection budget and schedule for team's product | Determines baseline treasury cost; may differ from PCS 8,000 CAKE/cycle | open |
| M-005 | Bracket allocations for team's product (PCS 10/20/40% or something else) | Core mechanic; affects all prize pool math | open |
| M-006 | Matching direction for team's product | Affects implementation spec; probability math is direction-agnostic | open |
| M-007 | Rollover mode for team's product (global or per-bracket) | Affects carry-forward dynamics and jackpot growth model | open |
| M-008 | Whether burn applies to injections in team's product | Affects every injection cost calculation | open |
