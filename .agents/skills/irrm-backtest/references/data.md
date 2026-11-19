# Backtest data

- `minute_bars`: 1-minute regular-hours bars. `ts` is the bar's **start** time in UTC, so the bar stamped 12:40 PT covers 12:40:00–12:41:00. Its open is the first price after 12:40:00, and it is completed at 12:41. Convert to Pacific with `America/Los_Angeles`.
- `daily_bars`: daily regular-hours bars, split-adjusted. `close` is the official close.
- `earnings_dates`: earnings report dates.

Get dividends (ex-date and amount) and the 3-month Treasury bill yield from a read-only market-data tool, for example Alpha Vantage `DIVIDENDS` and `TREASURY_YIELD` (maturity 3month).

Build 5-minute bars from the 1-minute bars when needed. Check coverage first: each full day has 390 1-minute bars and each half day has 211 (last bar 09:59 PT). Treat a day with any other count as a data gap and report it. Never fill a gap with data from outside the bar's time.
