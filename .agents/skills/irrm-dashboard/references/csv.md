# Dashboard CSV files

The dashboard's charts read two CSV files attached to the dashboard artifact. Update both at every check, so the charts stay current to within one check.

| Dataset doc | File | One row per |
|---|---|---|
| `datasets/daily_pnl` | `daily_pnl.csv` | Pacific trading day and active strategy |
| `datasets/hourly_pnl` | `hourly_pnl.csv` | hour (PT, hour ending) and active strategy |

Each dataset doc holds the file's current location in `source.url` (`/_blob/<asset id>`), its file name in `source.name`, and `updated: {at, by}`.

## Columns

Money is in dollars, rounded to 6 decimals. A sell's P&L is its trade doc's `pnl`. Open P&L is `(mark − cost_price) × shares` for a strategy's open position, and 0 with no position. Take `strategy_name` from the "name" column of the active strategies list.

`daily_pnl.csv`: `date,strategy,strategy_name,day_pnl,cum_pnl,trades,wins,losses,open_pnl,total_pnl`
- `day_pnl`: the sum of that day's sell P&L
- `cum_pnl`: realized P&L since the start, through that day
- `trades`: that day's buys and sells; `wins` and `losses`: that day's sells with P&L above or below 0
- `open_pnl`: open P&L, marked at the day's close (today: at the latest bid)
- `total_pnl`: `cum_pnl + open_pnl`

`hourly_pnl.csv`: `date,hour,strategy,strategy_name,hour_pnl,cum_pnl,day_cum_pnl,trades,wins,losses,total_pnl`
- `hour`: the hour ending, `07:00` (covering 6:30–7:00am) through `13:00`
- `hour_pnl`: the sum of that hour's sell P&L
- `cum_pnl`: realized P&L since the start, through that hour; `day_cum_pnl`: the same for that day only
- `trades`, `wins`, `losses`: as in the daily file, for that hour
- `total_pnl`: `cum_pnl` plus open P&L marked at the hour's close (the current hour: at the latest bid)

## Updating at each check

1. **Download** the current files from the two dataset docs' `source.url`. Save them to disk and work on them with Python, not in your context.
2. **Rebuild today's rows only.** Keep every row dated before today exactly as it is. Replace today's rows with new ones built from today's trade docs (including this check's) and the state docs:
   - daily: one row per active strategy
   - hourly: one row per active strategy for each hour ending from `07:00` through the hour that contains this check. The last hour's row is partial until that hour ends.
   - A strategy new to the active list starts with `cum_pnl` 0.
3. **Upload** both files as new assets of the dashboard artifact (in Claude Code, the Artifact tool's asset upload), with the same file names.
4. **Point the datasets at them** in the check's one batch: update each dataset doc's `source.url` to its new asset's URL, exactly as the upload returned it, and set `updated` to `{at: <now, ISO UTC>, by: "IRRM check"}`. Pin each with its `if_version`.
5. **Delete the old assets** after the batch succeeds, so old files don't pile up. If the batch fails, delete the new assets instead.

On a market holiday, add no rows.
