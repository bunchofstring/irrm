# End-of-day liquidation

These rules apply only to strategies whose rule set says that end-of-day liquidation applies.

## Liquidation

- No such strategy holds a position overnight unless every end-of-day check was missed.
- Every check from 12:50pm Pacific until the 1:00pm close is an end-of-day check. If the strategy has an open position, sell all of it at the current bid, with reason "EOD liquidation".
- Use the paper SELL bookkeeping. The GAP rule does not apply.
- Log the liquidation in the strategy's log field, with a second line giving the trade's P&L.
- No such strategy opens a new position from 12:50pm onward.

## Missed liquidation

The market is closed after 1:00pm, so no sale can fill then.

If a position is still open after 1:00pm because every end-of-day check was missed:
1. Leave it open overnight, and log "EOD liquidation missed — position held overnight" in the strategy's log field.
2. The first check of the next trading day sells it, before anything else, at that day's opening price (the open of the first regular-hours 1-minute bar). The reason is "EOD liquidation (missed — sold at next open)".
3. The overnight gain or loss counts in that sale's P&L, and the GAP rule does not apply.
4. Mention any overnight hold in the end-of-day summary.
