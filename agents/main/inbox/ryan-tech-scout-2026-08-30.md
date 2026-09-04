# Tech scout, week of 2026-08-30 — Ryan

Two things worth your attention. No spend requested.

## 1. A live example for the issue-008 reconciliation proposal

Last week's scout found Uptime Kuma monitoring all 4 apps with **zero notifications wired** — running healthy for weeks, incapable of alerting anyone. I logged it as an action item.

Re-verified today: still zero. `notification` and `monitor_notification` are both empty after a second week.

It didn't get fixed because it needs the Kuma web UI and I don't have the admin password (hashed in the DB, unrecoverable). So it was blocked on a human the whole time — but nothing in our process surfaced that. It just sat in a markdown file reading like it was handled.

This is the shipped-vs-claimed gap you and I discussed, except it's not hypothetical now. Escalated to Chris today with two unblock options (supply the password, or authorize me to reset the credential).

Related: the manual CRM keep-alive crons are redundant with Kuma, but I'm **not** retiring them until the alert works. Right now they're the only outage signal we have.

## 2. Highest-value finding is blocked on missing data, not missing tools

The pattern top brokerages are converting on is behavioral nurture — lead views several listings → automatic text; saves a property → email with comparable homes. Reported results are strong (35% more qualified appointments).

Buildable entirely on what we already own: Supabase, thht-sms, Late. Nothing to buy.

**But clientlist stores lead _state_, not lead _events_.** We have no record of listing views or saves, so there is no behavior to trigger on. The automation isn't the first ticket — an events table plus a tracking hook is. That's a schema change to a production CRM holding 410 leads, so I'm scoping it to you before touching anything.

Want me to write up the schema + migration plan for review?

## Rest of the scout (FYI, no action)

- **DeepSeek Harness** — new MIT agent framework, big month. Not proposing migration off OpenClaw. One idea worth stealing: an append-only, replayable log of every agent run. Directly relevant to item 1 above — we can't reconcile claims against reality because we keep no replayable record.
- **OpenClaw-RL** — evaluated and rejected. Requires GPU fine-tuning of open-weight models; we run frontier API models. Logged with the reason so it doesn't get re-scouted.
- Skipped as redundant: PocketBase, n8n, Lofty AOS.

Radar: `research-lab/tech-radar.md`. Log: `research-lab/scouting.jsonl` (scout-014 → 016).
