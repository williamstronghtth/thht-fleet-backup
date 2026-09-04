# Distress Pipeline — upgraded to v2 (three tracks)  — from Ryan, 2026-08-18

Chris sent SOP **v2**. I upgraded your `distress-pipeline/` package in place before
the first cron run (Mon Aug 24). It stays yours to run; delivery is still Chris-only
and the hard wall is intact (`verify_wall.py` green).

## What changed vs v1 (foreclosure-only → three tracks)

- **Probate track is LIVE** (`source_probate.py`). Parses the Union Leader
  "APPOINTMENT OF FIDUCIARIES" batch → decedent, `late of` town, first fiduciary
  name+address, **out-of-state flag**, docket #. Validated live: 19 target-town
  estates today, OOS flags correct.
- **Probate hold rule + gate.** `first_letter_eligible = first_seen + 14 days`
  (shown in digest). Estates are **held** as `pending_property_match` until an
  assessor match confirms a property — they are NOT letter-eligible leads yet, and
  they're shown in their own labelled digest section (never dropped).
- **Tax lien track** (`source_registry.py`, monthly): nhdeeds.org is a search
  portal, so for now it emits a **manual checklist** line in the digest instead of
  fake records. `enrich.py` already computes an estimated redemption_deadline once
  real lien records exist.
- **Sources 4/5** (courts.nh.gov monthly, tax-collector quarterly) → digest
  **reminders** (`reminders.py`). Source 5 quarterly: *you draft the records
  requests, **Chris sends them from his own email*** (optics).
- **Track-aware dedupe:** probate keys on docket #, foreclosure/tax on address+owner.
- New/updated Supabase columns — re-apply `supabase_migration.sql` (idempotent; adds
  probate/tax columns + track-aware unique indexes).

## Your action items

1. **Assessor gate is the #1 fast-follow** — it's what converts held probate estates
   into real leads. Per-town portal resolvers in `assessor.py` (`TOWN_PORTALS`), then
   set `ASSESSOR_LOOKUP_ENABLED`. Until then probate rows stay in the "HELD" section.
2. Same as before: bot token (`DISTRESS_BOT_TOKEN`) + Supabase service key when Chris
   provides them. Email sends regardless; Telegram lights up when the token lands.
3. Store was cleared to a clean slate after testing — first cron run repopulates.
   60-day backfill (both tracks) is still a fast-follow.

Run `DISTRESS_DRY_RUN=1 python3 run_monday.py` any time to preview. Ping me with Qs.
