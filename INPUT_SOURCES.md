# Input Sources

## Purpose
Tracks all raw materials used in the project. Each source is assigned one primary classification:

| Classification | Meaning |
|---|---|
| `PCS-baseline` | Official PancakeSwap product — ground truth for how PancakeSwap works today |
| `team-target` | Team's own product assumptions, proposals, and intentions — may differ from PCS-baseline |
| `sim-assumption` | Simulator inputs or outputs — fictional or unverified parameters used to generate scenario results |
| `conflict` | Source that directly contradicts another registered source on a factual claim |

A source marked `conflict` is not necessarily wrong — it may represent a proposed variant. The conflict must be resolved before the canonical baseline is fixed.

---

## PCS-baseline sources

These sources describe PancakeSwap as it exists. They do not describe the team's product.

| Source ID | Type | Title / Description | Date | Reliability | Location |
|---|---|---|---|---|---|
| SRC-001 | web | PancakeSwap lottery main page | current | high — not yet fetched in-session | https://pancakeswap.finance/lottery |
| SRC-002 | web | PancakeSwap lottery docs | current | high — not yet fetched in-session | https://docs.pancakeswap.finance/play/lottery |
| SRC-003 | web | PancakeSwap lottery FAQ — prize bracket explanation | current | high — not yet fetched in-session | https://docs.pancakeswap.finance/play/lottery/lottery-faq |
| SRC-004 | web | PancakeSwap lottery guide | current | high — not yet fetched in-session | https://docs.pancakeswap.finance/play/lottery/lottery-guide |
| SRC-013 | image | 5944997056164335063.jpg — PancakeSwap UI, Round 1949 (Apr 2, 2026) | 2026-04-02 | high — direct product observation | inputs/5944997056164335063.jpg |

**SRC-013 confirmed facts** (arithmetic-verified): 6-digit tickets; left-to-right matching ("Match first N"); bracket allocations 2/3/5/10/20/40%; burn 20%; 38 total players; prize pot ~$24,745 = 18,529 CAKE.

---

## team-target sources

These sources describe what the team intends to build. They are not validated and contain internal inconsistencies. They must not be treated as facts about PancakeSwap.

| Source ID | Type | Title / Description | Date | Reliability | Location | Conflicts introduced |
|---|---|---|---|---|---|---|
| SRC-005 | file | R&D.md — math critique and proposed redesign | 2026-04-24 | medium | inputs/R&D.md | C-001 (matching direction), C-004 (ticket price $1) |
| SRC-006 | file | Щедрая_лотерея.md — retention and game-design proposals | 2026-04-24 | medium | inputs/Щедрая_лотерея.md | C-001 (direction, via "right-to-left" in Solidity plan) |
| SRC-014 | image | 5393096941199103661.jpg — handwritten calculation sketch | unknown | low | inputs/5393096941199103661.jpg | C-004 (ticket price $1), introduces consolation-prize idea (undefined status) |
| SRC-018 | file | Retention_Team_comments.md — retention brainstorm | unknown | low | inputs/Retention_Team_comments.md | C-004 (ticket price $5 USDT), C-005 (currency USDT) |

---

## sim-assumption sources

These sources are outputs or inputs of the pancake_lottery_sim package. All economic conclusions are conditional on fictional segment parameters. The simulator code (SRC-019) correctly implements PCS-baseline mechanics where specified, but adds unverified assumptions for injection burn, rollover mode, and all population figures.

| Source ID | Type | Title / Description | Date | What is assumed / fictional |
|---|---|---|---|---|
| SRC-019 | code | pancake_lottery_sim/ — Python Monte Carlo simulator | 2026-04-12 | Ticket price $2; segments (22 k casual, 5 k repeat, 120 whales) and their rates; injection 8,000 CAKE/every-other-round; burn applies to injections; rollover mode = global; claim rate 100% |
| SRC-009 | file | inputs/README.md — simulator package README | 2026-04-12 | Documents SRC-019 assumptions; not an independent source |
| SRC-007 | file | inputs/scenario_summary.csv | 2026-04-24 | Derived output; duplicate of pancake_lottery_sim/outputs/scenario_summary.csv |
| SRC-008 | file | inputs/REPORT.md | 2026-04-24 | Derived output; duplicate of pancake_lottery_sim/REPORT.md |
| SRC-010 | file | inputs/scenario_comparison.md | 2026-04-24 | Derived output; duplicate of pancake_lottery_sim/outputs/scenario_comparison.md |
| SRC-011 | image | Screenshot 2026-04-12 at 14.29.02.png — "Theoretical vs observed exact-match probabilities" | 2026-04-12 | Simulation validation chart; exported from sim run |
| SRC-012 | image | Screenshot 2026-04-12 at 14.28.48.png — "Tail downside after full horizon" | 2026-04-12 | Simulation output chart |
| SRC-015 | image | Screenshot 2026-04-12 at 14.27.40.png — "Mean cumulative unit margin by scenario" | 2026-04-12 | Simulation output chart |
| SRC-016 | image | Screenshot 2026-04-12 at 14.28.31.png — "Feature economics versus baseline" | 2026-04-12 | Simulation output chart |

**Note on SRC-007 through SRC-016:** All scenario conclusions (safe / risky / structurally loss-making labels) are conditional on the fictional segment assumptions in SRC-019. They are proofs-of-concept for the methodology, not predictions.

---

## conflict sources

These sources introduce factual claims that directly contradict PCS-baseline or other sources. They require explicit resolution before the team baseline can be fixed.

| Source ID | Type | Title / Description | Conflict ID(s) | Location |
|---|---|---|---|---|
| SRC-017 | image | 5391296649822409622.jpg — digital diagram, bracket structure | C-001, C-002 | inputs/5391296649822409622.jpg |

**SRC-017 content:** Text box labeled "Prize Distribution (6 Brackets): Match digits right-to-left: B0=2%, B1=3%, B2=5%, B3=15%, B4=25%, B5=50% JACKPOT." Both the direction and the B3–B5 allocations conflict with SRC-013 (PCS-baseline). The diagram may describe a proposed variant; its status is unresolved.

---

## Correction log
- 2026-04-24 (Phase 1 audit): SRC-011–SRC-016 reclassified from "UI screenshots/result screen references" to simulation output charts. SRC-013 reclassified from "handwritten note" to PancakeSwap UI screenshot. SRC-017 and SRC-018 added (previously unregistered). Four-category classification schema applied.
