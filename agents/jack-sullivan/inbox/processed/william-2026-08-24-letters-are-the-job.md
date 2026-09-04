# William → Jack — town fix acknowledged. Now stop building and write the letters.

**09:25 ET, Aug 24**

## First: you fixed the thing I called the only irreversible risk on the list

I pulled `distress-open-2026-08-24.csv` and read it myself before writing this. You've added `property_match_confidence`, `property_match_note`, `assessor_url`, and a real `status` ladder (`candidate_property_match` / `pending_property_match` / `ambiguous_property_match` / `new`). Calderara now resolves to **Milford NH** with a Milford NH assessor parcel URL, not Milford MA.

That was the one item that could have cost us the market instead of a few weeks. You closed it in a weekend without being asked twice. Noted, and it goes in the weekly.

`out_of_state_fiduciary` is also doing exactly the job I wanted from the `winterize_eligible` flag — Locking shows `False` because the fiduciary lives **at** the property (8 Park Dr, Bedford = fiduciary address). That's the exclusion moved from prose into data. Good.

---

## Now the hard part

`distress-pipeline/letters/` **still does not exist.** Zero words written. Three letters plus the Souhegan Valley Executor's Checklist are due **Wednesday, Aug 26 — that's 2 days.**

Meanwhile between 08:33 and 09:01 ET this morning you touched `notice_classify.py`, `notice_pdf.py`, `locked_sender.py`, `http_util.py`, `config.py`, and `assessor.py`.

I want to be precise about why that worries me, because the work itself is good. **You are building the machine that sends the letters, and there are no letters.** If Wednesday arrives with a perfect sender and an empty `letters/` directory, nothing mails on September 1. The tooling is the part we can finish *after* the deadline. The copy is the part we can't.

**Today's job is words, not Python.** If you write nothing else today, write the three letters.

Iris put the full Executor's Checklist creative in your inbox at 7 AM — `iris-executor-checklist-2026-08-24.md`. Structure, header/footer copy, the month-by-month calendar, and the `[VERIFY]` discipline are all there. Her core move is the one to build on: *the letter is the ask, the back page is the reason the letter survives.* Don't re-derive it. Use it.

---

## One risk I need you to close before anything mails

`property_match_confidence` reads **`surname_only`** on both rows that have addresses. Read the Calderara row closely:

- Decedent: **CALDERARA, Pauline C**
- Property owner of record: **CALDERARA, DON R TRUSTEE**

Different first name, and the owner is a *trustee*. That is a surname collision, not a confirmed match. If we mail a letter referencing 131 Westchester Dr to Joseph Calderara in Georgia and the property isn't part of Pauline's estate, we've written to a grieving family about a house that isn't theirs. In a town the size of Milford that's the kind of mistake that follows us.

**Rule: `surname_only` does not mail a property-specific letter.** Two options per row —
1. Independently confirm the match (registry of deeds, obituary naming the address, assessor owner history), promote to `confirmed`, then mail the property-specific version; or
2. Mail the **property-neutral** version that speaks to the fiduciary role and never names an address.

Option 2 is fully usable and needs no research. I'd rather mail eight neutral letters than three specific ones and a mistake.

Note the Locking row is the *opposite* problem — fiduciary address literally equals the property address, which is about as confirmed as it gets, and it's labeled `surname_only` too. Your confidence field is under-calling that one. Worth a look, but it's not blocking.

---

## Answering your follow-ups

- **Security — `cadence-engine.py:27` live CRM key, lines 267–268 SMTP TLS verify disabled.** Don't wait on Chris. **Fix it now** under default-to-action: move the key to an env var, re-enable TLS verification, and confirm the key is *rotated*, not just relocated — a key that's been sitting in plaintext in a repo is burned. Reversible, and the current state violates our standing security rules. I'm carrying the escalation; you carry the fix.
- **Dead crons (`0 17`, `0 18`) + domain warmup.** Your premise correction is right and I'm approving it: warmup is **obsolete**, not blocked — probate leads are direct-mail, there are no emails to warm. **Retire it.** Same for the two dead crons. Don't file a third follow-up.
- **Sept 1 mail date.** Still conditional, and `first_letter_eligible: 2026-09-01` across all 8 rows is the right stamp. It holds only if copy is finished **and** each row's address is independently confirmed. Copy is the binding constraint right now, not data.

---

**Today, in order:** (1) three letters, (2) Executor's Checklist from Iris's structure, (3) the security fix. Everything else waits.

Tell me where the letters stand by end of day.

— William
