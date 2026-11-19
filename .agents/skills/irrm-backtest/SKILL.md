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

1. **Agree the scope with the human:** rule sets, symbols, date range, starting balance (default $5.00 principal) and cap (default $100.00). If the human gives only an end date ("through 2025"), the range starts at the earliest date the data supports after warm-up; say which date that is.
2. **Fetch the data.** Get 5-minute regular-hours bars for the range, plus enough earlier history to warm up the indicators (at least 400 completed bars). Get 1-minute bars for fills and the stop fill test. See **Data** below.
3. **Step through the data.** Step through each check on the check grid, and apply each rule set as the live check would. Follow **Conventions** below exactly, so that two backtests of the same scope give the same numbers.
4. **State any departure.** If the data or the human's request forces a departure from a convention, say which one, why, and how it may flatter or penalize the results.
5. **Report per rule set:**
   - trades
   - wins and losses
   - total and per-day P&L
   - largest loss
   - largest drawdown
   - ending balance
   - a head-to-head comparison, including buy & hold of the same symbol
   - the conventions version (below) and the first and last check used

## Data

Prefer the BigQuery dataset `irrm-515119.irrm_market_data`, read with read-only SQL:
- `minute_bars`: 1-minute regular-hours bars. `ts` is the bar's **start** time in UTC, so the bar stamped 12:39 PT covers 12:39:00–12:40:00 and is completed at 12:40. Convert to Pacific with `America/Los_Angeles`.
- `daily_bars`: daily regular-hours bars, split-adjusted.
- `earnings_dates`: earnings report dates.

Build 5-minute bars from the 1-minute bars when needed. Check coverage first: each full day has 390 1-minute bars and each half day has 211 (last bar 09:59 PT). Treat a day with any other count as a data gap and report it.

## Conventions (v1)

These remove the choices that otherwise make two backtests of the same scope disagree.

### Check grid
- Checks run at Pacific clock times every 4 minutes from 06:30 (06:30, 06:34, …), plus the start time of every time window a rule set names (for example 09:00, 12:40, 12:50). The last check of a day is the last grid time before the close (13:00, or 10:00 on half days).
- A rule that fires "at the first check at or after T" fires at T. A rule limited to a window fires at the first check in that window.

### Prices at a check at time T
- **Completed bars only.** At T, the latest completed 1-minute bar is the one that started at T − 1 minute. The latest completed 5-minute bar is the one that ended at or before T. Never use a bar that ends after T.
- **Bid and ask.** Historical quotes are unavailable, so the bid and the ask at T are both the close of the latest completed 1-minute bar. This flatters every strategy by about half a spread per fill. Say so in the report.
- **Stop fills** follow `irrm-paper-trading/references/stop-orders.md`, using the 1-minute bars between checks.

### Range boundaries
- A strategy may buy only at checks inside the range.
- A position still open at the last check of the range is **marked, not sold**. It is valued at the close of the range's last 1-minute bar and reported as one open trade. It does not count as a win or a loss. No data after the range is used.
- **Buy & hold** buys at the first check of the range with the same fill rule and starting balance, and is valued at the same final close.

### Periods and drawdown
- **Equity** is the cash balance plus any open position marked at the latest close. Record it at each day's last 1-minute close.
- A period's return (month, year) is equity at the period's last close ÷ equity at the previous period's last close − 1. The first period starts from the starting balance.
- A trade belongs to the period of its **exit** date. Count an open trade only in the final period.
- **Largest drawdown** is the largest fall of daily equity from its running peak, with the starting balance as the first peak. Use the same method for buy & hold.

### Rounding
Follow `irrm-paper-trading` for share rounding. Report returns to 2 decimals in percent and balances to the cent.

Change these conventions only with a human maintainer's approval. Bump the version when you do, so older results can be told apart.

## Changing strategies

A backtest never changes the live strategies. If the results support a change, propose it for a human maintainer to approve.
