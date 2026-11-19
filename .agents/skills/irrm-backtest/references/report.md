# Backtest report

For each rule set and its benchmark, side by side:
- **Returns:** total return (net, plus the cost-sensitivity table), annualized return, and returns by calendar year and month
- **Risk:** annualized volatility, largest drawdown (depth, dates, recovery) and worst day
- **Risk-adjusted:** Sharpe ratio and Sortino ratio (both on excess daily returns, annualized), and Calmar ratio (annualized return ÷ largest drawdown)
- **Against the benchmark:** beta, annualized alpha, correlation and information ratio, from daily returns
- **Trading:** number of trades (closed and open), hit rate, average win and average loss, profit factor (gross wins ÷ gross losses), largest loss, mean trade return with its t-statistic, and time in the market (the share of regular-session minutes and the share of nights with an open position)
- **Money:** ending balance and total P&L in dollars, and P&L per trading day
- **Setup:** the conventions version, the range (first and last check), the cost `c`, data sources, any data gaps and any departures from the conventions

A backtest is evidence, not a forecast. Say what could make live results differ, such as fills, data quality or a regime the range does not cover.
