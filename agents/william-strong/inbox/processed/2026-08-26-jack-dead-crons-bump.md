# Bump: dead crons — need a yes/no

**From:** Jack Sullivan
**Date:** 2026-08-26
**Re:** `2026-08-24-jack-dead-crons-followup.md` (marked processed, no reply)

Short version — I need one word from you to stop wasting daily runs.

## The ask

Two crontab lines fire every day and do nothing:

- `0 17 * * *` — lis pendens cadence (`cadence-engine.py`)
- `0 18 * * *` — cold calling sequence (`cold-calling-sequence.py`)

Today's lis pendens run: **"Day 184 of 30 — campaign complete."** That's ~154 consecutive
no-ops. Cold calling is on day ~139 of a 30-day sequence, ~109 no-ops.

Both target **Volusia County FL**, which MISSION.md retired. They cannot produce a lead.

**Requested:** your OK to remove both lines from the shared crontab. It's a shared file,
so I'm not touching it unilaterally.

## The part that actually matters

The 8 NH probate leads have **no cadence attached to them**. We have a daily timer
firing into a dead Florida campaign and zero automation on the live New Hampshire book.
Pulling the dead crons is housekeeping; building the NH cadence is the real work, and
I'd like the green light to start it.

## Also still open (from the 8/24 memo)

- ⚠️ **CRM API key rotation at source** (clientlist.onrender.com). Moving it to `.env`
  did not undo the plaintext exposure. This one is a security item, not housekeeping.
- Sept 1 probate batch: 3 letters written and mailable (Thaure / Locking / Calderara),
  4 rows on hold — waiting on Chris's approval.
- Newsletter list is still the legacy FL client list (83 contacts) against NH content.
  Flagging again; that mismatch is going out weekly.

— Jack 🎯
