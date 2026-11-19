---
name: irrm-backtest
description: Backtest IRRM rule sets by replaying them over historical bars with IRRM's indicator and paper-fill rules. Use when a human asks how a strategy would have performed, or wants to compare rule sets, symbols or parameters before changing the live strategies.
---

# IRRM backtest

Replay one or more rule sets over historical data. The "rule set" column of `strategy/ACTIVE.md` says where each rule set file lives. Use:
- `irrm-indicators` for the indicators
- `irrm-paper-trading` for sizing, stop orders and end-of-day liquidation

## Rules

- **Read-only.** Fetch historical bars with read-only market-data tools only. Never use a tool that places, previews, reviews, changes, cancels or exercises an order, or moves money.
- **Never touch the live dashboard's state.** Do not write to the dashboard that the scheduled check uses.
- **Results live in the session.** When the backtest is done, ask the human whether they want the results in a dashboard artifact. If they do, use a separate artifact, never the live one.

## Method

1. **Agree the scope with the human:** rule sets, symbols, date range, starting balance (default $5.00 principal) and cap (default $100.00).
2. **Fetch the data.** Get 5-minute regular-hours bars for the range, plus enough earlier history to warm up the indicators (at least 400 completed bars). Get 1-minute bars for fills and the stop fill test, daily bars for valuation, dividends for each symbol, and the 3-month Treasury bill yield. See **Data** below.
3. **Step through the data.** Step through each check on the check grid, and apply each rule set as the live check would. Follow **Conventions** below exactly, so that two backtests of the same scope give the same numbers.
4. **State any departure.** If the data or the human's request forces a departure from a convention, say which one, why, and how it may flatter or penalize the results.
5. **Report** as **Report** below describes.

## Data

- `minute_bars`: 1-minute regular-hours bars. `ts` is the bar's **start** time in UTC, so the bar stamped 12:40 PT covers 12:40:00–12:41:00. Its open is the first price after 12:40:00, and it is completed at 12:41. Convert to Pacific with `America/Los_Angeles`.
- `daily_bars`: daily regular-hours bars, split-adjusted. `close` is the official close.
- `earnings_dates`: earnings report dates.

Get dividends (ex-date and amount) and the 3-month Treasury bill yield from a read-only market-data tool, for example Alpha Vantage `DIVIDENDS` and `TREASURY_YIELD` (maturity 3month).

Build 5-minute bars from the 1-minute bars when needed. Check coverage first: each full day has 390 1-minute bars and each half day has 211 (last bar 09:59 PT). Treat a day with any other count as a data gap and report it. Never fill a gap with data from outside the bar's time.

## Conventions (v1)

These follow common institutional backtesting practice and the GIPS valuation and return rules. They remove the choices that otherwise make two backtests of the same scope disagree.

### Check grid
- Checks run at Pacific clock times every 4 minutes from 06:30 (06:30, 06:34, …), plus the start time of every time window a rule set names (for example 09:00, 12:40, 12:50). The last check of a day is the last grid time before the close (13:00, or 10:00 on half days).
- A rule that fires "at the first check at or after T" fires at T. A rule limited to a window fires at the first check in that window.

### No look-ahead
- A decision at check time T uses only data completed by T: the 1-minute bar that started at T − 1 minute and earlier, and 5-minute bars that ended at or before T. Never use a bar that ends after T.
- Use only data that was known at T. Earnings dates, dividends and other events count only from when they were announced.

### Fills
- **Price.** A decision at T fills at the **open of the 1-minute bar that starts at T**: the next tradeable price after the decision. Stop fills follow `irrm-paper-trading/references/stop-orders.md`, using the 1-minute bars between checks.
- **Transaction costs.** Charge a cost of `c` per side: a buy fills at price × (1 + c) and a sell at price × (1 − c). Commissions are $0.
  - When historical bid and ask quotes are available, set `c` to the median half-spread at the strategy's check times over the range, plus 0.5 basis points for slippage.
  - Otherwise, use the default: **c = 1 basis point** for large, liquid US stocks and ETFs such as AMZN and QQQ. This is about 2–4 times the half-spread of a one-cent quote at their prices, and IRRM's orders are too small to move the market. Use a larger `c` for less liquid symbols.
  - Say which `c` you used and where it came from.
- **Cost sensitivity.** Report the total return at c = 0 (gross), 1, 2 and 5 basis points, and the **break-even costs**: the `c` at which the net return falls to zero, and the `c` at which it falls to buy & hold (or "none" if it trails buy & hold even at zero cost). High-turnover strategies are very sensitive to cost, so judge them on this table rather than on the gross return.

### Corporate actions and cash
- Prices are split-adjusted.
- A position held at the close before an ex-dividend date receives the dividend in cash on the ex-date.
- Uninvested cash earns no interest, matching the paper account. Risk-adjusted metrics still use returns in excess of the risk-free rate (below).

### Valuation and returns
- **Daily valuation.** Equity is the cash balance plus any open position valued at the day's official close (`daily_bars.close`; if missing, the last 1-minute close). Record equity every trading day.
- **Range end.** A strategy may buy only at checks inside the range. A position still open at the end of the range is **marked to the final official close, not sold**. Report it as one open trade, not a win or a loss. No data after the range is used.
- **Time-weighted return.** The daily return is equity today ÷ equity at the previous close − 1. The first day starts from the starting balance. A period's return (month, year, full range) links the daily returns geometrically. Periods are calendar periods, and a trade belongs to the period of its exit date.
- **Annualize** with 252 trading days. Annualize returns only for ranges of at least one year.
- **Risk-free rate.** Use the 3-month Treasury bill yield for each month, ÷ 252 per trading day.

### Benchmark
Buy & hold the same symbol, as a total return: buy at the first check of the range with the same fill and cost rules and the same starting balance, reinvest dividends at the ex-date's close, and value at the same daily closes. Report the same metrics for it. When the human names another benchmark (for example QQQ), report that one as well.

### Statistics and validity
- Measure drawdown on daily equity, peak to trough, with the starting balance as the first peak. Report its depth, its peak and trough dates, and when it recovered (or "not recovered").
- Report the t-statistic of the mean trade return. Call a result statistically meaningful only if |t| ≥ 2.
- When the backtest is used to choose parameters or between rule sets, choose them on the earlier part of the data and report the most recent 30% (at least 6 months) separately as out-of-sample. Say how many variants were tried, since trying many variants inflates the best one.
- Say when the range is under 2 years or has fewer than 100 trades, as results that short are weak evidence.

### Rounding
Follow `irrm-paper-trading` for share rounding. Report returns in percent to 2 decimals, ratios to 2 decimals, and balances to the cent.

Change these conventions only with a human maintainer's approval. Bump the version when you do, so older results can be told apart.

## Report

For each rule set and its benchmark, side by side:
- **Returns:** total return (net, plus the cost-sensitivity table), annualized return, and returns by calendar year and month
- **Risk:** annualized volatility, largest drawdown (depth, dates, recovery) and worst day
- **Risk-adjusted:** Sharpe ratio and Sortino ratio (both on excess daily returns, annualized), and Calmar ratio (annualized return ÷ largest drawdown)
- **Against the benchmark:** beta, annualized alpha, correlation and information ratio, from daily returns
- **Trading:** number of trades (closed and open), hit rate, average win and average loss, profit factor (gross wins ÷ gross losses), largest loss, mean trade return with its t-statistic, and time in the market (the share of regular-session minutes and the share of nights with an open position)
- **Money:** ending balance and total P&L in dollars, and P&L per trading day
- **Setup:** the conventions version, the range (first and last check), the cost `c`, data sources, any data gaps and any departures from the conventions

A backtest is evidence, not a forecast. Say what could make live results differ, such as fills, data quality or a regime the range does not cover.

## Changing strategies

A backtest never changes the live strategies. If the results support a change, propose it for a human maintainer to approve.
