# Active strategies

This is the only place that names the live strategies and their symbols. Every other file refers to "each active strategy" or "each active symbol". To add, remove or change a live strategy, edit this table. A human maintainer must approve the change.

| id | symbol | rule set | state doc | log field |
|---|---|---|---|---|
| main | CBRS | original | bot/state | lines |
| early | CBRS | early | bot/state_early | lines_early |
| regime | CBRS | regime-switch | bot/state_regime | lines_regime |
| bnh | AMZN | buy-and-hold | bot/state_bnh | lines_bnh |

## Columns

- **id:** names the strategy in trade doc ids and in each trade's `strategy` field.
- **symbol:** the only symbol this strategy may trade. The active symbols are the distinct symbols in this table.
- **rule set:** the file `.agents/skills/irrm-strategy/references/<rule set>.md`.
- **state doc:** the dashboard doc that holds this strategy's balance and position.
- **log field:** the field in each day's dashboard doc that holds this strategy's per-check lines.
