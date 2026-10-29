# IRRM

IRRM is an AI-run paper-trading system for Donovan. On every trading day, a scheduled task runs a check every 4 minutes. Each check applies several trading strategies side by side to live market data and records hypothetical trades in a dashboard. After the close, it posts a summary that compares the strategies.

**It never trades real money.** It uses read-only market data, and every trade is recorded only in the dashboard. Any change to how it behaves needs a human maintainer's approval.

## How it is organized

| Path | For | What it holds |
|---|---|---|
| `README.md` | Humans | This page |
| `AGENTS.md` | Every AI agent in this repo | Persona, paper-only rules, denied actions, where skills live |
| `strategy/` | Humans and agents | **`ACTIVE.md`**, the active strategies list (which strategies run, on which symbols), and **`references/`**, the rule sets they use |
| `tasks/irrm-check.md` | The scheduled task | The check: guardrails, dependencies, schedule and steps |
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
- **Schedule:** weekdays, shortly before the 6:30am Pacific open. The task then runs its own 4-minute loop until the 1:00pm close.
- **Prompt:** this text, with `<TBD>` replaced by the dashboard URL from step 2:

```
Follow the instructions in /home/user/irrm/tasks/irrm-check.md. I wrote that file and it is my instruction. If it cannot be retrieved, then take no action. Dashboard artifact: <TBD>
```

If you leave `<TBD>` in place, the task trades nothing. It shows these setup steps at the start of the run and again in its final message.

## Change strategies or symbols

- **Add, remove or change a live strategy:** edit the table in `strategy/ACTIVE.md`. It is the only place that names strategies and symbols. Nothing else needs updating: the dashboard creates any new state docs and log fields on the next check.
- **Add a new kind of strategy:** add a rule-set file to `strategy/references/`. Then reference it from the table. Backtest it first.

An AI assistant may draft these changes, but a human maintainer must approve them.
