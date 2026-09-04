# Fly In cron: killed — and a correction on the method
**From:** Ryan Chen  **Date:** 2026-07-19 (weekly review)

## Done ✅
Your #1 Monday action item (Fly In 15-touch cadence cron) is dead. But the situation wasn't what the note assumed — worth knowing:

**The Fly In cron was already ABSENT from the live crontab.** The landmine was `crontab.txt` (the source-of-truth file), which still had it active. So it wasn't actually firing daily — but any reload of that file would have brought it back.

**Your instruction was "remove from crontab.txt and reload" — I did NOT do a straight reload, because it would have regressed two other jobs.** The file had drifted from live in 3 places:
1. Fly In cron — active in file, absent in live (the one you wanted gone)
2. Derek SEO blog cron — active in file, but correctly PAUSED in live (Jul 16 content-audit note)
3. nolan-mc cron — single 15:30 fire in file, but every-30-min corrected version in live

A reload would have re-activated Derek and reverted nolan-mc. So I did the reverse: backed up `crontab.txt.bak-2026-07-19`, then regenerated the file FROM live (`crontab -l > crontab.txt`). Now file == live, Fly In gone from both, zero drift.

## The real issue (issue-006)
`crontab.txt` is an unowned shared single-point-of-failure that silently drifts from the live crontab. This week proved the drift is real and dangerous. Durable fix options:
- (a) Make live crontab the sole source of truth; delete crontab.txt, or
- (b) A pre-reload guard that diffs file vs live and refuses to clobber newer live state.

Hand-sync is a patch, not the fix. Want me to build (b)?

## Standing blockers (escalating to Chris today)
- Town Origin + Market Pulse deploy — built + committed, awaiting Chris green light
- gh token (issue-004) — 5+ weeks blocked
- Render kill/keep/pay (issue-003) — thht-hq + thht-social both stable-503 suspend
