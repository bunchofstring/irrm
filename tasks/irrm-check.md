# IRRM check

This is the scheduled task: a loop that repeats every 4 minutes until the 1:00pm Pacific close. Its only responsibilities are repetition, determining when a check is warranted, and triggering that check. It is intentionally ignorant of analysis, dashboards and trading. Work unattended.

**Open `tasks/irrm-check-procedure.md` only when a check (or the end-of-day step) is warranted** (section 4).

## 1. Setup (main thread, once per session)

Do these steps in order at the start of every scheduled session. Do not skip one. Setup runs once per session: a loop iteration skips this section.

1. **Start the keep-alive** (section 6).
2. **Wait until the market is about to open.** Do a foreground sleep until 2 seconds before market open. This sleep is allowed. After the sleep ends, continue the steps below.
3. **Start the loop** (section 5).
4. **Confirm the loop.** Expect exactly one loop job.
   - If there is none, start the loop once more and confirm again.
   - If there is still none, post an error line that says the loop could not be started, and end the run (section 6).
   - If there is more than one, delete the newer duplicates and keep the oldest.
5. **Print the loop status** once: `Loop started — job <id>, cron <cron>, next run <time>`. Omit the next run if it is not known. Write no state for it.
6. **Let the loop fire the rest of the iterations.**

## 2. Inputs

The dashboard artifact URL is given in the scheduled task's prompt as `Dashboard artifact: <url>`. If the prompt gives no URL, or gives `<TBD>`, display these setup instructions at the start of the run and repeat them in the final message:

> **IRRM needs a dashboard.** No dashboard artifact URL was given, so no trades were checked or recorded.
> 1. In an interactive session in this repository, ask the agent to set up the IRRM dashboard (skill `irrm-dashboard`).
> 2. Copy the new dashboard artifact's URL.
> 3. Edit this scheduled task's prompt and replace `<TBD>` after `Dashboard artifact:` with that URL. A human must approve this change.

## 3. Dependencies

Before the first loop, confirm that each dependency below is available. The check confirms its own dependencies each time it runs.

| Need | Required | Suggested connector or tool |
|---|---|---|
| Clock in Pacific time | yes | Bash: `TZ=America/Los_Angeles date` |
| Recurring loop that can be started, listed and deleted | yes | In Claude Code, the `loop` skill, `CronList` and `CronDelete` (section 5) |
| Keep-alive between loops | yes | A background command (section 6) |
| Sub-agents | no | In Claude Code, the Agent tool. Without it, the session opens `tasks/irrm-check-procedure.md` and performs each warranted check itself. |

Load a tool's schema before calling it (in Claude Code, with ToolSearch).

## 4. When a check is warranted

**Regular hours** are weekdays 6:30am–1:00pm Pacific (America/Los_Angeles). A **check** is the trading work: one pass over every active strategy.
- **A check is warranted** in a loop within regular hours, if the prompt gives a dashboard URL and every required dependency in section 3 is available.
- **The end-of-day step is warranted** in the first loop at or after the 1:00pm close, if today had regular hours and the prompt gives a dashboard URL.

## 5. One loop

**Loop:** a recurring job, for this session only, that fires every 4 minutes with the prompt `Run ONE IRRM loop`. Setup (section 1) starts it, runs its first iteration immediately and confirms it. The loop fires the rest, including outside regular hours and after an error, until the run ends (section 6). In Claude Code, start it with the `loop` skill through the Skill tool, with `args: "4m Run ONE IRRM loop"` (the slash command `/loop 4m Run ONE IRRM loop`).
- **Confirm it:** list the session's recurring jobs and keep those whose prompt contains `Run ONE IRRM loop`.
- **Delete it as needed:** remove a job by its id. In Claude Code: `CronDelete`.

Each loop has two steps. The second starts only after the first finishes.
1. The main thread (the scheduled session) gets the current Pacific time.
2. If a check or the end-of-day step is warranted, it starts a sub-agent to perform it. Then, if section 6 says the run ends, it ends the run.

**Starting a sub-agent:** start a fresh general-purpose sub-agent on the Sonnet model, whatever model the session runs, naming both explicitly instead of relying on defaults. Start it in blocking mode, never in the background, so the main thread does nothing else until it finishes and gets its report within the loop's own turn. In Claude Code: the Agent tool with `subagent_type: "general-purpose"`, `model: "sonnet"` and `run_in_background: false`. Give it this prompt:

> Run ONE IRRM check as `tasks/irrm-check-procedure.md` describes. Dashboard artifact: `<url>`. Do not sleep, start background commands or change the loop.

For the end-of-day step, replace "ONE IRRM check" with "the IRRM end-of-day step". For a check, if the previous check's line named a folder of unwritten JSON files, add "Unwritten batch: `<folder>`."

**What comes back:** a check returns ONE line that ends in CONTINUE or END RUN, for example `08:37 PT — no trades, no errors — CONTINUE`. The end-of-day step returns the day's summary, which becomes the final message.

## 6. Keep-alive and ending the run

- **Keep-alive:** if no turn and no background command is running, the cloud container can be shut down, and the loop dies with it. So keep exactly one long background command running between loops, instead of a sleep in every loop. Start it in setup (section 1, step 1), and start a new one only when the previous one ends (about 3 times a day): a background command labeled "Keep-alive" that sleeps for just under 2 hours. In Claude Code: Bash `sleep 7080` with `run_in_background: true` and `timeout: 7200000` (2 hours, the most a background command may run).
- **The run ends** in the first loop at or after 1:00pm, on a day with no regular hours, or when a check returns END RUN (a market holiday, or 3 consecutive data errors). End it gracefully: delete the loop, stop the keep-alive (in Claude Code, TaskStop), and post the final message.

## 7. Silence

Every line the main thread writes is re-read at each later loop, so it displays text only:
- **once at setup,** the loop status line (section 1, step 4).
- **to report an error:** a loop that could not be started, a missing dashboard URL or dependency (and why), a sub-agent that fails, or a sub-agent line that reports an error or END RUN (post the reason).
- **in the final message,** which names any missing dependency, including any a check reported.

A loop that goes as planned ends its turn with no text at all: no status line, no summary of the check, no note about the keep-alive.
