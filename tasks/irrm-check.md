# IRRM check

This is the scheduled task: a loop that repeats at the loop interval until the end of the operating hours. Its only responsibilities are reading the settings, repetition, determining when a check is warranted, and triggering that check. It is intentionally ignorant of analysis, dashboards and trading. Work unattended.

**Open `tasks/irrm-check-procedure.md` only when a check (or the end-of-day step) is warranted** (section 4).

## 1. Setup (main thread, once per session)

Do these steps in order at the start of every scheduled session. Do not skip one. Setup runs once per session: a loop iteration skips this section.

1. **Read the settings** (section 2).
2. **Start the keep-alive** (section 6).
3. **Start the loop** (section 5).
4. **Confirm the loop.** Expect exactly one loop job.
   - If there is none, start the loop once more and confirm again.
   - If there is still none, post an error line that says the loop could not be started, and end the run (section 6).
   - If there is more than one, delete the newer duplicates and keep the oldest.
5. **Print the loop status** once: `LOOP started — job <id>, cron <cron>, next run <time> — settings: <the resolved settings, as Key: value pairs separated by semicolons>`. Omit the next run if it is not known. Add any setting that `CONFIG.md` says to report, and why. Write no state for it.
6. **Let the loop fire the rest of the iterations.**

## 2. Settings

`CONFIG.md` defines every setting, its default, and how to read them from this scheduled task's prompt. Read them once, as its "Reading the settings" section describes, and keep the resolved list for the whole run. Everything below that names a setting (the dashboard artifact, the loop interval, the operating hours, the display time zone, the sub-agent) means its resolved value.

If the dashboard artifact is missing, display these setup instructions at the start of the run and repeat them in the final message:

> **IRRM needs a dashboard.** No dashboard artifact URL was given, so no trades were checked or recorded.
> 1. In an interactive session in this repository, ask the agent to set up the IRRM dashboard (skill `irrm-dashboard`).
> 2. Copy the new dashboard artifact's URL.
> 3. Edit this scheduled task's prompt and replace `<TBD>` after `Dashboard artifact:` with that URL. A human must approve this change.

## 3. Dependencies

Before the first loop, confirm that each dependency below is available. The check confirms its own dependencies each time it runs.

| Need | Required | Suggested connector or tool |
|---|---|---|
| Clock | yes | As `CONFIG.md` (Time keeping) describes |
| Recurring loop that can be started, listed and deleted | yes | In Claude Code, the `loop` skill, `CronList` and `CronDelete` (section 5) |
| Keep-alive between loops | yes | A background command (section 6) |
| Sub-agents | no | In Claude Code, the Agent tool. Without it, the session opens `tasks/irrm-check-procedure.md` and performs each warranted check itself. |

Load a tool's schema before calling it (in Claude Code, with ToolSearch).

## 4. When a check is warranted

A **check** is the trading work: one pass over every active strategy. Compare the UTC clock with the operating hours and with the close (`CONFIG.md`, Time keeping).
- **A check is warranted** in a loop within the operating hours, if a dashboard artifact is set and every required dependency in section 3 is available. The check itself decides whether the market is open.
- **The end-of-day step is warranted** once per session, in the first loop at or after the close, or at or after the end of the operating hours if they end before the close. It needs a session that had regular hours and a dashboard artifact.

## 5. One loop

**Loop:** a recurring job, for this session only, that fires at the loop interval with the prompt `Run ONE IRRM loop`. Setup (section 1) starts it, runs its first iteration immediately and confirms it. The loop fires the rest, including outside the operating hours and after an error, until the run ends (section 6). In Claude Code, start it with the `loop` skill through the Skill tool, with `args: "<loop interval> Run ONE IRRM loop"` (the slash command `/loop <loop interval> Run ONE IRRM loop`).
- **Confirm it:** list the session's recurring jobs and keep those whose prompt contains `Run ONE IRRM loop`.
- **Delete it as needed:** remove a job by its id. In Claude Code: `CronDelete`.

Each loop has two steps. The second starts only after the first finishes.
1. The main thread (the scheduled session) gets the current time.
2. If a check or the end-of-day step is warranted, it starts a sub-agent to perform it. Then, if section 6 says the run ends, it ends the run.

**Starting a sub-agent:** start a fresh general-purpose sub-agent with the model and effort the `Sub-agent` setting names. Name only the parts it names; leave the rest to the harness's default. Start it in blocking mode, never in the background, so the main thread does nothing else until it finishes and gets its report within the loop's own turn. In Claude Code: the Agent tool with `subagent_type: "general-purpose"`, `run_in_background: false`, and `model` and `effort` only when the setting names them. Give it this prompt:

> Run ONE IRRM check as `tasks/irrm-check-procedure.md` describes. Settings: `<every resolved setting, one Key: value per line>`. Do not sleep, start background commands or change the loop.

For the end-of-day step, replace "ONE IRRM check" with "the IRRM end-of-day step". For a check, if the previous check's line named a folder of unwritten JSON files, add "Unwritten batch: `<folder>`."

**What comes back:** a check returns ONE line that ends in CONTINUE or END RUN, for example `08:37 PST — no trades, no errors — CONTINUE`. The end-of-day step returns the day's summary, which becomes the final message.

## 6. Keep-alive and ending the run

- **Keep-alive:** if no turn and no background command is running, the cloud container can be shut down, and the loop dies with it. So keep exactly one long background command running between loops, instead of a sleep in every loop. Start it in setup (section 1, step 2), and start a new one only when the previous one ends (about 3 times a day): a background command labeled "Keep-alive" that sleeps for just under 2 hours. In Claude Code: Bash `sleep 7080` with `run_in_background: true` and `timeout: 7200000` (2 hours, the most a background command may run).
- **The run ends** in the first loop at or after the end of the operating hours (after any end-of-day step that loop warrants), on a day the operating hours exclude, or when a check returns END RUN (a market holiday, or 3 consecutive data errors). End it gracefully: delete the loop, stop the keep-alive (in Claude Code, TaskStop), and post the final message.

## 7. Silence

Every line the main thread writes is re-read at each later loop, so it displays text only:
- **once at setup,** the loop status line (section 1, step 5).
- **to report an error:** a loop that could not be started, a missing dashboard artifact or dependency (and why), a sub-agent that fails, or a sub-agent line that reports an error or END RUN (post the reason).
- **in the final message,** which names any missing dependency, including any a check reported.

Render every time in these lines in the display time zone. A loop that goes as planned ends its turn with no text at all: no status line, no summary of the check, no note about the keep-alive.
