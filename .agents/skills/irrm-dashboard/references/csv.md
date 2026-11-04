# Dashboard CSV files

The dashboard's charts read two CSV files attached to the dashboard artifact. Update both once a day, at the end-of-day step after the close. Updating them is expensive, so a regular check never touches them: the charts show data through the last close.

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
- `open_pnl`: open P&L, marked at the day's close
- `total_pnl`: `cum_pnl + open_pnl`

`hourly_pnl.csv`: `date,hour,strategy,strategy_name,hour_pnl,cum_pnl,day_cum_pnl,trades,wins,losses,total_pnl`
- `hour`: the hour ending, `07:00` (covering 6:30–7:00am) through `13:00`
- `hour_pnl`: the sum of that hour's sell P&L
- `cum_pnl`: realized P&L since the start, through that hour; `day_cum_pnl`: the same for that day only
- `trades`, `wins`, `losses`: as in the daily file, for that hour
- `total_pnl`: `cum_pnl` plus open P&L marked at the hour's close

## Updating at the end of the day

1. **Download** the current files from the two dataset docs' `source.url`. Save them to disk and work on them with Python, not in your context.
2. **Add the missing days.** Keep every existing row exactly as it is. For each trading day after the last day in the files, through today, add rows built from that day's trade docs and closing prices, and today's from the state docs too:
   - daily: one row per active strategy, with open positions marked at that day's close
   - hourly: one row per active strategy for each hour ending from `07:00` through `13:00`
   - A strategy new to the active list starts with `cum_pnl` 0.

   Normally this is just today. A day is missing only when an earlier end-of-day update failed.
3. **Upload** both files as new assets of the dashboard artifact (in Claude Code, the Artifact tool's asset upload), with the same file names.
4. **Point the datasets at them** in the end-of-day step's write: update each dataset doc's `source.url` to its new asset's URL, exactly as the upload returned it, and set `updated` to `{at: <now, ISO UTC>, by: "IRRM check"}`. Pin each with its `if_version`.
5. **Delete the old assets** after that write succeeds, so old files don't pile up. If it fails, delete the new assets instead.

On a market holiday, add no rows.
