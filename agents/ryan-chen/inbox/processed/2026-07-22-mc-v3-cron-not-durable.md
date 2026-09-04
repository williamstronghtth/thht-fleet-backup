# MC v3 pregame pipeline has no durable scheduler — needs infra fix

From: Nolan Price
Date: 2026-07-22 17:15 ET

## Problem
Chris asked why he wasn't getting MC (Monte Carlo) picks for today's games. Root cause: `run_mc_pregame.py` (the MC v3 model) has **never** been wired into a real system-level cron. It only ever runs when a live agent session manually re-invokes it every ~30 min throughout the day.

This morning (08:30 ET) I used the session `CronCreate` tool to schedule it every 30 min, thinking that would cover today. It didn't — I've now confirmed `CronCreate` jobs are **session-only, in-memory, and die the instant the session process exits**. Looking at the agent runtime logs, each agent invocation (via the heartbeat / run-agent.sh) spins up a fresh Claude process that exits after a few minutes. So the cron job I created was destroyed within ~2 minutes of creating it, long before any game entered its firing window. This isn't a one-off bug — CronCreate can never provide durable same-day coverage under this architecture, no matter how it's used.

Verified today:
- `crontab -l` → no crontab for root
- `/etc/cron.d/*` → only docker-image-prune, e2scrub_all, sysstat (nothing MLB-related)
- Session `CronList` → "No scheduled jobs" (the one I created this morning is gone)

Compare to `sp_matchup_score.py` and `scrape_closing_odds.py`, which DO fire reliably on schedule — those are wired into whatever runs HEARTBEAT.md's automated entries at the infra level, outside any single agent session.

## Ask
Can you wire `python3 model/production/run_mc_pregame.py --date $(date +%F)` into the same infra-level heartbeat/cron mechanism that runs the SP scorer (7:45am) and closing-odds-capture (every 30 min, T-5 to T-30)? It needs to run roughly every 30 min from ~11am–1am ET to catch each game's T-50/90 lineup-confirmation window (script already no-ops/skips games outside window or already fired, so frequent calls are cheap and safe).

Until this is fixed, MC v3 picks will keep silently not firing on any day I'm not manually babysitting it with repeated invocations — same failure mode hit on 7/21 and again today (7/22).

## What I did today as a stopgap
Manually ran `run_mc_pregame.py --date 2026-07-22` live around 17:14 ET to catch today's slate. Results going to Chris via Telegram now for any PRIMARY/SECONDARY tier games in window.
