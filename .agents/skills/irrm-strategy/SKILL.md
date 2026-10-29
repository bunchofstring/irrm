---
name: irrm-strategy
description: Help a human create, compare or change IRRM trading strategies, from idea to a tested rule set ready for review. Use when a human wants to design a new strategy, tune an existing rule set, or understand how a rule set behaves.
---

# IRRM strategy

Helps a human turn a trading idea into a rule set that is precise, tested and ready for a human maintainer to review.

## Terms

- A **rule set** is a reusable set of trading rules, one file per rule set in `strategy/references/`.
- A **strategy** is a rule set applied to one symbol, with its own $5.00 account. Writing a rule set does not make it live.

## What a rule set file defines

- **Summary:** one line.
- **Extra state fields** kept in the strategy's state doc, if any.
- **Extra position fields**, and the stop levels it keeps in `stops`, if any.
- **BUY rule.**
- **SELL rule:** stop levels and any other exits.
- **End-of-day liquidation:** whether it applies.
- **Log line additions**, if any.

Rule sets describe only their own trading rules. The indicator math and the paper-trading mechanics (sizing, fills, stop orders, liquidation) are the same for every rule set, so a rule set file does not repeat them.

## Workflow

1. **Understand the idea.** Ask what market behavior the human wants to trade, on which symbols, and what risk they will accept. Read existing rule sets in `strategy/references/` for comparison or as a starting point.
2. **Look at the market.** Use `irrm-market-analysis` to check how the idea fits recent price action on the symbols in question.
3. **Define the signals.** Express every condition with the indicators in `irrm-indicators`. If the idea needs an indicator that skill does not define, say so and propose adding it there first.
4. **Write the rule set.** Draft `strategy/references/<name>.md` with the sections above. Keep every rule precise enough to apply with no judgment calls. Changing an existing rule set changes every strategy that uses it, so prefer a new file for a new idea.
5. **Test it.** Use `irrm-backtest` to replay the rule set, and compare it with the rule sets it would replace or run beside.
6. **Hand it over.** Summarize the rule set and the backtest results. A rule set goes live only when a human maintainer approves adding it to the active strategies list.
