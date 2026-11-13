# "Trend swing" (paper experiment)

MACD above zero + bullish crossover, held across nights behind wide ATR stops. One position at a time. Never add to an open position.

None of the original rule set's stop levels apply to it: no breakeven, breakeven_plus, principal floor or 2% trailing stop.

## Extra state fields
- `last_used_cross_bar`: the ISO end time of the crossover bar last used to buy. Default null.

## Extra position fields
- `atr_at_entry`: ATR14 of the crossover bar. It stays fixed for the life of the position.
- `entry_bar_end`: the ISO end time of the crossover bar.
- `stops`: `{initial, trailing}`
- `stop_reason`: "initial" or "trailing".

## BUY rule
1. Only when the strategy has no open position.
2. Only at a check whose time is between 6:35 and 12:59 Pacific (inclusive).
3. Only when the latest completed bar has a bullish crossover AND the MACD line > 0. EMA200 is not used.
4. Never reuse a crossover bar: skip if the bar's end time equals last_used_cross_bar.
5. Make a paper BUY. Record atr_at_entry and entry_bar_end, and set last_used_cross_bar.

## SELL rule
1. Only when the strategy has an open position.
2. At each check, set peak_price = max(peak_price, current bid). Compute these levels:
   - **initial** = cost_price − 6 × atr_at_entry
   - **trailing** = peak_price − 10 × atr_at_entry
   - **stop_price** = the higher of initial and trailing, and never lower than the previous stop_price (it only moves up).
   - **stop_reason** = whichever level set it.
3. stop_price is the trigger of the position's resting stop-loss order. SELL when that order fills, at its fill price. The order stays in place overnight, so a lower open fills at the open under the GAP rule.

## End-of-day liquidation
Does NOT apply. Positions may be held overnight.

## Log line additions
- After the MACD section, add `| ATR14 $x.xx`.
- The Pos part shows the stop, its reason, and the number of nights held.
