# "Gap-fill overshoot" (paper trial)

Overnight-gap mean reversion, traded intraday. When AMZN opens at least 0.5% below the previous close, and has not already run up more than 5% over the past 20 sessions, it buys just after the open. It sells when the price has recovered 125% of the gap, or at its stop, or at the end of the day. One position at a time. Never add to an open position.

It uses the daily indicators in the "Daily indicators" section of `irrm-indicators`: the opening gap and the 20-session return.

## Extra state fields
- `last_entry_date`: the Pacific trading date of the last buy. Default null.

## Extra position fields
- `gap_abs`: the previous official close minus today's open, in dollars (positive).
- `target`: today's open + 1.25 × gap_abs.
- `stops`: `{initial}`
- `stop_reason`: "initial".

## BUY rule
1. Only when the strategy has no open position.
2. Only at the first check at or after 06:34 Pacific, and before 06:38. That is one chance per session.
3. Only if last_entry_date is not today.
4. BUY when both are true:
   - the opening gap ≤ −0.50%
   - the 20-session return ≤ +5.00%
5. Make a paper BUY. Record gap_abs and target, and set last_entry_date.

## SELL rule
1. Only when the strategy has an open position.
2. **initial** = cost_price − 1.0 × gap_abs. This stop is fixed and does not trail. The stop risk equals the size of the gap.
3. stop_price is the trigger of the position's resting stop-loss order. SELL when that order fills, at its fill price.
4. **take_profit:** at a check where the current BID ≥ target, SELL at the current bid. The reason is "take_profit".

## End-of-day liquidation
Applies. Positions are not held overnight.

## Log line additions
- After the MACD section, add `| Gap -0.00%, 20d return +0.00%`.
- The Pos part shows the stop and the target.

## Backtest evidence (conventions v1)

AMZN, 2024-11-26 to 2026-11-20 (498 sessions, just under 2 years), $5.00 start, c = 1 bp per side. This is generation 4's B4a.

| | Gap-fill overshoot | AMZN buy & hold |
|---|---|---|
| Total return | +37.84% | +22.24% |
| Out-of-sample (2026-04-22 to 2026-11-20) | +5.57% (Sharpe 0.66) | −1.24% |
| Sharpe / Sortino | 1.11 / 2.42 | 0.35 / 0.53 |
| Largest drawdown | −5.39% | −30.88% |
| Trades / hit rate / profit factor | 86 / 55.8% / 1.93 | — |
| Mean trade (t) | +0.39% (2.09) | — |
| Break-even cost per side | 18.5 bp (6.2 bp against buy & hold) | — |
| Time in market | 9.4% of session minutes, no nights | 100% |

Generation 5's B5a, with a stop of 1.5 × gap_abs, ranked slightly higher in-sample (Sharpe 1.33 against 1.26). It ranked lower out-of-sample (+3.47%, drawdown −7.52%) and over the full range. This file uses the simpler 1.0 × gap stop. That choice was made after seeing the out-of-sample results, so the out-of-sample figures above slightly flatter it.

Fewer than 100 trades and a range under 2 years make this weak evidence. Trying 87 variants also inflates the best results. A rule-free gap-fill baseline (gap ≥ 0.75%, full-fill target, generation 1) returned +6.12% over the same out-of-sample months. The refinements improved the in-sample results but not the out-of-sample results.

## Paper trial
Run it on AMZN beside the AMZN buy-and-hold strategy for 6 months. A human maintainer then reviews it:
- **Keep** it if its return is positive and its largest drawdown is under 10%.
- **Otherwise remove** it from `strategy/ACTIVE.md`.
