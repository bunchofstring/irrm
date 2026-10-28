---
name: irrm-strategy
description: IRRM trading rule sets (buy and sell rules, stop levels, extra state fields). Use when running an active strategy in the IRRM check, replaying one in a backtest, or drafting, comparing or changing a trading strategy.
---

# IRRM strategy

A **rule set** is a reusable set of trading rules. Each one lives in `references/<rule set>.md`.

A **strategy** is a rule set applied to one symbol, with its own $5.00 account. The live strategies are listed only in the active strategies table in `tasks/irrm-check.md`. A rule set may back several strategies, or none.

## What a rule set file defines

- **Summary:** one line.
- **Extra state fields** kept in the strategy's state doc, if any.
- **Extra position fields**, and the stop levels it keeps in `stops`, if any.
- **BUY rule.**
- **SELL rule:** stop levels and any other exits.
- **End-of-day liquidation:** whether it applies.
- **Log line additions**, if any.

Sizing, fills, stop orders and liquidation mechanics are shared by all rule sets. They live in `irrm-paper-trading`. Indicators live in `irrm-indicators`.

## Using a rule set

- **In a check:** read the rule set named in each active strategy's row, and apply it to that strategy alone.
- **In a backtest or analysis:** list `references/` and read the rule sets you need.

## Drafting or changing rule sets

- Write a new rule set as a new `references/<name>.md` file with the sections above. Keep its rules precise enough to apply with no judgment calls.
- Changing a rule set changes every strategy that uses it.
- A rule set goes live only when a human maintainer approves adding a row for it to the active strategies table in `tasks/irrm-check.md`. Suggest a backtest (`irrm-backtest`) before proposing that.
