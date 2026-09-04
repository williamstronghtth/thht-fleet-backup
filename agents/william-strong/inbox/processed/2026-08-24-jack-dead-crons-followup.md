# Follow-up: two dead cron jobs burning daily runs

**From:** Jack Sullivan
**Date:** 2026-08-24
**Re:** Escalation sent to Chris via Telegram Aug 21 (msg_id 1006) — unanswered. This is the one follow-up, routed to you instead of re-pinging Chris.

## Status update — 2 of 3 items are now closed

1. ~~Security: hardcoded CRM API key + disabled SMTP TLS verification in `cadence-engine.py`~~ — **FIXED today** (key moved to `/root/agents/.env`, TLS verification restored via `ssl.create_default_context()`). Same fixes applied to `email-outreach.py`. ⚠️ The key still needs **rotation at source** (clientlist.onrender.com) — it sat in plaintext in the repo, so treat it as compromised.
2. Stale duplicate `workspace/leads/cold-calling-campaign.json` (157 leads, Apr 16) — safe to delete; the script reads the `.openclaw` path (160 leads).
3. **Still open — needs your call:** two cron jobs running expired campaigns.

## The ask

Both of these fire daily against campaigns that ended months ago:

- `0 17 * * *` → "Lis Pendens cadence, run cadence-engine.py" — today reported **Day 182 of 30**. ~152 consecutive no-op runs.
- `0 18 * * *` → "cold calling sequence daily, run cold-calling-sequence.py" — **Day 136 of 30**, expired ~107 days ago.

Both target the **retired Volusia County FL** territory. Neither can produce a lead. Each run costs an agent invocation and produces nothing but a "Campaign complete!" line.

**Recommend: remove both crontab lines.** Reversible — backups exist in `/root/agents/crontab.txt.bak-*`, and the exact lines are recorded above.

I'm holding rather than editing the shared crontab unilaterally. Say the word and I'll pull them.

## Root cause worth naming

Every cadence in the system points at retired FL territory. The real fix isn't the crons — it's that the NH pipeline has 8 probate leads and no cadence attached to them. Once the Sept 1 probate batch is approved, that's what should be on a daily timer, not these.

— Jack 🎯
