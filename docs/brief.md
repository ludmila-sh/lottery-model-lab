# Brief — Lottery Problem

## 1. What the problem is

A ticket lottery runs in discrete rounds. Players buy 6-digit tickets, a winning number is drawn uniformly at random, and each ticket wins at most one of six prize brackets based on how many consecutive digits match from a fixed end. Each bracket's prize pool is split equally among its winners. If a bracket has no winners, its allocated amount carries forward and inflates next round's pool. A periodic external injection supplements ticket revenue. Twenty percent of each round's pool is either burned (token model) or redirected as protocol fee (stablecoin model).

The core question: can this lottery be made economically viable — meaning incremental revenue from retention features covers their cost — without the prize pool becoming either structurally depleted or uselessly frozen in rollover?

There are two candidate baselines. One is the PancakeSwap product, which is a token-burn lottery with zero cash margin. The other is what the team intends to build, which may use a stablecoin and a cash-fee structure. These are not parameter variants of each other — they have different economic logics — and the team has not yet decided which one applies.

## 2. What the mathematical object is

The prize pool is a discrete-time stochastic process:

    P_t = (1 − r) × (revenue_t + I_t) + C_{t−1}

where r is the burn/fee rate, I_t the injection, and C_{t−1} the carry from unhit brackets. The bracket pools are B_{k,t} = α_k × P_t. Winner counts are approximately binomial: N_{k,t} | N_t ~ Bin(N_t, p_k), where p_k = 0.9/10^k for brackets 1–5 and 10^{−6} for the jackpot. Per-winner payout is parimutuel: B_{k,t} / N_{k,t} when N_{k,t} > 0; otherwise the full amount rolls forward.

The carry process is a Markov chain whose state is scalar under global rollover or a 6-vector under per-bracket rollover. The jackpot sub-process is a renewal process with geometric inter-arrival times: time to first jackpot win has expectation ≈ 10^6 / N rounds.

## 3. Why scale is the critical variable

At N tickets per round, the probability that bracket k pays out at all is 1 − (1 − p_k)^N. For the jackpot this is approximately N × 10^{−6}. At N = 38 (observed PancakeSwap), expected wait for a jackpot is ≈ 26,000 rounds — about 70 years at one round per day. At N = 10,000, it is ≈ 100 rounds.

This is not a detail. At low N, brackets 4–6 never pay out organically. Their allocations (70% of the prize pool) accumulate indefinitely. Player-facing expected value concentrates entirely in brackets 1–3 on fractions of the pool. The team's critique that "high-bracket money is frozen" is exactly right at 38 players and exactly wrong at 10,000. All simulation results in the existing codebase assume ≈ 10,000 tickets per round — a scale that has no grounding in any source document. Every quantitative conclusion about feature viability is conditional on this assumption.

## 4. What the team must decide

Five decisions gate any quantitative model. They are ordered: each later decision is only meaningful once earlier ones are fixed.

1. **Token or stablecoin.** If token: the model inherits PancakeSwap's burn logic and the protocol extracts no cash per ticket. If stablecoin: the protocol earns a cash fee per ticket, burn disappears, and injection is a direct USDT expense. This is a model-class choice, not a parameter.

2. **Fee and burn structure.** What fraction of each ticket goes to prizes, protocol, and reserve? This sets the prize pool equation.

3. **Bracket allocations.** Three candidate distributions exist with qualitatively different properties at low scale: PCS weights (top-heavy), the diagram variant (more top-heavy), and the proposed redesign (bottom-weighted for engagement). The choice materially changes per-ticket expected value at any realistic launch scale.

4. **Matching direction.** Left-to-right or right-to-left. The probability values are identical under uniform picks, but the formal bracket assignment function differs, the implementation differs, and the realized distribution for non-uniform pickers differs. It cannot be deferred to implementation.

5. **Injection model.** Fixed schedule, dynamic shortfall subsidy, or none. Injection is the dominant cost driver in the baseline financial model. Its form determines whether the protocol faces a fixed liability or a variable one that scales with player behavior.
