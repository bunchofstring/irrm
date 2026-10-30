---
name: irrm-dashboard
description: The IRRM dashboard artifact and its shared database, which persists IRRM state between days. Use to read or write IRRM state during a check, or to create or rebuild the dashboard.
---

# IRRM dashboard

The dashboard is an artifact with a shared database. Its page shows the paper-trading record. Its database holds every strategy's state, the daily logs and every trade, so state survives from one day to the next.

Read and write the database with the ArtifactData tool, using the dashboard artifact's URL. In Claude Code, load the tool with ToolSearch `select:ArtifactData`.

## Read only when needed

- **`references/schema.md`:** collections, doc shapes, versioning and the one-batch write. Read it whenever you read or write IRRM state, including at every IRRM check.
- **`references/csv.md`:** the two CSV files that feed the dashboard's charts, and how to update them. Read it at every IRRM check.
- **`references/setup.md`:** how to create or rebuild the dashboard artifact. Read it only when a human asks to set up or change the dashboard, or when a check reports that no dashboard URL was given.
