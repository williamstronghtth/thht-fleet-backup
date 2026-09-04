# Handoff: Distress Pipeline ("Foreclosure Watch") — you now own this

**From:** Ryan Chen (engineering) · **Date:** 2026-08-18 · **For:** Jack Sullivan

Chris reassigned the NH pre-foreclosure pipeline from a new agent to you — you've
got the SMTP (Workspace app password) and the CRM chops. I built the MVP; **it
lives in your workspace and runs on your schedule. You own running/monitoring it.**

📁 `distress-pipeline/` — read `README.md` first. It's self-contained.

## What you need to know

- **It delivers to Chris ONLY.** There is a hard wall (Chris's explicit
  requirement): the pipeline cannot email/message anyone but Chris, and it shares
  no code or send path with your drip/sequence outreach. `python3 verify_wall.py`
  proves it. **Do not wire any of this into cadence-engine or email-outreach** —
  that would breach the wall.
- **Cron is installed** (root crontab): Mon 11:00 UTC (main run + email + CSV) and
  Thu 11:00 UTC (postponement re-check). First run: **Mon Aug 24**.
- **Email is live** (your Gmail app password, recipient locked to Chris). **Telegram
  is waiting** on the dedicated bot token — until `DISTRESS_BOT_TOKEN` is in
  `/root/agents/.env`, Telegram is cleanly skipped and email still sends. When
  Chris supplies the token, add it and it lights up — no code change.
- Storage is local JSONL now; Supabase table mirrors once `supabase_migration.sql`
  is applied + service key is set.

## Your action items

1. Watch the first cron run Mon Aug 24 (`/root/agents/logs/cron.log`) — confirm
   Chris gets the email + CSV.
2. Once the bot token lands, drop it in `.env`, then `python3 run_monday.py` once to
   confirm the Telegram digest.
3. Phase-2 (when you have cycles): handle Chris's "letter sent" Telegram replies →
   update `letter_sent_date`. See README "fast-follows".

Ping me (ryan-chen) if anything in the code needs changing — I'll keep owning the
engineering; you own operations + Chris comms on this.
