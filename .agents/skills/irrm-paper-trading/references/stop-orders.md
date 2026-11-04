# Resting stop-loss orders (paper)

Every paper BUY under a rule set that defines stop levels places a resting stop-loss order at the same moment as the buy. That way a stop is never missed because a check ran late or not at all.

The order is simulated: it exists only as `stop_order` in the position object. Never call a broker order tool to place, change or cancel it.

## At the BUY

1. Compute the position's starting `stop_price` and `stop_reason` from the rule set's SELL rule, as if this were the first check.
2. Record `stop_order = {type: "stop", trigger: stop_price, placed_at: entry_time, modified_at: entry_time}`.

## Fill test

Run this first thing in every check, for each open position:

1. Fetch 1-minute regular-hours bars from `stop_order.modified_at` up to now.
2. The stop fills on the first bar whose low ≤ trigger.
   - Fill price = the trigger, or that bar's open if the bar opened below the trigger (the price gapped through the stop).
   - Exit time = that bar's start time.
3. If no bar shows a fill yet but the current bid ≤ trigger, it fills at the trigger now.

## Bookkeeping

- Use the paper SELL bookkeeping, with the fill price in place of the bid.
- last_sell_time = exit time, and the trade doc's `ts` = exit time.
- If the fill is below the trigger by more than one cent, mark gap = true and log "GAP".

## Raising the trigger

- At each check, after the fill test, recompute the stop levels from the current bid as the rule set's SELL rule describes.
- When `stop_price` rises, raise the trigger to match and set `modified_at` = now. The trigger never moves down.
- Between checks, the trigger stays at the level set by the last check. A missed or late check therefore still fills the stop at the right price at the next check.

## Missing 1-minute bars

If 1-minute bars are unavailable or stale, treat it as missing data:
- take no new BUYs
- still sell any position whose current bid ≤ trigger, at the bid
- log why
