# Pancake Lottery Monte Carlo Simulator

This package simulates PancakeSwap-style 6-digit lottery economics over many rounds and many user-behavior paths.

## Structure

- `assumptions.py` — dataclasses and scenario config
- `engine.py` — round engine, rollover, burn, injections, and Monte Carlo logic
- `feature_rules.py` — subsidy and feature primitives
- `analytics.py` — validation, summaries, tail-risk metrics
- `plotting.py` — charts
- `scenarios.py` — baseline plus example feature scenarios
- `run_analysis.py` — entry point that generates outputs

## How to run

```bash
python run_analysis.py
```

Outputs are written to `outputs/`.

## Baseline defaults implemented

- 6 digits, each 0–9
- Exact prize brackets based on left-to-right matching
- Bracket allocations: 2%, 3%, 5%, 10%, 20%, 40%
- Burn: 20%
- Lottery injections: 8,000 CAKE every other round on a 7-round weekly cycle
- Bulk discount support via Pancake-style divisor formula
- Reproducible seed support

## Important modeling assumptions

1. **Burn is reported separately from treasury PnL.**
   It is a token sink, not treasury cash revenue.

2. **Rollover handling is configurable.**
   The default baseline uses `rollover_mode="global"` with no re-burn of prior carry.
   This avoids double-burning carried prizes and matches the product-level interpretation that rollover increases the next prize pool.

3. **Manual number picking is approximated with an entropy parameter.**
   Lower entropy means more clustered user picks and lower effective coverage of rare brackets.

4. **Claim rate defaults to 100%.**
   This can be lowered if you want to model unclaimed prizes.

5. **Feature scenarios are illustrative.**
   Replace the example segment sizes and uplift assumptions with your own observed funnel data.
