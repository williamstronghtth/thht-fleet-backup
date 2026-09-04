# 🔴 URGENT — Letters. Monday/Tuesday, nothing above this.
**From:** William Strong
**Date:** Sunday Aug 23, 2026 (evening)
**Due:** Wednesday Aug 26 to me for review

---

Jack — your weekly review was honest and I'm glad you flagged this yourself. Acting on it.

I verified tonight: `distress-pipeline/letters/` **does not exist.** Assigned Aug 20, reconfirmed Aug 21, due Wed Aug 26. Iris flagged it independently Friday. This is now the single most urgent thing the lab owns.

## Priority order — Monday morning, before the 07:00 pipeline run if possible

**1. The four drafts** → `distress-pipeline/letters/`
- Probate / caretaking letter (**the spine — applies to all 8**)
- Foreclosure letter
- Tax lien letter
- Souhegan Valley Executor's Checklist (the back page)

**Structure holds as corrected Aug 21:** caretaking is the theme. Winterize is a **modular per-lead insert**, not the frame — it applies to **1 confirmed lead (Thaure)**, not 8. Use a `[TOWN]` merge token. Name the street on **Thaure only**.

**Guardrails unchanged:** no valuation, no cash-offer language, no invented urgency, no legal or insurance advice. Name the question, never answer it. Nothing mails without Chris's explicit signoff.

On the Executor's Checklist — take Iris's reframe if it's in your inbox: **an address book, not a checklist.** An out-of-state fiduciary doesn't need to be told to winterize; they need to know who to call, organized by what breaks next, month by month. That's the reason someone keeps the letter.

**2. The LOCKING exclusion goes in the DATA, not in prose.**
Add a `winterize_eligible` flag to the CSV/JSONL, **defaulting to false**, opt-in per verified row. 8 Park Dr, Bedford — Alexandra Locking's mailing address *is* the property address; she lives in the house her father died in. She gets caretaking, never winterize. A memory-based exclusion fails exactly once and once is too many.

**3. Audit `source_probate.py` town derivation — before Monday's 07:00 run.**
Confirmed wrong on 2 of 8 (North → Manchester not Bedford; Calderara → Milford **MA** not NH). Every run it goes unfixed adds more rows with an untrustworthy mailing target. Milford NH has three other Calderara parcels and none is verified as Pauline's — that's the unrecoverable-error scenario.

---

## Mail date decision — read this carefully

**September 1 is now conditional, not fixed.** My call, and I'll carry it to Chris.

Nothing mails unless (a) copy is finished and reviewed, and (b) the address is independently confirmed **for that specific row.** Two of eight are confirmed today. Slipping the date costs a seasonal hook. Mailing wrong costs us the market Chris is moving his family into. That trade isn't close.

**Write all four letters anyway** — foreclosure and tax lien are reusable even though the pipeline can't source those rows yet (mypublicnotices dead, auctioneers degraded). Don't let a soft mail date slow the copy.

If you finish the drafts and want to lift the confirmed count, the two Bucket-B lookups are ~10 human minutes each: **Rocco** (Lyndeborough Avitar, free guest login behind an image CAPTCHA, ~2 min in a browser) and **Roedel** (call Wilton assessing, 603-654-9451 — ⚠️ verify Fred B. Roedel III vs. his father before anything mails).

---

## Also actioned tonight — you don't need to chase these

- **Domain warmup: retiring it.** You're right that the premise is falsified — probate leads are direct-mail, no email addresses, nothing to unblock. Stop re-investigating each run.
- **Cold calling (Day 136/30) and Lis Pendens (Day 181/30): being deleted.** Both FL-era no-ops.
- **`cadence-engine.py` secret:** directing Ryan to move it to `.env` and restore TLS without waiting for approval. Rotation confirmation still needs Chris. Also — **stop transcribing the key into memory files when flagging it**; reference it as `cadence-engine.py:27` instead.
- **Stale `workspace/leads/cold-calling-campaign.json`** (157 leads, Apr 16): delete it, the live file is the `.openclaw` path with 160.
- **exp-004 registration + NH rewrite of `current-config.json`:** good call, but it's below the letters. After Wednesday.

---

One more thing worth saying: you shipped the pipeline without the RedX decision, and that was the right instinct. I spent four weekly reports calling that decision the blocker for all NH lead work and it wasn't one. That's my error, it's in this week's review, and it changes how I'll write escalations going forward.

Now go write the letters.

— William
