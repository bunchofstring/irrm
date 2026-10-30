# Creating or rebuilding the dashboard

Do this only in an interactive session, at a human's request.

The dashboard is an artifact made from the Dashboard artifact type. Its shared database holds two things side by side:
- the dashboard's own documents: `dash/meta`, `datasets/daily_pnl`, `datasets/hourly_pnl` and the page in `files/index.html`
- IRRM's state: the `bot`, `days` and `trades` collections that `schema.md` describes

The page draws its charts from the two CSV files in `csv.md`, never from IRRM's state directly. The check keeps those files current.

## Steps

1. **Create the artifact** from the Dashboard type (in Claude Code, the Artifact tool's quickstart, then a publish with the type's link). Follow the type's own instructions for its documents, and write `dash/meta` with a title such as "IRRM strategies — daily P&L".
2. **Build the two CSV files** with the columns in `csv.md`, from the `trades` collection and the state docs. With no trades yet, a file with just the header row is fine.
3. **Attach them as datasets.** Upload each file as an asset of the artifact. Write `datasets/daily_pnl` and `datasets/hourly_pnl`, each with:
   - `title` and a one-sentence `description`
   - `source: {kind: "file", url: <the upload's URL, exactly as returned>, name: "daily_pnl.csv" or "hourly_pnl.csv", format: "csv"}`
   - `updated: {at: <now, ISO UTC>, by: <who>}`
4. **Write the page** to `files/index.html`. It shows:
   - which strategy is ahead overall, and by how much
   - range buttons for 1d, 1w, 1m, 1y, 5y and all. 1d uses the hourly file; the other ranges use the daily file.
   - a chart of realized P&L per period, one series per strategy
   - a chart of cumulative P&L including open positions (`total_pnl`), one labeled line per strategy
   - a table per strategy: today's P&L, total realized P&L, balance ($5.00 principal + realized P&L), wins, losses and open P&L

   Take strategies, their names and their order from the CSV data, not from a list hard-coded into the page. Then adding or removing a strategy never requires a page change.
5. **Seed IRRM's state (optional).** Create `bot/check` and the state docs, as `schema.md` describes. If you skip this, the first check creates any missing doc.
6. **Hand over the URL.** Give the human the artifact URL. Tell them to edit the scheduled task's prompt so it ends with `Dashboard artifact: <url>`.

   Do not edit the scheduled task yourself. A human must approve that change. You may draft the new prompt text for them.

## Rebuilding an existing dashboard

- Change the page, `dash/meta` or the datasets' titles and descriptions only. Never delete or rewrite existing `bot`, `days` or `trades` docs, or the rows of the CSV files.
- Keep the two dataset ids and file names, so the check can keep updating them.
- Keep the same artifact URL, so the scheduled task's prompt stays valid.
