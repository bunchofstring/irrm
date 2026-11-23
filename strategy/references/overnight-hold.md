# "Overnight hold" (paper trial)

Buys late in every session, holds overnight, and sells the next trading morning, with no indicator filter. One position at a time. Never add to an open position.

## Extra state fields
- `last_used_signal_bar`: the ISO end time of the completed bar last used to buy. Default null.

## Extra position fields
- `entry_date`: the Pacific trading date of the buy.
- `entry_bar_end`: the ISO end time of the completed bar used to buy.

It defines no stop levels, so it places no resting stop order.

## BUY rule
1. Only when the strategy has no open position.
2. Only at a check whose time is between 12:40 and 12:49 Pacific (inclusive). The check takes no new positions from 12:50 onward. On half days, which close at 10:00 Pacific, it does not buy.
3. Never reuse a signal bar: skip if the latest completed bar's end time equals last_used_signal_bar.
4. Make a paper BUY. Record entry_date and entry_bar_end, and set last_used_signal_bar.

There is no EMA200 or other indicator condition.

## SELL rule
1. Only when the strategy has an open position.
2. At the first check at or after 9:00 Pacific on a trading day after entry_date, SELL at the current bid. The reason is "morning_exit".
3. There is no other exit.

## End-of-day liquidation
Does NOT apply. Positions are held overnight by design.

## Log line additions
- The Pos part shows entry_date and "sell from 09:00 next day".

## Paper trial
On QQQ, this rule set runs beside a QQQ buy-and-hold strategy, which is its benchmark. A human maintainer reviews it after 6 months of paper trading (about 125 trades):
- **Keep** it if its return is within 2 percentage points of QQQ buy-and-hold over the same period AND its largest drawdown is smaller.
- **Otherwise remove** it from `strategy/ACTIVE.md`.

Backtest evidence (`irrm-backtest` conventions v1, 2024-11-25 to 2026-11-12, 493 sessions, cost 1 bp per side, `irrm-paper-trading` bookkeeping that keeps uninvested cash):
- **Return:** +34.26% against +36.29% for QQQ buy-and-hold. Before costs it led, +48.01% against +36.31%. It trades twice a day, so it falls behind buy-and-hold above 0.85 bp per side.
- **Largest drawdown:** −23.5% against −22.8%. **Sharpe:** 0.69 against 0.63.
- **Trades:** 487 closed and 1 open, mean +0.067% per trade (t = 1.27, not statistically meaningful).
- **Most recent 30%** (2026-04-15 to 2026-11-12): +12.13% against +9.71%, drawdown −7.4% against −14.8%.
- **Keep bar:** met in 79 of 368 six-month windows (21%).

The rule set was found by searching this same period, so none of the evidence is out-of-sample. It did not beat buy-and-hold after costs. The trial tests whether it can match buy-and-hold while holding only overnight and early morning.
