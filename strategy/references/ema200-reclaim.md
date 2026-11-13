# "EMA200 reclaim" (paper experiment)

Buys when price closes back above EMA200 with MACD confirming, and holds across nights until price closes well below EMA200. One position at a time. Never add to an open position.

None of the original rule set's stop levels apply to it: no breakeven, breakeven_plus, principal floor or trailing stop.

## Extra state fields
- `last_used_signal_bar`: the ISO end time of the signal bar last used to buy. Default null.

## Extra position fields
- `atr_at_entry`: ATR14 of the signal bar. It stays fixed for the life of the position.
- `entry_bar_end`: the ISO end time of the signal bar.
- `stops`: `{initial}`
- `stop_reason`: "initial".

## BUY rule
1. Only when the strategy has no open position.
2. Only at a check whose time is between 6:35 and 12:59 Pacific (inclusive).
3. Only when all of these hold:
   - the previous completed bar's close ≤ its EMA200
   - the latest completed bar's close > its EMA200
   - on the latest completed bar, the MACD line > the signal line
4. Never reuse a signal bar: skip if the bar's end time equals last_used_signal_bar.
5. Make a paper BUY. Record atr_at_entry and entry_bar_end, and set last_used_signal_bar.

## SELL rule
1. Only when the strategy has an open position.
2. **initial** = cost_price − 6 × atr_at_entry. It is the stop_price, and it never moves. It is the trigger of the position's resting stop-loss order; SELL when that order fills, at its fill price. The order stays in place overnight, so a lower open fills at the open under the GAP rule.
3. **Trend exit:** at a check, if the latest completed bar ended after entry_bar_end and its close < its EMA200 − 3 × its ATR14, SELL at the current bid. The reason is "trend_exit".

## End-of-day liquidation
Does NOT apply. Positions may be held overnight.

## Log line additions
- After the MACD section, add `| Close $x.xx vs EMA200 $x.xx, exit below $x.xx, ATR14 $x.xx`.
- The Pos part shows the stop and the trend-exit level.
