# ✅ Blog publish-verification gate — DEPLOYED

**From:** Ryan Chen
**Date:** 2026-08-16 (Sunday weekly review)
**Re:** Your nudges of Aug 11 / 12 / 13

## Status: DONE and live

Straight answer first: the gate was **not built** when you nudged — the Aug 10 ticket and all three of your nudges had been filed to `processed/` without the work actually happening (same "marked processed, not done" failure mode as the exp-067 audit). I caught it in tonight's review and built it end-to-end.

## What shipped
- **`fiona-murphy/workspace/scripts/publish-gate.py`** — session-end gate.
  - Queries the WP REST API for posts **published today (ET)**.
  - If a post published → logs OK, exits clean.
  - If **a draft dated today exists but nothing published** → the exact bug you reported (Aug 4/5/8) → **loudly alerts Chris on Telegram**, same-day.
  - If nothing drafted or published (a social-only day) → stays quiet, no false alarm.
- **No hardcoded secrets:** WP creds from Fiona's gitignored `.env` (via `wp_config.py`); Telegram token read from `telegram-bots.json` (Fiona's bot).
- **Wired to cron:** new line `0 18 * * *` (2:00 PM ET) — an *independent* daily check, so it fires even if Fiona's session crashed mid-publish (which is how the drops happen). Added to tracked `crontab.txt` and reinstalled — verified **no drift**.

## Tested
- Dry-run against live WP today: auth passes, query works, correctly reported "no blog drafted or published today (Aug 16) — nothing to gate" (today is a testimonial/social day, so quiet is correct).
- Had to set a `curl/*` User-Agent — the host WAF (Mod_Security) 406s the default python-requests UA.

## One thing for you to confirm with Fiona
The gate keys on WP **drafts dated today**. If Fiona ever writes the draft the night before, the date filter could miss it — worth a 30-sec confirm with her that drafts are created same-day. If not, I'll widen the window.

## Separately — new secrets finding (flagging per policy)
`fiona-murphy/workspace/scripts/publish-aug-15.py` **hardcodes the live WP app password AND the Late API key**. Same violation class as the exp-067 Gmail password. I did not touch it tonight — flagging it into the next secrets-remediation batch (alongside the still-open opus-5 registry fix and the CRM key in 19 files). Say the word and I'll roll all three into one pass.

— Ryan
