# "Weak-close swing" (draft, not live)

Daily mean reversion. Buys AMZN late in a session that is closing weak, holds overnight, and sells when the price climbs back above its 3-day average or after 3 sessions. One position at a time. Never add to an open position.

It uses the daily indicators in the "Daily indicators (draft)" section of `irrm-indicators`: RSI2 now, IBS now and SMA3 now.

## Extra state fields
- `last_entry_date`: the Pacific trading date of the last buy. Default null.

## Extra position fields
- `entry_date`: the Pacific trading date of the buy.
- `entry_rsi2`, `entry_ibs`: the signal values at the buy.

It defines no stop levels, so it places no resting stop order.

## BUY rule
1. Only when the strategy has no open position.
2. Only at the first check at or after 12:40 Pacific, and before 12:50. On half days, which close at 10:00 Pacific, it does not buy.
3. Only if last_entry_date is not today.
4. Let P be the latest completed 1-minute close. BUY when both are true:
   - RSI2 now < 25
   - IBS now ≤ 0.30
5. Make a paper BUY. Record entry_date, entry_rsi2 and entry_ibs, and set last_entry_date.

## SELL rule
1. Only when the strategy has an open position, and only at checks on a trading day after entry_date.
2. At each check, SELL at the current bid when the first of these is true:
   - **above_sma3:** P > SMA3 now.
   - **time:** this is the 3rd trading session after entry_date or later.
3. There is no stop-loss. In the backtest the largest loss on a trade was −4.42%.

## End-of-day liquidation
Does NOT apply. Positions are held overnight by design.

## Log line additions
- After the MACD section, add `| RSI2 now 00.0, IBS now 0.00, SMA3 now $x.xx`.
- The Pos part shows entry_date and "exit > SMA3 or day 3".

## Backtest evidence (conventions v1)

AMZN, 2024-11-26 to 2026-11-20 (498 sessions, just under 2 years), $5.00 start, c = 1 bp per side. It was selected in generation 4 of a 5-generation search over 87 variants, using the in-sample period only (2024-11-26 to 2026-04-21).

| | Weak-close swing | AMZN buy & hold |
|---|---|---|
| Total return | +40.41% | +22.24% |
| Out-of-sample (2026-04-22 to 2026-11-20) | +8.66% (Sharpe 1.13) | −1.24% |
| Sharpe / Sortino | 1.03 / 1.91 | 0.35 / 0.53 |
| Largest drawdown | −5.83% | −30.88% |
| Trades / hit rate / profit factor | 62 / 71.0% / 2.26 | — |
| Mean trade (t) | +0.57% (2.20) | — |
| Break-even cost per side | 28.2 bp (12.2 bp against buy & hold) | — |
| Time in market | 10.8% of session minutes, 21.3% of nights | 100% |

Fewer than 100 trades and a range under 2 years make this weak evidence. Trying 87 variants also inflates the best results.

## Paper trial (proposed)
Run it on AMZN beside the AMZN buy-and-hold strategy for 6 months. A human maintainer then reviews it:
- **Keep** it if its return is positive and its largest drawdown is under 10%.
- **Otherwise remove** it from `strategy/ACTIVE.md`.
