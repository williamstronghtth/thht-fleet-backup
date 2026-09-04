# HEARTBEAT.md

## Fantasy Baseball GM Check-In
- Scan FanGraphs/Savant for skill trend changes
- Review league standings and category gaps
- Flag actionable move, watchlist candidate, roster risk
- Format: skills-based, concise, opinionated

## Daily Streamer Board — handled by cron, do NOT duplicate
- Root system crontab entry: `5 13 * * *` (9:05 AM ET during EDT)
- Runs scripts/daily_fetch.py + scripts/daily_report.py, delivers to Telegram
- **DST note:** shift to `5 14 * * *` when EST starts (early Nov), back to 13 in March
- (The old PitcherList cron 76474f56 is dead — it was session-only. Removed.)
