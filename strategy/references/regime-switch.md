# "Regime switch" (paper experiment)

Switches between a trend rule and an oversold-bounce rule. One position at a time. Never add to an open position.

It uses only the buy and sell rules below. None of the original rule set's stop levels apply to it: no breakeven, breakeven_plus, principal floor or 2% trailing stop.

## Extra state fields
- `last_used_signal_bar`: the ISO end time of the signal bar last used to buy. Default null.

## Extra position fields
- `mode`: "trend" or "bounce".
- `atr_at_entry`: ATR14 of the signal bar.
- `entry_bar_end`: the ISO end time of the signal bar.
- `stops`: `{initial, trailing, take_profit (null in trend mode)}`
- `stop_reason`: "initial" or "trailing".

## Mode
- At each check, look at the latest completed bar. The mode is TREND if its close > EMA200; otherwise it is BOUNCE.
- An open position keeps the mode it was bought in until it is sold.

## BUY rule
1. Only when the strategy has no open position.
2. **TREND mode:** the latest completed bar has a bullish crossover AND the MACD line > 0, and that bar ended between 7:05 and 11:00 Pacific (inclusive).
3. **BOUNCE mode:** RSI14 of the previous completed bar < 30 AND RSI14 of the latest completed bar ≥ 30, and that bar ended between 6:50 and 12:15 Pacific (inclusive).
4. Never reuse a signal bar: skip if the bar's end time equals last_used_signal_bar.
5. Make a paper BUY. Record mode and atr_at_entry, and set last_used_signal_bar.

## SELL rule
1. Only when the strategy has an open position.
2. At each check, set peak_price = max(peak_price, current bid). The levels use atr_at_entry, which stays fixed for the life of the position:
   - **TREND:** initial = cost_price − 1.5 × atr_at_entry; trailing = peak_price − 4 × atr_at_entry; no take-profit.
   - **BOUNCE:** initial = cost_price − 1 × atr_at_entry; trailing = peak_price − 3 × atr_at_entry; take_profit = cost_price + 2 × atr_at_entry.
   - **stop_price** = the higher of initial and trailing, never lower than the previous stop_price (it only moves up).
   - **stop_reason** = whichever level set it.
3. SELL when either of these happens:
   - The resting stop-loss order fills. The reason is stop_reason.
   - In BOUNCE mode, the current BID ≥ take_profit at a check. The reason is "take_profit", and it fills at the current bid.

## End-of-day liquidation
Applies. Positions are not held overnight.

## Log line additions
- After the MACD section, add `| Mode TREND/BOUNCE, Close $x.xx vs EMA200 $x.xx, RSI14 00.0, ATR14 $x.xx`.
- The Pos part shows the mode, the stop and the take-profit.
