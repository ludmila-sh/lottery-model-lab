# Lottery Model Lab

Quantitative research project: mathematical modeling and simulation of a PancakeSwap-style
6-digit bracketed prize lottery. Two candidate baselines with five unresolved structural
decisions. Analysis is blocked until those decisions are made by the team.

## Project state

| Phase | Status |
|---|---|
| Phase 0–2: Source intake, normalization, contradictions | Complete |
| Phase 3: Plain-language problem statement | Complete |
| Phase 4: Mathematical formulation | Complete |
| Phase 5–7: Hypotheses, solution options, validation plan | Not started (placeholders exist) |
| Research tool design | Complete — implementation is the next task |
| Research tool implementation | Not started |

## Critical scale fact

E[rounds to first jackpot] ≈ 10⁶ / N.

- At N = 38 (observed PancakeSwap, Apr 2026): ~26,000 rounds ≈ 72 years at one round/day.
- At N = 10,000: ~100 rounds.

The existing simulator assumes N ≈ 10,600 tickets/round — a fictional scale with no data
support. All quantitative conclusions about feature viability are conditional on this
assumption. At real PCS scale (38 players), the economic conclusions reverse.

## Five open decisions

Before any single formal model can be used for quantitative conclusions, the team must
decide (in order):

1. **D-1**: Token (burn-based) or stablecoin (cash-margin) — model-class choice, not a parameter.
2. **D-2**: Fee/burn structure — what fraction goes to prizes, protocol, reserve.
3. **D-3**: Bracket allocations — three candidate distributions with qualitatively different behavior at small N.
4. **D-4**: Matching direction — left-to-right (PCS) or right-to-left (team notes).
5. **D-5**: Injection model — fixed schedule, dynamic shortfall subsidy, or none.

See [docs/dual_baseline.md](docs/dual_baseline.md) for the full decision tree.

## Key documents

| Document | Purpose |
|---|---|
| [docs/brief.md](docs/brief.md) | Executive summary: problem, math object, scale insight, 5 decisions |
| [docs/dual_baseline.md](docs/dual_baseline.md) | Baseline A (PCS) vs Baseline B (team-target): full structural comparison and D-1..D-5 |
| [docs/problem_statement_plain.md](docs/problem_statement_plain.md) | Full plain-language problem statement |
| [docs/problem_statement_math.md](docs/problem_statement_math.md) | Mathematical formulation: probability structure, prize pool dynamics, two economic models |
| [docs/open_questions.md](docs/open_questions.md) | Q-001–Q-015: blocking questions by tier |
| [notes/raw_facts.md](notes/raw_facts.md) | Labeled statements extracted from all source materials |
| [notes/contradictions.md](notes/contradictions.md) | C-001–C-008: explicit conflict register |
| [notes/glossary.md](notes/glossary.md) | Canonical vocabulary across PCS, team-target, and simulator contexts |
| [INPUT_SOURCES.md](INPUT_SOURCES.md) | Source registry: all raw materials classified and indexed |

## File tree

```
lottery-model-lab/
├── CLAUDE.md                         # Project rules and workflow contract
├── INPUT_SOURCES.md                  # Source registry (SRC-001 through SRC-019)
├── README.md
│
├── docs/
│   ├── brief.md                      # Executive summary
│   ├── dual_baseline.md              # Baseline A vs B + D-1..D-5 decision tree
│   ├── open_questions.md             # Q-001–Q-015 blocking questions by tier
│   ├── problem_statement_math.md     # Full mathematical formulation
│   ├── problem_statement_plain.md    # Plain-language problem statement
│   ├── hypotheses.md                 # [placeholder — Phase 5]
│   ├── solution_options.md           # [placeholder — Phase 6]
│   ├── validation_plan.md            # [placeholder — Phase 7]
│   └── final_solution.md             # [placeholder — Phase 7]
│
├── notes/
│   ├── raw_facts.md                  # Labeled extracted statements from all sources
│   ├── contradictions.md             # C-001–C-008 conflict register
│   └── glossary.md                   # Canonical vocabulary
│
├── inputs/                           # Raw source materials + reference simulator
│   └── pancake_lottery_sim/          # Python Monte Carlo (Baseline A mechanics, fictional N)
│
└── archive/                          # Completed Phase 0 artifacts (not active)
    ├── PROJECT_BRIEF.md
    ├── INPUT_AUDIT.md
    ├── BATCHED_FIRST_SESSION_SCRIPT.md
    └── FIRST_SESSION_MASTER_PROMPT.txt
```
