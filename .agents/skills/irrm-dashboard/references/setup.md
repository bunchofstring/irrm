# Creating or rebuilding the dashboard

Do this only in an interactive session, at a human's request.

## Steps

1. **Create the artifact.** Publish a private artifact with a shared database: the page plus the `db` capability. The page reads the database live. It shows:
   - An interactive P&L chart with a labeled line for each strategy found in the `trades` collection. The line is cumulative realized P&L over time, built from the sell trades. The chart offers the ranges 1d, 1w, 1m, 1y, 5y and all.
   - Each strategy's current balance, realized P&L and open position, from its state doc.
   - Today's per-check lines for each strategy, and the latest end-of-day summary, from the `days` collection.

   Derive strategies from the data, not from a list hard-coded into the page. Then adding or removing a strategy never requires a page change.
2. **Seed the database (optional).** Create `bot/check` and the state docs, as `schema.md` describes. If you skip this, the first check creates any missing doc.
3. **Hand over the URL.** Give the human the artifact URL. Tell them to edit the scheduled task's prompt so it ends with `Dashboard artifact: <url>`.

   Do not edit the scheduled task yourself. A human must approve that change. You may draft the new prompt text for them.

## Rebuilding an existing dashboard

- Change the page only. Never delete or rewrite existing `bot`, `days` or `trades` docs.
- Keep the same artifact URL, so the scheduled task's prompt stays valid.
