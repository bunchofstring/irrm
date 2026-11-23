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

## Daily indicators (draft)

These are proposed for the draft rule sets `weak-close-swing` and `gap-fill-overshoot`. They need a human maintainer's approval before any live strategy uses them.

They use split-adjusted **official daily closes** from earlier sessions, plus today's data. P is the latest completed 1-minute regular-hours close. "Now" means today's close is replaced by P.

- **Opening gap** = (open of today's first regular-hours 1-minute bar) ÷ (previous session's official close) − 1.
- **20-session return** = (previous session's official close) ÷ (official close 21 sessions ago) − 1. It uses only closes known before today's open.
- **RSI2 now:** Wilder's RSI with n = 2, on official daily closes. Seed it over at least 250 sessions of history, then take one more Wilder step with P as today's close.
- **IBS now** (internal bar strength) = (P − today's low) ÷ (today's high − today's low). The high and low come from today's completed 1-minute bars. If high = low, IBS now = 0.5.
- **SMA3 now** = (the last 2 official daily closes + P) ÷ 3.
