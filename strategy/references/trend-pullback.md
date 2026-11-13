# "Trend pullback"

Buy a MACD bullish crossover from below zero while price holds above EMA200: a dip that turns back up inside an uptrend. Held overnight until a stop fills. One position at a time. Never add to an open position.

None of the original rule set's stop levels apply to it: no breakeven_plus, principal floor or 2% trailing stop.

## Extra state fields
- `last_used_signal_bar`: the ISO end time of the signal bar last used to buy. Default null.

## Extra position fields
- `atr_at_entry`: ATR14 of the signal bar.
- `entry_bar_end`: the ISO end time of the signal bar.
- `stops`: `{initial, breakeven (null until active), trailing}`
- `stop_reason`: one of "initial", "breakeven" or "trailing".

## BUY rule
1. Only when the strategy has no open position.
2. Only when ALL of these hold for the latest completed bar:
   - it has a bullish crossover
   - the MACD line < 0
   - its close > EMA200
   - it ended between 6:45 and 11:30 Pacific (inclusive)
3. Never reuse a signal bar: skip if the bar's end time equals last_used_signal_bar.
4. Make a paper BUY. Record atr_at_entry and entry_bar_end, and set last_used_signal_bar.

## SELL rule
1. Only when the strategy has an open position.
2. At each check, set peak_price = max(peak_price, current bid). The levels use atr_at_entry, which stays fixed for the life of the position:
   - **initial** = cost_price − 1.5 × atr_at_entry
   - **breakeven** = cost_price. Active once peak_price ≥ cost_price + 1 × atr_at_entry.
   - **trailing** = peak_price − 2.5 × atr_at_entry
   - **stop_price** = the highest active level, and never lower than the previous stop_price (it only moves up).
   - **stop_reason** = whichever level set it.
3. stop_price is the trigger of the position's resting stop-loss order. SELL when that order fills, at its fill price. There is no other exit.

## End-of-day liquidation
Does NOT apply. Positions may be held overnight, and the resting stop order stays in place. If the price opens below the trigger, the stop fills at the open (the GAP rule in `irrm-paper-trading`). No new position is opened from 12:50pm Pacific onward.

## Log line additions
- After the MACD section, add `| Close $x.xx vs EMA200 $x.xx, ATR14 $x.xx`.
