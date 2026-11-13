# "Overnight momentum"

Hold overnight only after an up day. Buy at the last check before 12:50pm Pacific when the price is above the previous session's close, and sell at the first check of the next trading day. One position at a time. Never add to an open position.

Why: over Nov 2024 – Nov 2026, AMZN's nights after an up day (12:45 PT price above the previous close) returned +41.2%. Nights after a down day were flat to negative. The filter worked in both halves of that period (+14.5% and +23.3%) and at nearby thresholds. It is not statistically significant on its own, so treat it as a hypothesis under test.

## Extra state fields
- `last_buy_date`: the Pacific date (YYYY-MM-DD) of the last buy. Default null.

## Extra position fields
- `buy_date`: the Pacific date of the buy.
- `prev_close_at_entry`: the prev_close used for the buy.

It defines no stop levels, so it places no resting stop order.

## BUY rule
1. Only when the strategy has no open position.
2. Only at a check between 12:45:00 and 12:49:59 Pacific, and only when the latest completed bar is the one ending at 12:45.
3. Only when last_buy_date is not today.
4. Only when that bar's close > prev_close (see `irrm-indicators`).
5. Make a paper BUY. Record buy_date and prev_close_at_entry, and set last_buy_date to today.

If no check falls in that window, there is no buy that day. Log why.

## SELL rule
1. Only when the strategy has an open position.
2. At the first check of any trading day after buy_date, sell at the current bid. The reason is "overnight exit".
3. If that check takes no action because data is missing or stale (guardrail 6), sell at the next check that has good data.

## End-of-day liquidation
Does NOT apply. Holding overnight is the strategy. Weekends and holidays are held through, and the position is sold at the first check of the next trading day.

## Log line additions
- After the MACD section, add `| Close $x.xx vs prev close $x.xx (UP/DOWN)`.
