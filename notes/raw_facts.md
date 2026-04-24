# Raw Facts

## Purpose
Central repository of extracted statements from raw source materials. Every statement is labeled. No smoothing of contradictions.

## Labels in use
- `[FACT]` — directly observable or stated as given in a primary source
- `[ASSUMPTION]` — taken as given by a model or author but not independently verified
- `[INTERPRETATION]` — a reading of ambiguous material; alternative readings exist
- `[OPEN_QUESTION]` — a gap that blocks formalization
- `[CONFLICT]` — directly contradicted by another source; see contradictions.md

---

## Source SRC-013 — PancakeSwap UI screenshot, Round 1949 (HIGH reliability)

### Source
- Source ID: SRC-013
- Source type: UI screenshot
- Author: PancakeSwap product
- Date: 2026-04-02 (round drawn date)
- Reliability: high (direct product observation)

### Extracted items

- [FACT] Round number: 1949
- [FACT] Draw time: April 2, 2026, 3:00 AM
- [FACT] Winning number displayed: 1 0 4 5 3 9 (six digits, shown left to right)
- [FACT] Total prize pot: ~$24,745 = 18,529 CAKE
- [FACT] Total players this round: 38
- [FACT] UI label for bracket 1: "Match first 1" — 371 CAKE, ~$495, 12.35 CAKE each, 30 winning tickets
- [FACT] UI label for bracket 2: "Match first 2" — 556 CAKE, ~$742, 277.93 CAKE each, 2 winning tickets
- [FACT] UI label for bracket 3: "Match first 3" — 926 CAKE, ~$1,237, 926.44 CAKE each, 1 winning ticket
- [FACT] UI label for bracket 4: "Match first 4" — 1,853 CAKE, ~$2,475, 0 winning tickets
- [FACT] UI label for bracket 5: "Match first 5" — 3,706 CAKE, ~$4,949, 0 winning tickets
- [FACT] UI label for bracket 6: "Match all 6" — 7,411 CAKE, ~$9,898, 0 winning tickets
- [FACT] Burn: 3,706 CAKE, ~$4,949
- [FACT] UI instruction: "Match the winning number in the same order to share prizes."
- [FACT] Bracket amounts verified: 371+556+926+1853+3706+7411+3706 = 18,529 CAKE ✓
- [FACT] Bracket fractions verified: 2%/3%/5%/10%/20%/40%/20% burn each confirmed to 4 sig figs
- [FACT] Matching direction confirmed by UI language: left-to-right ("Match first N")
- [INTERPRETATION] Prize pool is heavily padded by rollover or injection — 38 players × typical ticket price cannot generate ~$24,745 organically
- [OPEN_QUESTION] What was the ticket price in CAKE for this round?
- [OPEN_QUESTION] How many tickets did each of the 38 players buy?
- [OPEN_QUESTION] How much of the prize pool came from fresh ticket sales vs rollover vs injection?

### Numeric values
- Total CAKE in pot: 18,529
- CAKE/USD implied rate: ~$24,745 / 18,529 ≈ $1.335/CAKE
- Bracket 1 payout per winner: 12.35 CAKE (= 371/30)
- Bracket 2 payout per winner: 277.93 CAKE (= 556/2)
- Bracket 3 payout per winner: 926.44 CAKE (= 926/1)
- Total active players: 38

---

## Source SRC-005 — R&D.md (MEDIUM reliability)

### Source
- Source ID: SRC-005
- Source type: team analysis note (Russian language)
- Author: team / unknown author
- Date: 2026-04-24 (file date)
- Reliability: medium (internal analysis, not verified against primary sources)

### Extracted items

- [FACT] Mathematical claim: P(exact bracket 1) = (1/10) × (9/10) = 0.09
- [FACT] Mathematical claim: P(exact bracket 2) = (1/10)² × (9/10) = 0.009
- [FACT] Mathematical claim: P(exact bracket 3) = (1/10)³ × (9/10) = 0.0009
- [FACT] Mathematical claim: P(exact bracket 4) = 0.00009, P(5) = 0.000009, P(6) = 0.000001
- [FACT] Mathematical claim: self-buy increases the pool proportionally but also adds competitor tickets; per-winner payout stays the same as without self-buy
- [FACT] Mathematical claim: direct inject increases prize pool without adding competitor tickets, so per-winner payout increases for organic users
- [ASSUMPTION] Working example: 1000 user tickets × $1 = $1000 pool; prize pool (80%) = $800
- [ASSUMPTION] Working example: Bracket 1 (2%) = $16 among ~90 expected winners → $0.17/ticket
- [CONFLICT] States "matching right-to-left" as direction — contradicts SRC-013 which shows "Match first N" (left-to-right)
- [INTERPRETATION] Author argues the current bracket distribution creates psychological failure: players who win bracket 1 receive less than their ticket cost
- [INTERPRETATION] Author claims "90% of inject goes to brackets 4, 5, 6 which never get won at small scale" — this is a conditional claim that depends on player count and ticket volume
- [ASSUMPTION] Proposed new bracket allocations: 15% / 10% / 10% / 15% / 20% / 30% (of prize pool)
- [INTERPRETATION] Proposes "Dynamic Inject" = treasury guarantees minimum payout multiplier for brackets 1–2, only injects the shortfall each round
- [INTERPRETATION] Recommends eliminating self-buy entirely

### Numeric values
- Current bracket allocations (stated): 2%, 3%, 5%, 10%, 20%, 40%
- Proposed bracket allocations: 15%, 10%, 10%, 15%, 20%, 30% (of 80% prize pool)
- Working example ticket price: $1

---

## Source SRC-006 — Щедрая_лотерея.md (MEDIUM reliability)

### Source
- Source ID: SRC-006
- Source type: team concept doc (Russian language)
- Reliability: medium (internal brainstorm, not validated)

### Extracted items

- [FACT] Identifies core problem: "dead money" accumulating in high-bracket pools when jackpot is not won at low player counts
- [INTERPRETATION] Variant 1 (Waterfall / Roll-Down): if jackpot unawarded, portion cascades down to lower brackets. Proposed allocations: 15%/15%/10%/10%/15%/35%.
- [INTERPRETATION] Variant 2 (Pity Timer / "Loser Cashback"): split treasury 15%+5%; 5% goes to Retention Reserve; free ticket awarded after N consecutive losing rounds; "Lucky Near-Miss" consolation lottery among zero-match tickets
- [INTERPRETATION] Variant 3 (Risk Levels): player chooses Classic or Safe mode at ticket purchase; Safe players forgo jackpot brackets but get multiplied payouts on brackets 1–3
- [INTERPRETATION] Summary recommendation: shift 45% weight total to brackets 1–3 (vs current 10%); add 20% Roll-Down from unawarded jackpot; inject only into jackpot; cut treasury to 15%; auto-issue free tickets after 5–10 losses
- [INTERPRETATION] Solidity Plan 1 ("Attack Vector"): player chooses matching direction at mint (right-to-left / left-to-right / edges-to-center); implemented cheaply via modular arithmetic
- [INTERPRETATION] Solidity Plan 2 ("Sniper vs Shotgun"): straight (exact order) vs box (any-order) matching using bitmask comparison
- [INTERPRETATION] Solidity Plan 3 (LUCK Token): soulbound internal token accrues on losing tickets; redeemable for free tickets, insurance, or Gold upgrade
- [INTERPRETATION] Solidity Plan 4 (Syndicate): opt-in daily shared pool; if any member wins a large bracket, 50% shared among all syndicate participants
- [ASSUMPTION] Treasury = 20% of ticket sales (current baseline)
- [ASSUMPTION] Proposed treasury split: 15% project + 5% Retention Reserve

---

## Source SRC-018 — Retention_Team_comments.md (LOW reliability)

### Source
- Source ID: SRC-018
- Source type: team brainstorm note
- Reliability: low (internal, unvalidated, ticket price inconsistent with other sources)

### Extracted items

- [INTERPRETATION] Syndicate (Pool) feature: captain creates named pool, sets entry price, generates invite link; funds go to smart contract, not captain; win shares by contribution weight
- [INTERPRETATION] Syndicate edge cases: refund if underfunded, bot prevention via min 3 unique wallets, Roll-Over option for small wins
- [INTERPRETATION] XP/Points loyalty system — 5 tiers:
  - Level 1 (500 XP, min 2 tickets): 1 freebet
  - Level 2 (1,500 XP, min 8 tickets): 2 freebets
  - Level 3 (4,000 XP, min 20 tickets): 3 freebets + referral bonus
  - Level 4 (12,000 XP, min 50 tickets): 5 freebets + USDT bonus
  - Level 5 (35,000 XP, min 120 tickets): 7–10 freebets + VIP + USDT
- [ASSUMPTION] XP rates: 1 ticket = 100 XP; 3-in-a-row streak = 300 XP; 7-in-a-row = 1,000 XP; active week = 500 XP; friend buys first ticket = 200 XP; friend buys 3 total = +150 XP; friend active for a week = +150 XP
- [INTERPRETATION] Reserve fund: 5% of each ticket → separate smart contract for losers; eligibility requires spending > X USDT and winning < spent in that period
- [INTERPRETATION] Two cashback modes: (1) proportional guaranteed return; (2) "Losers Lottery" — entire reserve pool raffled among eligible losers
- [ASSUMPTION] Ticket price: $5 USDT
- [CONFLICT] $5 USDT ticket price conflicts with $1 (SRC-005/SRC-014), $2 (SRC-019), and unverified official CAKE price
- [INTERPRETATION] Referral program "Golden Link": 3 levels — Basic User 5%, Community Ambassador 10%, KOL/Affiliate 20–25%
- [OPEN_QUESTION] Are referral percentages paid out of treasury or separately? What is the funding source?

---

## Source SRC-014 — Handwritten calculation note 5393096941199103661.jpg (LOW reliability)

### Source
- Source ID: SRC-014
- Source type: handwritten note / rough working sketch
- Reliability: low (rough, no author or date, may be early brainstorm)

### Extracted items

- [ASSUMPTION] Example setup: prize pool $100 + $100 inject = $200 total; 100 players
- [ASSUMPTION] Bracket 1 = 2% (~$4); Bracket 2 = 3% (~$6)
- [ASSUMPTION] Ticket price: $1 (implied: 100 players × $1 = $100)
- [FACT] Correctly states P(bracket 1) = 9%, P(bracket 2) = 0.9%
- [INTERPRETATION] Sketch shows: 9 people win bracket 1 → $4/9 = $0.44 each; 1 person wins bracket 2 → $6
- [INTERPRETATION] Author then proposes allocating 10% of pool ($20) to losers (90 people) = $0.22/person consolation prize
- [OPEN_QUESTION] Is this "10% for losers" a proposed feature or arithmetic exploration? Not present in PancakeSwap baseline.

---

## Source SRC-017 — Digital diagram 5391296649822409622.jpg (LOW reliability)

### Source
- Source ID: SRC-017
- Source type: digital diagram (appears to be from a flowchart/presentation tool)
- Reliability: low (unverified; conflicts with official baseline)

### Extracted items

- [FACT] Shows a text box labeled "Prize Distribution (6 Brackets)"
- [CONFLICT] States "Match digits right-to-left" — contradicts SRC-013 (left-to-right) and SRC-019 (left-to-right)
- [CONFLICT] Shows B3=15%, B4=25%, B5=50% — contradicts official baseline (10%, 20%, 40%) confirmed by SRC-013
- [INTERPRETATION] This diagram likely describes a proposed alternative distribution, not the PancakeSwap baseline
- [OPEN_QUESTION] Is this diagram describing a different product entirely, or a proposed variant of PancakeSwap rules?

---

## Source SRC-019 — pancake_lottery_sim code (MEDIUM reliability)

### Source
- Source ID: SRC-019
- Source type: Python code artifact
- Reliability: medium (internal consistency verified; population assumptions are fictional)

### Extracted items

- [FACT] Implements 6-digit lottery, digits 0–9
- [FACT] Matching direction: left-to-right (variable named and described as "left-to-right")
- [FACT] bracket_allocations = [0.02, 0.03, 0.05, 0.10, 0.20, 0.40] — matches SRC-013 official values
- [FACT] burn_rate = 0.20
- [ASSUMPTION] ticket_price = $2.0
- [ASSUMPTION] injection_amount = 8,000 CAKE; injected on rounds where weekly_injection_cycle=1
- [ASSUMPTION] weekly_injection_cycle = [1, 0, 1, 0, 1, 0, 1] (4 injections per 7-round week)
- [ASSUMPTION] burn_applies_to_injections = True (burn rate applied to both ticket revenue AND injection)
- [ASSUMPTION] claim_rate = 1.0 (all winners claim; no unclaimed prizes)
- [ASSUMPTION] rollover_mode = "global" (all unhit prize amounts pool into one carry-forward, then redistributed by bracket weights next round)
- [ASSUMPTION] Segment "casual": population=22,000, participation_rate=0.08, mean_tickets=1.3, manual_share=0.65, entropy=0.92
- [ASSUMPTION] Segment "repeat": population=5,000, participation_rate=0.34, mean_tickets=2.8, manual_share=0.45, entropy=0.96
- [ASSUMPTION] Segment "whales": population=120, participation_rate=0.78, mean_tickets=38.0, manual_share=0.10, entropy=0.995
- [FACT] Exact-match probability formula: EXACT_MATCH_PROBS = [0.09, 0.009, 0.0009, 0.00009, 0.000009, 0.000001]
- [FACT] Round bracket hit model: P(any winner in bracket k) = 1 − (1 − p_k)^N for N effective tickets
- [FACT] Validation showed theoretical vs observed probabilities within acceptable tolerance for brackets 1–4; slight overcount in brackets 5–6 (expected for rare events in finite sample)
- [ASSUMPTION] Losing probability used in loss rebate calculation: 90% (= 1 minus overall win rate summed across brackets)
- [FACT] Bulk discount formula: total_cost = price × n × D / (D + 1 − n), where D=2000
- [ASSUMPTION] simulation: 104 rounds × 2,000 paths, seed=42
- [CONFLICT] Implied active players ~3,500/round from segment assumptions vs 38 real players observed in SRC-013

### Scenario summary (derived, not raw inputs)
- baseline: avg 10,605 paid tickets/round, avg revenue $22,309, avg burn $5,369, avg treasury cost $4,538
- bonus_tickets_light: +$897/round incremental margin vs baseline — labeled "safe"
- cashback_5pct: +$43/round, 25.9% paths negative — labeled "risky / parameter-sensitive"
- loss_rebate_whales_20pct: −$532/round, 100% paths negative — "structurally loss-making"
- jackpot_boost_2k: −$1,325/round, 100% paths negative — "structurally loss-making"
- loyalty_rebate_2pct: +$340/round, 0% paths negative — labeled "safe"
- multiplier_rewards: −$470/round, 100% paths negative — "structurally loss-making"
