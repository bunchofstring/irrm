# "Overnight drift" (paper experiment)

Buys late in the session while price is above EMA200, holds overnight, and sells the next trading morning. One position at a time. Never add to an open position.

## Extra state fields
- `last_used_signal_bar`: the ISO end time of the completed bar last used to buy. Default null.

## Extra position fields
- `entry_date`: the Pacific trading date of the buy.
- `entry_bar_end`: the ISO end time of the completed bar used to buy.

It defines no stop levels, so it places no resting stop order.

## BUY rule
1. Only when the strategy has no open position.
2. Only at a check whose time is between 12:40 and 12:59 Pacific (inclusive). On half days, which close at 10:00 Pacific, it does not buy.
3. Only when the latest completed bar's close > EMA200.
4. Never reuse a signal bar: skip if the latest completed bar's end time equals last_used_signal_bar.
5. Make a paper BUY. Record entry_date and entry_bar_end, and set last_used_signal_bar.

## SELL rule
1. Only when the strategy has an open position.
2. At the first check at or after 9:00 Pacific on a trading day after entry_date, SELL at the current bid. The reason is "morning_exit".
3. There is no other exit.

## End-of-day liquidation
Does NOT apply. Positions are held overnight by design.

## Log line additions
- After the MACD section, add `| Close $x.xx vs EMA200 $x.xx`.
- The Pos part shows entry_date and "sell from 09:00 next day".
