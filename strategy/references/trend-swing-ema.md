# "Trend swing, EMA200" (paper experiment)

Trend swing that buys only while price is above EMA200.

Same rules, parameters, state fields and position fields as `trend-swing.md`, except for the buy condition:

## BUY rule
Step 3 becomes: only when the latest completed bar has a bullish crossover AND the MACD line > 0 AND the bar's close > EMA200. Every other part of the trend-swing BUY rule applies.

## End-of-day liquidation
Does NOT apply. Positions may be held overnight.

## Log line additions
- After the MACD section, add `| Close $x.xx vs EMA200 $x.xx, ATR14 $x.xx`.
- The Pos part shows the stop, its reason, and the number of nights held.
