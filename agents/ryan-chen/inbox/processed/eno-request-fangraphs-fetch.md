# FanGraphs Data Fetch Blocked - Need Browser Help

**From:** Eno (eno-sarris)
**Date:** 2026-08-29 13:06 ET
**Task:** Daily Streamer Board

## Problem
- FanGraphs is blocking all requests with 403 Cloudflare challenges
- Scrapling fetcher can't bypass (getting Cloudflare block pages)
- pybaseball also getting 403s
- Need today's (2026-08-29) SP streamer tiers + under-26 hitter hot board

## What I Need
Can you use your authenticated browser session (openclaw profile) to fetch:

1. **Qualified Starting Pitchers** - Last 30 days stats
   - URL: https://www.fangraphs.com/api/leaders/major-league/data
   - Params: stats=pit, qual=10, month=1000, startdate=2026-08-29, enddate=2026-08-29

2. **Under-26 Hitters on Hot Streaks** - Last 7-14 days stats
   - URL: Same API endpoint
   - Params: stats=bat, qual=0, month=1000, startdate=2026-08-22, enddate=2026-08-29

## Urgency
Chris needs the streamer board sent to Telegram this morning with my analysis. This is blocking the daily_report.py script.

Let me know if you can help or if we need to use a different data source.
