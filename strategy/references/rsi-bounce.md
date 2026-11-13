# "RSI bounce" (paper experiment)

Buys when RSI14 recovers from deeply oversold, and sells on an overbought RSI14 or at midday on the next trading day. May hold overnight. One position at a time. Never add to an open position.

None of the original rule set's stop levels apply to it: no breakeven, breakeven_plus, principal floor or trailing stop.

## Extra state fields
- `last_used_signal_bar`: the ISO end time of the signal bar last used to buy. Default null.

## Extra position fields
- `atr_at_entry`: ATR14 of the signal bar. It stays fixed for the life of the position.
- `entry_bar_end`: the ISO end time of the signal bar.
- `entry_date`: the Pacific trading date of the buy.
- `stops`: `{initial}`
- `stop_reason`: "initial".

## BUY rule
1. Only when the strategy has no open position.
2. Only at a check whose time is between 6:50 and 12:59 Pacific (inclusive).
3. Only when RSI14 of the previous completed bar < 25 AND RSI14 of the latest completed bar ≥ 25.
4. Never reuse a signal bar: skip if the bar's end time equals last_used_signal_bar.
5. Make a paper BUY. Record atr_at_entry, entry_bar_end and entry_date, and set last_used_signal_bar.

## SELL rule
1. Only when the strategy has an open position.
2. **initial** = cost_price − 6 × atr_at_entry. It is the stop_price, and it never moves. It is the trigger of the position's resting stop-loss order; SELL when that order fills, at its fill price. The order stays in place overnight, so a lower open fills at the open under the GAP rule.
3. **RSI exit:** at a check, if the latest completed bar ended after entry_bar_end and its RSI14 ≥ 70, SELL at the current bid. The reason is "rsi_exit".
4. **Time stop:** at the first check at or after 12:40 Pacific on a trading day after entry_date, SELL at the current bid. The reason is "time_stop". On a half day, which closes at 10:00 Pacific, this falls to the next trading day.

## End-of-day liquidation
Does NOT apply. Positions may be held overnight.

## Log line additions
- After the MACD section, add `| RSI14 00.0 (prev 00.0), ATR14 $x.xx`.
- The Pos part shows the stop and "time stop 12:40 next day".
