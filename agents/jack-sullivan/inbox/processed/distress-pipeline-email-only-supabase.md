# Distress Pipeline — email-only + Supabase steps (2026-08-18, from Ryan)

Chris made two calls. Both applied to your `distress-pipeline/` package.

## 1. Email-only (Telegram removed as a constraint)
- `locked_sender.py` now exposes ONLY `send_email_to_chris`. `send_telegram_to_chris`,
  `MissingTokenError`, and `DISTRESS_BOT_TOKEN` are gone. No bot token needed anymore.
- `run_monday.py` — emails the digest + CSV, no Telegram path.
- `run_thursday.py` — now **emails** a short update only if a postponement changed
  (was Telegram-only before).
- `digest.build_telegram` → renamed `build_digest`.
- `verify_wall.py` now asserts `__all__ == {"send_email_to_chris"}` (email-only is
  tested, not just intended). Green.

## 2. Supabase — code side done, 2 dashboard steps are yours/Chris's
I can't apply DDL from here (no psql/service key on the box), so I hardened the code
and wrote exact steps in `README.md` → "Supabase setup — exact steps".
- `store.py`: sync now upserts on `id` (`on_conflict=id`), strips ephemeral enrich
  fields to a `TABLE_COLUMNS` whitelist (was going to 400 on unknown columns), and
  surfaces the real error body on failure. Renamed `_sync_supabase` → `sync_supabase`.
- New `backfill_supabase.py` — one-shot to push the whole local store up once creds
  land. Idempotent (`--dry-run` supported).
- `supabase_migration.sql` unchanged (already correct + idempotent).

**To go live on Supabase:** run the migration SQL in the thht-crm SQL Editor, copy the
`service_role` key + Project URL into `/root/agents/.env` as `SUPABASE_SERVICE_KEY` /
`SUPABASE_URL`, then `python3 backfill_supabase.py`. Full detail in README.

## Housekeeping
- Cleared the test store again — Aug 24 first cron run starts on a clean slate.
- Cron unchanged (Mon + Thu 11:00 UTC). Reminder: bump to 12:00 UTC in November (EST).

— Ryan
