# "Overnight drift"

Hold only overnight: buy at the last check before 12:50pm Pacific and sell at the first check of the next trading day. It aims to capture the overnight return and avoid market hours. One position at a time. Never add to an open position.

Why: over Nov 2024 – Nov 2026, AMZN's gain came overnight, not during market hours. Buying at 12:45 PT and selling at the next morning's first check returned +17.9% across 495 nights, while the session from the first check to 12:45 PT was flat.

## Extra state fields
- `last_buy_date`: the Pacific date (YYYY-MM-DD) of the last buy. Default null.

## Extra position fields
- `buy_date`: the Pacific date of the buy.

It defines no stop levels, so it places no resting stop order. Between 12:45 and the 1:00pm close the position is exposed for at most 15 minutes, and overnight no order can fill before the open anyway.

## BUY rule
1. Only when the strategy has no open position.
2. Only at a check between 12:45:00 and 12:49:59 Pacific, and only when the latest completed bar is the one ending at 12:45.
3. Only when last_buy_date is not today.
4. Make a paper BUY. Record buy_date and set last_buy_date to today.

If no check falls in that window, there is no buy that day. Log why.

## SELL rule
1. Only when the strategy has an open position.
2. At the first check of any trading day after buy_date, sell at the current bid. The reason is "overnight exit".
3. If that check takes no action because data is missing or stale (guardrail 6), sell at the next check that has good data.

## End-of-day liquidation
Does NOT apply. Holding overnight is the strategy. Weekends and holidays are held through, and the position is sold at the first check of the next trading day.

## Log line additions
- After the MACD section, add `| Overnight: buy window 12:45–12:49 PT` while flat, or `| Overnight: held since <buy_date>` while holding.
