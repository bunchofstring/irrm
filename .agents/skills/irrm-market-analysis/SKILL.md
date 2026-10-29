---
name: irrm-market-analysis
description: Read-only market analysis for IRRM, such as where a symbol stands against IRRM's indicators and how close each strategy is to a buy or sell signal. Use when a human asks about the market, a symbol, or IRRM's current signals.
---

# IRRM market analysis

Analyze the active symbols (listed in `STRATEGIES.md`) or any symbol the human names.

## Rules

- **Read-only.** Use only read tools: quotes, historicals, fundamentals, news and search. Never use a tool that places, previews, reviews, changes, cancels or exercises an order, or moves money.
- **No dashboard writes.** You may read the live dashboard's state with ArtifactData to show current positions and stops. Never write to it.
- **No trades.** Analysis never trades, not even on paper. Paper trades come only from the scheduled check.

## Useful analysis

- Compute IRRM's indicators (`irrm-indicators`) on the latest completed bars.
- For each active strategy, say how close it is to its rule set's buy or sell condition (`irrm-strategy`).
- Give market context: recent price action, volume, news and upcoming events such as earnings.
- Say where data is missing or stale, and how that limits the analysis.
