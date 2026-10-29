# Dashboard database schema

This schema does not name any particular strategy or symbol. "Each active strategy" means each row of `STRATEGIES.md`. That row gives the strategy's id, symbol, rule set, state doc and log field.

## Versioning

- Keep each doc's `version`, and pass it as `if_version` on every write. Use the new version that each write returns.
- If a write fails on version, re-read the doc and redo the write.
- When creating a doc, pass no `if_version`.

## Collection "bot"

### Doc "check": bot-wide fields
- `updated_at`: ISO UTC time of the last completed check. Used to detect missed checks.
- `consecutive_errors`: the number of data errors in a row. Reset to 0 after a good check.

If the doc is missing, create it with `updated_at` null and `consecutive_errors` 0. While `updated_at` is null, there are no missed checks to log.

### One state doc per active strategy (named in its row)

Common fields:
- `symbol`
- `phase` ("paper")
- `balance`
- `principal` (5.00)
- `realized_pnl`
- `position` (null or an object, see below)
- `check_count`
- `last_sell_time` (ISO, null if none)
- `updated_at` (ISO UTC)

The strategy's rule set may add more fields.

If an active strategy's state doc is missing, create it with:
- the symbol from its row
- phase "paper"
- balance 5.00 and principal 5.00
- realized_pnl 0
- position null
- check_count 0
- last_sell_time null
- each extra field the rule set defines, set to null

### Position object

Common fields:
- `shares`
- `cost_price`
- `cost_basis`
- `entry_time`
- `peak_price`
- `last_bid`

Fields for rule sets that keep stops:
- `stop_price`
- `stop_reason`
- `stops` (every stop level)
- `stop_order: {type: "stop", trigger, placed_at, modified_at}`

The rule set defines its extra position fields, the keys of `stops`, and the values of `stop_reason`.

Definitions:
- cost_price = the per-share price paid (the ask at the paper fill).
- cost_basis = the total dollars spent (shares × cost_price).
- All stop levels are per-share prices derived from cost_price. The highest active level is the resting stop order's trigger.

### Updating a state doc each check

Update:
- check_count
- updated_at
- position, with all stop levels and last_bid
- balance
- realized_pnl
- last_sell_time
- the rule set's extra fields

## Collection "days": today's log

- **Doc id:** today's date as YYYY-MM-DD (Pacific).
- **Fields:** `{date, summary: "", <log field>: [lines…] for each active strategy}`.
- Create it at the first check of the day. If it already exists without an active strategy's log field, add that field as an empty array.

## Collection "trades": one doc per paper trade

- **Doc id:** `YYYYMMDD-HHMM-<strategy id>-<side>`, for example `20261019-0712-main-buy`.
- **Fields:**
  - `ts` (ISO UTC)
  - `strategy` (the strategy id)
  - `side` ("buy" or "sell")
  - `price`
  - `shares`
  - `amount`
  - `pnl` (sells only)
  - `reason`
  - `gap` (bool)

Trades are kept forever. The dashboard chart and the end-of-day summary build the cumulative P&L record from them.

## One batch per check

Write each check's changes in ONE `batch` call:
- `bot/check`
- every active strategy's state doc
- the day doc's full updated log fields
- any trade docs

Pin each existing doc with its `if_version`.
