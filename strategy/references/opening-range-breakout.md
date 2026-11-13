# "Opening range breakout"

Buy the first close above the day's 15-minute opening range while MACD momentum is positive, and ride it with an ATR trailing stop. At most one buy per day. Never add to an open position.

Uses the opening range (OR15) from `irrm-indicators`. None of the original rule set's stop levels apply to it.

## Extra state fields
- `last_trade_date`: the Pacific date (YYYY-MM-DD) of the last buy. Default null.

## Extra position fields
- `or_high`, `or_low`: the day's OR15 high and low at the buy.
- `atr_at_entry`: ATR14 of the signal bar.
- `entry_bar_end`: the ISO end time of the signal bar.
- `stops`: `{initial, trailing}`
- `stop_reason`: "initial" or "trailing".

## BUY rule
1. Only when the strategy has no open position.
2. Only when last_trade_date is not today.
3. Only when today's OR15 is complete, and ALL of these hold:
   - the latest completed bar's close > or_high
   - the previous completed bar's close ≤ or_high (a fresh breakout)
   - the MACD histogram of the latest completed bar > 0
   - the latest completed bar ended between 6:50 and 10:00 Pacific (inclusive)
4. Make a paper BUY. Record or_high, or_low, atr_at_entry and entry_bar_end, and set last_trade_date to today.

## SELL rule
1. Only when the strategy has an open position.
2. At each check, set peak_price = max(peak_price, current bid). The levels use atr_at_entry, which stays fixed for the life of the position:
   - **initial** = the higher of (or_high + or_low) ÷ 2 and cost_price − 2 × atr_at_entry. A failed breakout that falls back to the middle of the range is over.
   - **trailing** = peak_price − 3 × atr_at_entry
   - **stop_price** = the higher of initial and trailing, never lower than the previous stop_price (it only moves up).
   - **stop_reason** = whichever level set it.
3. stop_price is the trigger of the position's resting stop-loss order. SELL when that order fills, at its fill price. There is no other exit before end of day.

## End-of-day liquidation
Applies. Positions are not held overnight.

## Log line additions
- After the MACD section, add `| OR15 $x.xx–$x.xx, Close $x.xx, ATR14 $x.xx`. Before 6:45 Pacific, show `OR15 forming`.
