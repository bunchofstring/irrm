---
name: irrm-paper-trading
description: IRRM's paper fill rules. Covers paper BUY sizing at the ask, sell bookkeeping, simulated resting stop-loss orders and end-of-day liquidation. Use when an IRRM check or backtest opens or closes a paper position.
---

# IRRM paper trading

All trades are hypothetical. They exist only as records in the dashboard database (or, in a backtest, in the session). Never call a broker tool to place, change or cancel anything, including the simulated stop orders described here.

## Paper BUY

- Fill at the current ASK.
- amount = min(balance, 100.00)
- shares = amount ÷ ask, rounded DOWN to 6 decimals
- cost_price = ask (the per-share price paid)
- cost_basis = shares × ask (the total dollars spent)
- entry_time = now
- peak_price = cost_price

The rule set may record more fields at the buy. If the rule set defines stop levels, place the resting stop order at the same moment (see `references/stop-orders.md`).

## Paper SELL bookkeeping

Every exit uses this bookkeeping, whatever the reason: stop, take-profit or end-of-day liquidation.

- proceeds = shares × fill price
- pnl = proceeds − cost_basis
- balance = proceeds
- realized_pnl += pnl
- position = null
- last_sell_time = exit time

Record a trade doc for every buy and sell.

## Read only when needed

- **`references/stop-orders.md`:** the resting stop-loss order, the fill test and the GAP rule. Read it whenever a strategy holds a position or buys.
- **`references/end-of-day.md`:** end-of-day liquidation, including the case where it was missed. Read it at any check from 12:50pm Pacific, and at the first check of a day when a position is still open from the day before.
