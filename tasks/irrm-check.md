# IRRM check

This is the scheduled task. It runs a loop every 4 minutes until the close. Each loop decides whether a check is warranted and, if it is, starts a sub-agent to perform it. The check itself is described in `tasks/irrm-check-procedure.md`.

**Do not open `tasks/irrm-check-procedure.md` in the main thread.** It is opened only when a check (or the end-of-day step) is warranted, and only by the sub-agent that performs it. The main thread just passes its path.

Work unattended. When in doubt, take NO ACTION and log why. The loop itself never trades: it calls no market-data, order or dashboard tool.

## 1. Inputs

- **Dashboard artifact URL:** given in the scheduled task's prompt as `Dashboard artifact: <url>`.
- **If the prompt gives no URL**, or gives `<TBD>`:
  - At the start of the run, display the setup instructions below.
  - Keep the schedule running until the close, but start no check and no end-of-day step.
  - Repeat the setup instructions in the final message.

  > **IRRM needs a dashboard.** No dashboard artifact URL was given, so no trades were checked or recorded.
  > 1. In an interactive session in this repository, ask the agent to set up the IRRM dashboard (skill `irrm-dashboard`).
  > 2. Copy the new dashboard artifact's URL.
  > 3. Edit this scheduled task's prompt and replace `<TBD>` after `Dashboard artifact:` with that URL. A human must approve this change.

## 2. Dependencies

These are what the loop needs. The check confirms its own dependencies (market data, the dashboard database and so on) each time it runs. Before the first loop, confirm that each one below is available. If a required one is missing, log which and why, start no check, and name it in the final message.

| Need | Required | Suggested connector or tool |
|---|---|---|
| Clock in Pacific time | yes | Bash: `TZ=America/Los_Angeles date` |
| Recurring schedule | yes | `/loop` |
| Keep-alive between loops | yes | A background command, for example Bash `sleep` with `run_in_background` (section 5) |
| Sub-agents | no | In Claude Code, the Agent tool. Without it, the session opens `tasks/irrm-check-procedure.md` and performs each warranted check itself. |

Load a tool's schema before calling it (in Claude Code, with ToolSearch).

## 3. When a check is warranted

- **Regular hours:** weekdays 6:30am–1:00pm Pacific (America/Los_Angeles).
- **Loops and checks are different things.**
  - A **loop** fires every 4 minutes. The main thread (the scheduled session) runs it.
  - A **check** is the trading work: one pass over every active strategy. A loop performs a check only when it is warranted.
  - Loops run whenever the routine runs, including outside regular hours. They continue until regular hours end, then the run ends itself gracefully.
- **A check is warranted** when the time is within regular hours, the prompt gives a dashboard URL, and every required dependency in section 2 is available.
- **The end-of-day step is warranted** in the first loop at or after the 1:00pm close, if today had regular hours and the prompt gives a dashboard URL.
- **Otherwise,** the loop does nothing and ends its turn.

## 4. One loop

**Schedule:** `/loop 4m Run ONE IRRM loop`. Run the first loop at the start of the session, then let the schedule fire the rest. Loops continue until the close, even if there is an error.

Each loop has two steps, in this order. The second step starts only after the first one finishes.
1. The main thread gets the current Pacific time.
2. If a check is warranted (section 3), the main thread starts a sub-agent to perform one check. If instead the end-of-day step is warranted, it starts a sub-agent for that step. If the time is at or after 1:00pm, or today has no regular hours, the loop then ends the run.

**Starting a sub-agent:**
- Start a fresh sub-agent on the Sonnet model, whatever model the session itself runs, and wait for it to finish.
- **Wait for it in the same turn.** Start the sub-agent in blocking mode, so the main thread does nothing else until it is done and gets its report within the loop's own turn. Sub-agents always start synchronously, never in the background. Name the sub-agent's type (a general-purpose agent) and model (Sonnet) explicitly instead of relying on defaults. For example, in Claude Code: the Agent tool with `subagent_type: "general-purpose"`, `model: "sonnet"` and `run_in_background: false`.
- **For a check,** give it this prompt: "Run ONE IRRM check as `tasks/irrm-check-procedure.md` describes. Dashboard artifact: `<url>`. Do not sleep, start background commands or change the schedule." If the previous check's line named a folder of unwritten JSON files, add: "Unwritten batch: `<folder>`."
- **For the end-of-day step,** give it this prompt: "Run the IRRM end-of-day step as `tasks/irrm-check-procedure.md` describes. Dashboard artifact: `<url>`. Do not sleep, start background commands or change the schedule."

**What comes back:**
- A check returns ONE line that ends in CONTINUE or END RUN, for example `08:37 PT — no trades, no errors — CONTINUE`. The per-check lines are on the dashboard, so the main thread does not display a line that reports no error.
- On END RUN, the main thread posts the reason and ends the run.
- The end-of-day step returns the day's summary. The main thread makes it the final message and ends the run.

## 5. Keep-alive and ending the run

- **The keep-alive:** never leave the session with nothing running. If no turn and no background command is running, the cloud container can be shut down, and the schedule dies with it. One long background command keeps it running between loops, instead of a new sleep in every loop.
  - **Start it once,** at the start of the run, before the first loop: a background command that sleeps for just under 2 hours, labeled "Keep-alive". In Claude Code: Bash `sleep 7080` with `run_in_background: true` and `timeout: 7200000` (2 hours, the most a background command may run).
  - **When it ends,** start a new one the same way, and display nothing. This happens about 3 times a day.
  - **Only one at a time.** Start a new keep-alive only when the previous one has ended. Never start one in a loop for any other reason.
- **Ending the run** is always graceful: delete the schedule, stop the keep-alive (in Claude Code, TaskStop), and post the final message. The run ends after the end-of-day step, on a day with no regular hours, or when a check returns END RUN (a market holiday, or 3 consecutive data errors).

## 6. Silence

The main thread is silent unless there is an error. Every line it writes is re-read at each later loop, so it displays text only to report an error: a missing dashboard URL or dependency (section 2), a sub-agent that fails, or a sub-agent line that reports an error or END RUN. A loop that goes as planned ends its turn with no text at all: no status line, no summary of the check, no note about the keep-alive. The one other message is the final message when the run ends. It names any dependency a check reported missing.
