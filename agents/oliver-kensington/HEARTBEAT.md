# HEARTBEAT.md
# Periodic tasks for Oliver Kensington.

## Weekly Performance Reports

Check if today is Monday or Friday. If so, run the appropriate report ONCE per day.
Use memory/heartbeat-state.json to track last run date and avoid duplicate sends.

### On MONDAY:
- Run: `cd /root/agents/oliver-kensington/workspace && python3 scripts/weekly-report.py MONDAY`
- This sends the prior-week performance report to Telegram (Chris Hoover).
- Skip if already ran today (check heartbeat-state.json `lastChecks.weekly_report`).

### On FRIDAY (after 3:30 PM ET):
- Run: `cd /root/agents/oliver-kensington/workspace && python3 scripts/weekly-report.py FRIDAY`
- This sends the week-to-date performance report to Telegram.
- Skip if already ran today (check heartbeat-state.json `lastChecks.weekly_report`).

### On other days:
- HEARTBEAT_OK — no report needed.

---

## Standard Checks (2-4x per day, rotate through)
- Emails: any urgent unread?
- Calendar: events in next 24-48h?
- Weather: relevant if Chris might go out?
