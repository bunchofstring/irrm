# "Overnight gap recovery"

Same entry as overnight momentum, with a different exit. It sells as soon as the position is above cost on a later day, which locks in gap-ups at the first check. After a gap down, it holds until the price gets back above cost, behind a 3% resting stop. A position still below cost at the next 12:45 check is kept overnight again only if the momentum condition still holds. One position at a time. Never add to an open position.

Why: over Nov 2024 – Nov 2026, AMZN gap-ups tended to fade in the first half hour, and gap-downs tended to recover. This exit returned +30.7% over that period (+7.3% and +21.8% in its two halves), with the 3% stop chosen in advance rather than tuned.

## Extra state fields
- `last_buy_date`: the Pacific date (YYYY-MM-DD) of the last buy. Default null.

## Extra position fields
- `buy_date`: the Pacific date of the buy.
- `prev_close_at_entry`: the prev_close used for the buy.
- `stops`: `{initial}`
- `stop_reason`: "initial".

## BUY rule
1. Only when the strategy has no open position.
2. Only at a check between 12:45:00 and 12:49:59 Pacific, and only when the latest completed bar is the one ending at 12:45.
3. Only when last_buy_date is not today.
4. Only when that bar's close > prev_close (see `irrm-indicators`).
5. Make a paper BUY. Record buy_date and prev_close_at_entry, and set last_buy_date to today.

## SELL rule
1. Only when the strategy has an open position.
2. **initial** = cost_price × 0.97. It is the trigger of the position's resting stop-loss order, set at the buy and never moved. stop_price = initial.
3. SELL when the first of these happens:
   - **Stop:** the resting stop-loss order fills, including at the open if the price gaps through it (the GAP rule in `irrm-paper-trading`). The reason is "initial".
   - **Above cost:** at any check on a trading day after buy_date, the current bid > cost_price. Sell at the bid. The reason is "above cost".
   - **Momentum lost:** at a check between 12:45:00 and 12:49:59 Pacific on a trading day after buy_date, if the position is still open and the 12:45 bar's close ≤ prev_close, sell at the bid. The reason is "momentum lost".
4. If the momentum condition still holds at that check, keep the position overnight again. Do not sell and re-buy.

## End-of-day liquidation
Does NOT apply. Positions are held overnight by design, and the resting stop stays in place.

## Log line additions
- After the MACD section, add `| Close $x.xx vs prev close $x.xx (UP/DOWN)`.
- The Pos part shows the stop and the days held.
