# "RSI snapback"

Buy the first turn up out of a deep oversold reading and sell when RSI recovers to neutral. A short mean-reversion trade with a time stop. One position at a time. Never add to an open position.

Unlike the bounce mode of `regime-switch.md`, it trades in any regime (above or below EMA200), needs a deeper oversold reading, and exits on RSI recovery or a time stop instead of an ATR take-profit. None of the original rule set's stop levels apply to it.

## Extra state fields
- `last_used_signal_bar`: the ISO end time of the signal bar last used to buy. Default null.

## Extra position fields
- `atr_at_entry`: ATR14 of the signal bar.
- `entry_bar_end`: the ISO end time of the signal bar.
- `stops`: `{initial, breakeven (null until active)}`
- `stop_reason`: "initial" or "breakeven".

## BUY rule
1. Only when the strategy has no open position.
2. Only when ALL of these hold:
   - RSI14 of the previous completed bar < 25
   - RSI14 of the latest completed bar ≥ 25
   - the latest completed bar ended between 6:45 and 12:15 Pacific (inclusive)
3. Never reuse a signal bar: skip if the bar's end time equals last_used_signal_bar.
4. Make a paper BUY. Record atr_at_entry and entry_bar_end, and set last_used_signal_bar.

## SELL rule
1. Only when the strategy has an open position.
2. At each check, set peak_price = max(peak_price, current bid). The levels use atr_at_entry, which stays fixed for the life of the position:
   - **initial** = cost_price − 1.25 × atr_at_entry
   - **breakeven** = cost_price. Active once peak_price ≥ cost_price + 1 × atr_at_entry.
   - **stop_price** = the highest active level, and never lower than the previous stop_price (it only moves up).
   - **stop_reason** = whichever level set it.
3. SELL when the first of these happens:
   - The resting stop-loss order fills. The reason is stop_reason, at the fill price.
   - **RSI target:** at a check, RSI14 of the latest completed bar ≥ 55. The reason is "rsi_target", and it fills at the current bid.
   - **Time stop:** at a check at least 60 minutes after entry_time, the current bid < cost_price. The reason is "time", and it fills at the current bid.

## End-of-day liquidation
Applies. Positions are not held overnight.

## Log line additions
- After the MACD section, add `| RSI14 00.0 (prev 00.0), ATR14 $x.xx`.
- The Pos part shows the minutes held.
