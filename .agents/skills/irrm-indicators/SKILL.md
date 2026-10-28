---
name: irrm-indicators
description: How IRRM computes MACD, the bullish crossover, EMA200, RSI14 and ATR14 from 5-minute bars. Use whenever an IRRM check, backtest or analysis needs indicator values.
---

# IRRM indicators

Compute indicators in Python (through Bash). Use only the closes and ranges of **completed** 5-minute regular-hours bars (6:30am–1:00pm Pacific). Never use the bar that is still forming. Use at least 400 completed bars, which is about 5 sessions; span previous sessions as needed.

Every EMA is a standard EMA with alpha = 2/(n+1).

## MACD and crossover

- MACD line = EMA12 − EMA26 of closes.
- Signal = the 9-period EMA of the MACD line.
- Histogram = MACD − signal.
- **Bullish crossover on the latest completed bar:** on the previous bar, MACD ≤ signal, AND on this bar, MACD > signal.

## EMA200

The 200-period EMA of closes (alpha = 2/201), seeded with the first close fetched.

## RSI14

Wilder's RSI of closes:
1. Average the first 14 gains and the first 14 losses.
2. Then smooth each one: (previous × 13 + new) ÷ 14.

## ATR14

The simple average of the true range of the last 14 completed bars.

True range = max(high − low, |high − previous close|, |low − previous close|).
