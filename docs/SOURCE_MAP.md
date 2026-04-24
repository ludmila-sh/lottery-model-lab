# Source Map

## What we use and for what

| Item | Category | Used for | Reuse status | Notes |
|---|---|---|---|---|
| Compiani & Magnolfi (2024, BFI WP-2024-34) | Academic paper | Rollover recursion framing; demand-elasticity ranges as Morris sensitivity bounds (take rates 30–50%) | Reference only | Single jackpot bracket only. No parimutuel, no multi-tier carry. Our problem is a superset. Cite for rollover theory baseline. |
| Garvey et al. LGGR (arXiv 2311.04826, 2024) | Academic paper | Closed-form stationary distribution of bracket-6 carry; expected jackpot at time-of-win. Use as simulation sanity check for SC-4. | Partially reusable | Continuous-pool approximation; no discrete winner-count variance. Formula valid; context differs. Verify against our Binomial model before citing results. |
| Ziemba et al. — Parimutuel Betting Markets | Academic paper | Per-ticket EV approximation: `E[B_{k,t}/N_{k,t}] ≈ α_k × P_t / (N_t × p_k)`. Implemented in `constants.py::ev_per_ticket_approx()`. | Reference only | Betting markets (live odds). Formula is correct for our problem. Valid only when N >> 1/p_k (fails for brackets 4–6 at small N). |
| Walker & Young (2001) | Academic paper | Theoretical support for D-3C (frequency-balanced allocation) at small N; shows bracket reallocation toward low tiers increases player participation | Reference only | Static optimization; no stochastic dynamics or rollover. Use for qualitative design argument for D-3C only. |
| `frefrik/pancakeswap-lottery` (GitHub) | Code / data source | On-chain historical round data for EV-1 (Round 1949 back-check), EV-2 (bracket hit rate calibration), EV-3 (carry accounting). | Partially reusable | Read-only data extraction; no simulation. Requires BSC node / API key. Deferred to Phase 5. |
| SALib (GitHub / PyPI) | Python library | Morris screening + Sobol sensitivity analysis in Phase 5. Wraps simulator as black box. | Directly reusable | Generic tool. ~50-line integration in `sensitivity.py`. Add in Phase 5 only — not in v1. |
| `inputs/pancake_lottery_sim/engine.py` | Existing codebase | Vectorized MC engine, bracket probability model (`EXACT_MATCH_PROBS`), analytics pattern, scenario runner structure. Refactored into `research/simulator.py`. | Directly reusable (refactor) | Uses fictional segment populations (22k casual, 5k repeat, 120 whales). Engine core is correct; replace segment model with direct N input. |

---

## Items excluded

| Item | Reason |
|---|---|
| Cook & Clotfelter (1993, NBER) | Macro behavioral analysis (scale economies in demand). No equations applicable to our stochastic model. |
| Lockwood, Allcott, Taubinsky, Sial (2024, RES) | Behavioral welfare analysis. Not applicable to protocol PnL or prize pool simulation. |
| LottoPipeline (GitHub) | No parimutuel, no rollover, no bracket mechanics. Architecture simpler than existing simulator. |
| MC_Simulation_Lotto (GitHub) | Toy project; single bracket; no carry; nothing to reuse. |
| Mesa | Agent-based modeling framework. Not applicable to synchronous-round lottery. |
| SimPy | Discrete-event simulation. Not applicable — lottery rounds are synchronous. |
| PyMC | Bayesian parameter calibration. Deferred until behavioral data exists. |
| Hydra | Config composition for ML training. Overkill for a 5-scenario research framework. |

---

## Citation notes

- arXiv 2311.04826 (Garvey et al.) is freely accessible.
- BFI WP-2024-34 (Compiani & Magnolfi) is freely accessible as a working paper.
- Walker & Young (2001) is likely paywalled via journal. NBER version may be available.
- Ziemba et al. is available via LSE repository.
