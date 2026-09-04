# Build request: Fiona blog publish-verification gate
**From:** William Strong — 2026-08-10
**Priority:** Medium (fixes a recurring reliability bug — 3 blog misses in the last week)

## Problem
Fiona's blog PUBLISH step is a manual WordPress API call buried inside her single daily cron session with **no enforcement**. On Aug 4, 5, and 8 the social posts ran and the draft was written, but the publish step silently dropped — no post went live, no alert fired. This is a publishing-consistency bug, not a content-supply problem (drafts existed).

## Requested fix (Fiona's own recommendation)
A **session-end publish-verification gate**:
1. At the end of Fiona's daily run, query the WordPress API for any post with `date` = today (published, not draft).
2. If one exists → OK, log and exit clean.
3. If none exists → **loudly alert Chris** (Telegram) that today's blog did not publish, so it can be caught same-day instead of surfacing in a weekly review.

## Notes
- Keep it idempotent / safe to re-run.
- WP credentials are already in Fiona's env (`fiona-murphy/.env`) — do not hardcode.
- Coordinate with Fiona on the exact WP API endpoint + auth she uses today.
- This is an "on us" item from the Aug 9 weekly review — no need to wait on Chris to build it.

Ping me when it's live and I'll confirm with Fiona on the next run.
