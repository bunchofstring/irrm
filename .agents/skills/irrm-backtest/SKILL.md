---
name: irrm-backtest
description: Backtest IRRM rule sets by replaying them over historical bars with IRRM's indicator and paper-fill rules. Use when a human asks how a strategy would have performed, or wants to compare rule sets, symbols or parameters before changing the live strategies.
---

# IRRM backtest

Replay one or more rule sets from `irrm-strategy` over historical data. Use:
- `irrm-indicators` for the indicators
- `irrm-paper-trading` for sizing, stop orders and end-of-day liquidation

## Rules

- **Read-only.** Fetch historical bars with read-only market-data tools only. Never use a tool that places, previews, reviews, changes, cancels or exercises an order, or moves money.
- **Never touch the live dashboard's state.** Do not write to the dashboard that the scheduled check uses.
- **Results live in the session.** When the backtest is done, ask the human whether they want the results in a dashboard artifact. If they do, use a separate artifact, never the live one.

## Method

1. **Agree the scope with the human:** rule sets, symbols, date range, starting balance (default $5.00 principal) and cap (default $100.00).
2. **Fetch the data.** Get 5-minute regular-hours bars for the range, plus enough earlier history to warm up the indicators (at least 400 completed bars). Get 1-minute bars for the stop fill test.
3. **Step through the data.** Step through each check during regular hours, and apply each rule set as the live check would. Only use bars completed by that time.
4. **State your assumptions.** Historical bid and ask quotes are often unavailable. Say what you used instead (for example, the 1-minute close for both), and say how that may flatter or penalize the results.
5. **Report per rule set:**
   - trades
   - wins and losses
   - total and per-day P&L
   - largest loss
   - ending balance
   - a head-to-head comparison

## Changing strategies

A backtest never changes the live strategies. If the results support a change, draft it (see `irrm-strategy`) for a human maintainer to approve.
