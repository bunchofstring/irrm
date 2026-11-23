# AMZN mean-reversion search (5 generations), 2026-11

The research behind the draft rule sets `strategy/references/weak-close-swing.md` and `strategy/references/gap-fill-overshoot.md`. Nothing here is live.

- **Data:** `irrm-515119.irrm_market_data`, AMZN `minute_bars` (1-minute, regular hours) and `daily_bars`. The 3-month T-bill yields come from Alpha Vantage `TREASURY_YIELD` (`tbill3m.csv`; November 2026 reuses October's value).
- **Range:** 2024-11-26 to 2026-11-20, 498 sessions. The first sessions from 2024-11-18 warm up the 5-minute indicators. In-sample: 2024-11-26 to 2026-04-21. Out-of-sample (the most recent 30%): 2026-04-22 to 2026-11-20.
- **Conventions:** `irrm-backtest` conventions v1, with c = 1 bp per side and a $5.00 start.
- **Departures from the conventions:**
  - On half days, end-of-day liquidation happens at 09:50 PT.
  - Take-profit and signal exits are decided on the latest completed 1-minute close and fill at the next 1-minute open, rather than at a live bid.
  - The range is slightly under 2 years, because 1-minute AMZN bars before 2024-11-18 are not available from Massive (plan limit), Robinhood (filler bars only) or Alpha Vantage (premium endpoint).
- **Files:**
  - `engine.py` is the simulator and metrics.
  - `strategies.py` holds the three families: A = intraday band reclaim, B = opening-gap fill, C = daily weak-close swing.
  - `genN.py` and `genN.json` hold each generation's variants and in-sample results. Generation 1 is `gen1.py`, and the family-A probe is `probe_a.py`.
  - `learn3.py` is the regime diagnostics behind generation 4.
  - `final.py` and `final.json` are the finalists' full, in-sample and out-of-sample metrics.
- **Re-running:** the scripts read `data/amzn_1m.pkl` and `data/amzn_daily.pkl` under `BASE` (see `engine.py`), built from the BigQuery tables above. Set `BASE` to a working folder before running them.
