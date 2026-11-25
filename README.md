# IRRM

IRRM is an AI-run paper-trading system for Donovan. On every trading day, a scheduled task runs a check every few minutes. Each check applies several trading strategies side by side to live market data and records hypothetical trades in a dashboard. After the close, it posts a summary that compares the strategies.

**It never trades real money.** It uses read-only market data, and every trade is recorded only in the dashboard. Any change to how it behaves needs a human maintainer's approval.

## How it is organized

| Path | For | What it holds |
|---|---|---|
| `README.md` | Humans | This page |
| `AGENTS.md` | Every AI agent in this repo | Persona, paper-only rules, denied actions, where skills live |
| `CONFIG.md` | Humans and agents | **The settings:** every setting's definition and default, the scheduled task's prompt, and the time-keeping rules |
| `strategy/` | Humans and agents | **`ACTIVE.md`**, the active strategies list: which strategies run, on which symbols |
| `tasks/irrm-check.md` | The scheduled task | The loop: schedule, market hours, when a check is warranted, keep-alive |
| `tasks/irrm-check-procedure.md` | The check's sub-agent | The check: guardrails, dependencies, steps and end of day. Opened only when a check is warranted |
| `.agents/skills/` | Agents, as needed | Skills, one folder each. Each skill keeps its details in files that load only when needed |

To see what each skill covers, browse `.agents/skills/`: every `SKILL.md` starts with a one-line description. The skills follow the open Agent Skills format, so they aren't tied to one AI provider. `AGENTS.md` tells agents to look there.

## Set up IRRM

### 1. Connect the services
In the AI app that will run the task, connect:
- **Market data (read-only):** any provider that gives quotes plus 1- and 5-minute bars, for example Massive or Robinhood. IRRM uses only read tools.
- **Artifacts with a database:** these hold the dashboard.

### 2. Create the dashboard
Open an interactive session in this repository and ask: *"Set up the IRRM dashboard."* The agent creates it and gives you the new artifact's URL.

### 3. Create the scheduled task
Create a scheduled task with:
- **Repository:** this repo.
- **Connectors:** the ones from step 1.
- **Schedule:** shortly before the operating hours begin, on each day they include. With the default, that's before the earlier of the two UTC opening times in `CONFIG.md`. The task then runs a loop at the loop interval, performs a check in each loop within the operating hours, posts the summary after the close, and ends itself.
- **Model:** a smaller, cheaper model is enough. The task only runs the loops; every check runs in a sub-agent, on the model the `Sub-agent` setting names.
- **Prompt:** the template in `CONFIG.md`, with `<TBD>` replaced by the dashboard URL from step 2.

`CONFIG.md` lists every setting with its default, including the loop interval, the operating hours and the display time zone. To change one, add a `Key: value` line to the prompt. If you leave `<TBD>` in place, the task trades nothing. It shows these setup steps at the start of the run and again in its final message.

## Change strategies or symbols

- **Add, remove or change a live strategy:** edit the table in `strategy/ACTIVE.md`. It is the only place that names strategies and symbols. Give each row a display name for the dashboard's charts. Nothing else needs updating: the next check creates any new state docs and log fields, and adds the strategy to the chart data.
- **Add a new kind of strategy:** ask an agent in this repository to help you design one. It drafts a rule set and backtests it for you to review. Then reference it from the table.

An AI assistant may draft these changes, but a human maintainer must approve them.
