---
name: irrm-backtest
description: Backtest IRRM rule sets by replaying them over historical bars with IRRM's indicator and paper-fill rules. Use when a human asks how a strategy would have performed, or wants to compare rule sets, symbols or parameters before changing the live strategies.
---

# IRRM backtest

Replay one or more rule sets over historical data. The "rule set" column of `strategy/ACTIVE.md` says where each rule set file lives. Use:
- `irrm-indicators` for the indicators
- `irrm-paper-trading` for sizing, stop orders and end-of-day liquidation

## Rules

- **Read-only.** Fetch historical bars with read-only market-data tools only. Never use a tool that places, previews, reviews, changes, cancels or exercises an order, or moves money.
- **Never touch the live dashboard's state.** Do not write to the dashboard that the scheduled check uses.
- **Results live in the session.** When the backtest is done, ask the human whether they want the results in a dashboard artifact. If they do, use a separate artifact, never the live one.

## Method

1. **Agree the scope with the human:** rule sets, symbols, date range, starting balance (default $5.00 principal) and cap (default $100.00).
2. **Fetch the data** (see `references/data.md`): 5-minute regular-hours bars for the range plus at least 400 earlier completed bars to warm up the indicators, 1-minute bars for fills and stops, daily bars for valuation, dividends, and the 3-month Treasury bill yield.
3. **Step through the data.** Apply each rule set at each check as the live check would. Follow `references/conventions.md` exactly, so that two backtests of the same scope give the same numbers.
4. **State any departure.** If the data or the human's request forces a departure from a convention, say which one, why, and how it may flatter or penalize the results.
5. **Report** as `references/report.md` describes.

## Read only when needed

- **`references/data.md`:** the tables, bar timestamps and coverage check. Read it before fetching data.
- **`references/conventions.md`:** the check grid, fills and costs, valuation and returns, benchmark and validity rules. Read it before stepping through the data.
- **`references/report.md`:** what the results must include. Read it before reporting.

## Changing strategies

A backtest never changes the live strategies. If the results support a change, propose it for a human maintainer to approve.
