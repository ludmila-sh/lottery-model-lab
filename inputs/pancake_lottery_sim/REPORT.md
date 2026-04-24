# PancakeSwap Lottery Monte Carlo Analysis

## What this model does

This tool evaluates a PancakeSwap-style lottery under many rounds and many participation paths, then compares baseline economics versus retention features.

It measures:
- paid ticket revenue
- free ticket volume
- prize payouts
- burned value
- treasury-funded subsidies and injections
- cumulative incremental unit margin versus baseline
- downside tails and worst-case paths

## Baseline mechanics used

- 6-digit tickets
- digits 0–9
- prize requires matching from left to right
- non-stacking prize brackets
- 2% / 3% / 5% / 10% / 20% / 40% bracket split
- 20% burn
- 8,000 CAKE injected every other round on the published weekly schedule
- unhit prize amounts roll forward

## Core formulas

For an **exact** bracket hit:

- exact 1-match = `0.9 / 10 = 0.09`
- exact 2-match = `0.9 / 10^2 = 0.009`
- exact 3-match = `0.9 / 10^3 = 0.0009`
- exact 4-match = `0.9 / 10^4 = 0.00009`
- exact 5-match = `0.9 / 10^5 = 0.000009`
- exact 6-match = `1 / 10^6 = 0.000001`

For `N` effective tickets in a bracket:
- `P(any winner in bracket k) = 1 - (1 - p_k)^N`

Bulk discount support uses the documented Pancake-style formula:
- `total_price = price * n * D / (D + 1 - n)`

## Key economic insight

The base lottery is **not a normal house-edge casino product**. By construction, the bracket allocations already direct 80% of fresh inflow to prize funding and 20% to burn. When 8,000 CAKE is injected every other round, that is an explicit external subsidy rather than organic unit margin.

That means retention features should be judged mostly on:

`incremental paid sales - incremental treasury-funded subsidy`

not on raw payout timing, because rollover mainly shifts payouts across rounds.

## Validation

The ticket-level validation sample matched theory closely:

|   bracket |   expected |   observed |   abs_error |
|----------:|-----------:|-----------:|------------:|
|         1 |     0.09   |   0.090071 |    7.1e-05  |
|         2 |     0.009  |   0.009248 |    0.000248 |
|         3 |     0.0009 |   0.000906 |    6e-06    |
|         4 |     9e-05  |   8.9e-05  |    1e-06    |
|         5 |     9e-06  |   1.7e-05  |    8e-06    |
|         6 |     1e-06  |   2e-06    |    1e-06    |

## Scenario results

| scenario                 |   avg_paid_tickets_per_round |   avg_free_tickets_per_round |   avg_revenue_per_round |   avg_payout_per_round |   avg_burn_per_round |   avg_treasury_cost_per_round |   incremental_margin_ex_burn_vs_baseline |   prob_negative_unit_margin_ex_burn | safety_label                |
|:-------------------------|-----------------------------:|-----------------------------:|------------------------:|-----------------------:|---------------------:|------------------------------:|-----------------------------------------:|------------------------------------:|:----------------------------|
| baseline                 |                      10604.8 |                         0    |                 22308.7 |                20783.6 |              5369.44 |                       4538.46 |                                     0    |                                0    | baseline                    |
| bonus_tickets_light      |                      11031.1 |                       257.02 |                 23205.8 |                21500.5 |              5548.85 |                       4538.46 |                                   897.09 |                                0    | safe                        |
| cashback_5pct            |                      11184.4 |                         0    |                 23528.4 |                21749   |              5613.37 |                       5714.88 |                                    43.26 |                                0.26 | risky / parameter-sensitive |
| loss_rebate_whales_20pct |                      11056   |                         0    |                 23258.2 |                21531.9 |              5559.33 |                       6020.09 |                                  -532.17 |                                1    | structurally loss-making    |
| jackpot_boost_2k         |                      10925.7 |                         0    |                 22984   |                22869.2 |              5904.48 |                       6538.46 |                                 -1324.77 |                                1    | structurally loss-making    |
| loyalty_rebate_2pct      |                      10866.3 |                         0    |                 22859   |                21216.1 |              5479.48 |                       4748.77 |                                   339.93 |                                0    | safe                        |
| multiplier_rewards       |                      10841.1 |                         0    |                 22806   |                21171.8 |              5468.89 |                       5505.26 |                                  -469.54 |                                1    | structurally loss-making    |

## Interpretation

### Safe in the example assumptions
- **bonus_tickets_light**: positive incremental margin versus baseline and no negative paths in the run. This works because ticket lift is materially larger than the free-ticket burden.
- **loyalty_rebate_2pct**: still positive under the assumed uplift. Small, targeted rewards can work when aimed at repeat users instead of everyone.

### Borderline
- **cashback_5pct**: near break-even on average, but around 25.9% of simulated paths finished negative relative to baseline. This is the classic trap feature: broad appeal, weak margin.

### Structurally loss-making
- **loss_rebate_whales_20pct**: the rebate is too large relative to incremental whale spend.
- **jackpot_boost_2k**: direct subsidy dominates the extra demand in the example.
- **multiplier_rewards**: extra payout top-up is not offset by enough ticket lift.

## Business recommendations

1. Prefer **narrow, delayed, behavior-gated** rewards:
   - streak rewards
   - loyalty rebates capped to repeat users
   - occasional bonus tickets with hard caps

2. Avoid broad unconditional transfers unless you can prove large lift:
   - blanket cashback
   - large loss rebates
   - always-on jackpot boosts
   - uncapped payout multipliers

3. Evaluate every feature with a hurdle rule:
   - `incremental paid revenue must exceed incremental subsidy`
   - treat burn as a secondary upside, not the primary justification

4. Keep three hard controls in production:
   - per-user reward caps
   - per-round treasury budget caps
   - automatic kill switch when rolling 7- or 30-round incremental margin turns negative

## Files

- `scenario_summary.csv` — final summary table
- `scenario_round_means.csv` — mean path by round
- `scenario_comparison.md` — compact comparison table
- `cumulative_mean_margin.png` — cumulative scenario comparison
- `scenario_margin_bars.png` — mean incremental economics by feature
- `scenario_tail_risk.png` — downside tail chart
- `validation_exact_match.png` — validation plot

## Next step

Replace the illustrative segment populations, participation rates, and feature uplifts with your own observed data. The structure is already set up for config-driven scenario testing.
