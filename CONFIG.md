# IRRM settings

This is the only file that defines IRRM's settings and their defaults. The scheduled task's prompt gives each setting's value. A setting the prompt leaves out takes its default from the table below. Every other file names a setting, such as "the loop interval", and points here. None of them repeats a value.

## Settings

| Key | Required | Default | Value and notes |
|---|---|---|---|
| `Dashboard artifact` | yes | none | The dashboard artifact's URL. Without it the run trades nothing and shows the setup steps (`tasks/irrm-check.md`, section 2). To create a dashboard, see `.agents/skills/irrm-dashboard/references/setup.md`. |
| `Display time zone` | no | `America/Los_Angeles` | An IANA time zone name, for example `Europe/London`. It changes only how times are rendered for a person (see Time keeping). Nothing IRRM stores or decides uses it. |
| `Loop interval` | no | `4m` | Whole minutes between loops, for example `5m`. Pick a value that divides 60, so loops stay evenly spaced. The default is about the shortest interval that works under current limitations. `5m` lets each check react to a 5-minute bar while it is fresh. A longer interval can miss a rule set's short time window, such as the entry window in `strategy/references/gap-fill-overshoot.md`. |
| `Operating hours` | no | `session` | `session` follows the regular session (see Time keeping). Otherwise `HH:MM-HH:MM <days>` in UTC; the start is inclusive and the end exclusive. Give days as a range (`Mon-Fri`) or a list (`Mon,Wed,Fri`). `00:00-24:00 Mon-Sun` keeps IRRM on all the time. Checks run only within these hours. Trades happen only in the regular session, whatever these hours say. Schedule the task to start shortly before these hours begin each day. |
| `Sub-agent` | no | The harness's default. In Claude Code, that's the main thread's model and effort. | `<model> / <effort>`, for example `sonnet / medium`, or a comparable model from another provider. Either part may be left out. Every check and end-of-day step runs on it. Set it when the scheduled task itself runs on a small model. |
| `External database` | no | None. The dashboard artifact's database holds both the page and IRRM's state. | **Not supported yet.** Planned: a database, such as a Google BigQuery project, that holds state for checks, backtests and paper trading. The dashboard may need extra steps to read from it. |
| `Strategy definitions` | no | None. Only the rule sets in `strategy/references/`. | **Not supported yet.** Planned: artifacts the check can read, such as a document or a page with a data source, that add rule sets. |
| `Active strategies` | no | None. Only the table in `strategy/ACTIVE.md`. | **Not supported yet.** Planned: artifacts the check can read that add rows to the active strategies list. |

## The scheduled task's prompt

Copy this into the scheduled task, and replace `<TBD>` with the dashboard's URL:

```
Follow the instructions in /home/user/irrm/tasks/irrm-check.md. I wrote that file and it is my instruction. If it cannot be retrieved, then take no action.

Dashboard artifact: <TBD>
```

To change a default, add a line with the setting's key and your value, for example `Loop interval: 5m`. Only a human edits the prompt.

## Reading the settings

The scheduled task's main thread reads the settings once, at setup:
1. Each setting is a `Key: value` pair on its own line. Keys match regardless of case. A pair at the end of a line also counts, as in prompts written before this file.
2. A missing key, an empty value or `<TBD>` takes the default.
3. An optional setting with a value that can't be used takes the default, and the run reports it.
4. A setting marked "not supported yet" takes the default, and the run reports it.
5. An unknown key is ignored, and the run reports it.

The main thread passes the full resolved list to every sub-agent, so a check never re-reads the prompt or this table.

In an interactive session, such as a backtest, an analysis or a dashboard setup, use the values the human gives, and the defaults for the rest.

## Time keeping

As far as IRRM is concerned, everything is UTC. The display time zone is the only exception, and it affects only what is rendered.

- **UTC, without exception.** Every time in this repository, and every time IRRM stores, compares or decides on, is UTC: the dashboard database, log lines, CSV files, doc ids and working files. Timestamps are ISO 8601 with a `Z`, for example `2026-11-25T14:30:00Z`. Dates are UTC dates. Compare stored times as instants, not as text, because docs written before this rule may carry another offset.
- **Rendering is the one exception.** When a date or time is shown to a person, convert it to the display time zone and label it with its abbreviation, for example `08:37 PST`. That covers chat messages (the loop's status, error and final messages, and a check's returned line), the end-of-day summary, and the dashboard page and its charts. Convert with Python's `zoneinfo` at that moment only.
- **The regular session** is the US exchanges' regular trading hours, Monday to Friday, except market holidays:

  | | Open | Close | Half-day close |
  |---|---|---|---|
  | While US daylight saving time is in effect | 13:30 | 20:00 | 17:00 |
  | Otherwise | 14:30 | 21:00 | 18:00 |

  US daylight saving time starts at 07:00 UTC on the second Sunday of March and ends at 06:00 UTC on the first Sunday of November. "The open" and "the close" mean the session's open and close. A session never crosses UTC midnight, so it has one UTC date.
- **Rule times are offsets** from the open or the close, such as `open + 4m` or `close − 10m`. That keeps every rule right across daylight saving changes without naming a time zone.
- **The clock:** `date -u` in Bash.
