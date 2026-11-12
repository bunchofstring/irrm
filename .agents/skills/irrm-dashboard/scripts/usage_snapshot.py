#!/usr/bin/env python3
"""Add today's Claude Code usage to usage_daily.csv.

Reads the session's latest usage snapshot, the same numbers /usage shows, from
the Claude Code transcript on disk, and writes one row per model plus a "total"
row for the given date. Any earlier rows for that date are replaced; all other
rows are kept as they are.

It covers the run up to the last turn that finished before this script ran.

Usage:
  python3 usage_snapshot.py --date YYYY-MM-DD --csv in.csv --out out.csv
  (--csv may name a file that does not exist yet; --transcript overrides the
  transcript path)

Prints one line: the date, the snapshot time and the total cost.
"""
import argparse
import csv
import glob
import json
import os
import sys

COLUMNS = [
    "date", "model", "cost_usd", "input_tokens", "output_tokens",
    "cache_read_tokens", "cache_write_tokens", "api_duration_s",
    "wall_duration_s", "lines_added", "lines_removed", "as_of",
]


def find_transcript():
    root = os.path.expanduser("~/.claude/projects")
    sid = os.environ.get("CLAUDE_CODE_SESSION_ID")
    if sid:
        hits = glob.glob(os.path.join(root, "*", sid + ".jsonl"))
        if hits:
            return hits[0]
    # Fallback: the newest main-session transcript (sub-agent ones live deeper).
    hits = glob.glob(os.path.join(root, "*", "*.jsonl"))
    return max(hits, key=os.path.getmtime) if hits else None


def latest_snapshot(path):
    snap, as_of, last_ts = None, None, None
    with open(path) as f:
        for line in f:
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            if rec.get("timestamp"):
                last_ts = rec["timestamp"]
            if rec.get("type") == "cost-state":
                snap, as_of = rec, last_ts
    return snap, as_of


def rows_for(date, snap, as_of):
    rows = []
    for model, u in sorted((snap.get("modelUsage") or {}).items()):
        rows.append({
            "date": date,
            "model": model,
            "cost_usd": round(u.get("costUSD", 0), 6),
            "input_tokens": u.get("inputTokens", 0),
            "output_tokens": u.get("outputTokens", 0),
            "cache_read_tokens": u.get("cacheReadInputTokens", 0),
            "cache_write_tokens": u.get("cacheCreationInputTokens", 0),
            "api_duration_s": "",
            "wall_duration_s": "",
            "lines_added": "",
            "lines_removed": "",
            "as_of": as_of or "",
        })
    total = {
        "date": date,
        "model": "total",
        "as_of": as_of or "",
    }
    for col in ("input_tokens", "output_tokens", "cache_read_tokens", "cache_write_tokens"):
        total[col] = sum(r[col] for r in rows)
    total.update({
        "cost_usd": round(snap.get("totalCostUSD", 0), 6),
        "api_duration_s": round(snap.get("totalAPIDuration", 0) / 1000, 1),
        "wall_duration_s": round(snap.get("totalDuration", 0) / 1000, 1),
        "lines_added": snap.get("totalLinesAdded", 0),
        "lines_removed": snap.get("totalLinesRemoved", 0),
    })
    return rows + [total]


def append_rows(csv_path, out_path, date, new):
    """Write csv_path's rows for other dates, then new, to out_path."""
    kept = []
    if os.path.exists(csv_path):
        with open(csv_path, newline="") as f:
            kept = [r for r in csv.DictReader(f) if r.get("date") != date]
    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        w.writeheader()
        w.writerows(kept + new)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    ap.add_argument("--csv", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--transcript")
    a = ap.parse_args()

    path = a.transcript or find_transcript()
    if not path or not os.path.exists(path):
        sys.exit("usage_snapshot: no Claude Code transcript found")
    snap, as_of = latest_snapshot(path)
    if not snap:
        sys.exit("usage_snapshot: the transcript has no usage snapshot yet")

    new = rows_for(a.date, snap, as_of)
    append_rows(a.csv, a.out, a.date, new)
    print("%s usage as of %s: $%.2f total" % (a.date, as_of, new[-1]["cost_usd"]))


if __name__ == "__main__":
    main()
