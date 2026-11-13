# "Overnight hold" (paper experiment)

Buys late in every session, holds overnight, and sells the next trading morning, with no trend filter.

Same rules, state fields and position fields as `overnight-drift.md`, except for the BUY rule:

## BUY rule
1. Only when the strategy has no open position.
2. Only at a check whose time is between 12:40 and 12:59 Pacific (inclusive). On half days, which close at 10:00 Pacific, it does not buy.
3. Never reuse a signal bar: skip if the latest completed bar's end time equals last_used_signal_bar.
4. Make a paper BUY. Record entry_date and entry_bar_end, and set last_used_signal_bar.

There is no EMA200 or other indicator condition.

## End-of-day liquidation
Does NOT apply. Positions are held overnight by design.

## Log line additions
- The Pos part shows entry_date and "sell from 09:00 next day".
