# "Donovan's original"

MACD above zero + bullish crossover. One position at a time. Never add to an open position.

## Extra state fields
- `last_used_cross_bar`: the ISO end time of the crossover bar last used to buy.

## Extra position fields
- `realized_pnl_before_trade`: the strategy's realized_pnl at the buy.
- `entry_bar_end`: the ISO end time of the crossover bar.
- `stops`: `{initial, breakeven (null until active), breakeven_plus (null until active), trailing, principal_floor (null unless active)}`
- `stop_reason`: one of "initial", "breakeven", "breakeven_plus", "trailing" or "principal".

## BUY rule
1. Only when the strategy has no open position.
2. Only when the latest completed bar has a bullish crossover AND the MACD line > 0.
3. Make a paper BUY. Record realized_pnl_before_trade = the strategy's current realized_pnl, and set last_used_cross_bar.

## SELL rule
1. Only when the strategy has an open position.
2. At each check, set peak_price = max(peak_price, current bid). Compute these levels:
   - **initial** = cost_price − min(1% of cost_price, $1.00 ÷ shares). The $1 cap is per position; on positions under $100 the 1% is smaller.
   - **breakeven** = cost_price. Active once peak_price > cost_price (the bid has risen above cost at any point since purchase).
   - **breakeven_plus** = cost_price × 1.0025 (cost +0.25%). Active once peak_price ≥ cost_price × 1.005 (the bid has been at least 0.5% above cost).

     Why the extra 0.25%: when the price falls fast, the stop can sell for a little less than its stop price. Setting the stop slightly above what we paid means a sale that lands a bit low should still come out at about break-even instead of a loss.
   - **trailing** = peak_price × 0.98
   - **principal_floor** = principal ÷ shares. Active only if realized_pnl_before_trade > 0.
   - **stop_price** = the highest active level, and never lower than the previous stop_price (it only moves up).
   - **stop_reason** = whichever level set it. Do NOT tighten for any other reason (no MACD-based tightening).
3. stop_price is the trigger of the position's resting stop-loss order. SELL when that order fills, at its fill price.

## End-of-day liquidation
Applies.

## Log line additions
None.
