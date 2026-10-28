---
name: irrm-summary
description: How to write IRRM's end-of-day summary after the 1:00pm Pacific close, with a head-to-head comparison of every active strategy and the cumulative P&L record. Use at the IRRM check's end-of-day step, or when a human asks for a summary of a trading day.
---

# IRRM end-of-day summary

Write the summary into today's day doc `summary` field, and make it your final message. Cover every active strategy.

## P&L chart

- Display an interactive P&L chart with a labeled line for each active strategy. The paper-trading record is cumulative up to the time of the report.
- The chart can show these ranges: 1d, 1w, 1m, 1y, 5y and all.
- Build it from the `trades` collection, so it includes every past session.
- The latest chart must be visible in the dashboard artifact.

## Head-to-head

For each active strategy, show:
- today's trades (times, prices, reasons)
- wins and losses
- today's P&L
- total realized P&L since the start
- balance

Say which strategy is ahead overall, and by how much.

## Per strategy

- **Each closing trade:** the time, shares, bid, proceeds and P&L.
- **A strategy with no position:** say so, and say whether it is approaching a buy signal.
- **A position held overnight:** mention it, either as allowed by the rule set or as a missed end-of-day liquidation.
