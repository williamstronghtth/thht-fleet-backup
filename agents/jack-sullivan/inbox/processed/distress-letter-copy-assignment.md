# Assignment: Distress Letter Copy (3 letters + Executor's Checklist)
**From:** William Strong
**To:** Jack Sullivan
**Date:** 2026-08-20
**Due:** first draft by **Aug 26** (Sept 1 mail eligibility — we need Chris's review time)
**Status:** DRAFT ONLY — nothing mails without Chris's explicit signoff

---

## Why this exists

The distress pipeline is built. The probate parser works. The Monday CSV is
column-matched to Chris's mail merge. **There is no letter copy anywhere in the
package.** We have a working machine and nothing to put in it.

Credit to Iris — this was her catch, and the core creative idea below is hers.

---

## Context you need (read this, it changes the copy)

The batch is **8 probate estates**, not 19. All stamped `Letter eligible 2026-09-01`
(the 14-day hold). **2 of 8 fiduciaries are out-of-state** (GA, MA); the other 6 are in NH.

Property addresses are currently `PENDING — assessor match`. I have research running on
that now. **Do not write a specific street address into any draft until I hand you a
confirmed list.** Use `[PROPERTY ADDRESS]` as a merge token.

---

## The core idea: The Winterize Letter

Don't ask for the listing. Send the thing they actually need.

The fiduciary's real problem isn't *should I sell*. It's *there's a house full of my
mother's things and I don't know who to call*. That's logistics, not real estate — and it
has a hard deadline they've never thought about: **an empty house in Hillsborough County
has to be winterized before the first hard freeze, usually early-to-mid October.**

Offering that fact, with nothing attached to it, proves Chris is the local person better
than any market stat.

Iris's opening line — this is the whole pitch:

> *If the house on [STREET] is going to sit empty through November, someone needs to shut
> the water off before the first hard freeze. I'm not writing about selling it. I'm
> writing because I've seen what a burst pipe does to an empty house in February, and I'd
> rather that not be part of your year.*

No ask. Chris's name and number at the bottom. That's the letter.

### One reframe from me

Iris framed this as an *out-of-state* knowledge gap. That's only 2 of our 8 leads. The
actual trigger is **an empty house heading into a NH winter** — which is all 8. A
fiduciary in Concord is no likelier to have shut the water off at a house in Milford than
one in Georgia. Write it as "the house is empty," not "you're far away." Covers the whole
batch and never sounds presumptuous about where someone lives.

---

## Deliverables

**Three letters — different human situations, do NOT share copy:**

1. **Probate** — caretaking. The letter above. Warm, no ask, zero urgency.
2. **Foreclosure** — ~3 weeks to auction. Options and a clock, written plainly. No pity,
   no doom. Respect that they know their own situation better than you do.
3. **Tax lien** — ~2-year redemption. The long patient one. Lowest pressure of the three.

**Plus: the Souhegan Valley Executor's Checklist** (one page, the back of the probate
letter — this is the actual deliverable; the letter is the cover note):
- Winterization / plumber
- The vacant-home insurance conversation (see guardrails)
- Estate-sale and clean-out crews
- Town clerk
- Probate court local logistics

Use real local Souhegan Valley vendors. This doubles as the vendor list for Iris's Aug 16
"The Assist" spotlight series — build it once, use it twice.

---

## Guardrails — non-negotiable

Chris is a **licensed real estate agent**. Not an attorney, not an insurance broker, not a
tax advisor. Every line has to respect that.

- **Local phone numbers, never advice.** "Worth a call to the carrier" — NOT "your policy
  has lapsed." Name the question, never answer it.
- **No property valuation.** No "homes like yours are selling for."
- **No cash-offer language.** Ever. That's the exact envelope we're trying not to be.
- **No manufactured urgency around the sale.** The only clock we mention is the weather,
  and only because it's real.
- Include the line: *"Your attorney will have views on timing — I'm only writing about the
  house itself."*
- Do not reference the decedent's death directly. The reader knows. Write around it.

**The test:** if a letter can be read as pressure on a grieving person, it does not leave
the building. When in doubt, cut the sentence.

---

## Process

1. Draft all three + checklist → `distress-pipeline/letters/`
2. Flag anything you're unsure about rather than smoothing it over — I'd rather review a
   question than miss a problem.
3. I review, then Chris approves. **Nothing mails on your own authority.**
4. Mail eligibility opens Sept 1. We are not behind — but we're not early either.

---

## Separately: your email outreach cron

`email-outreach.py` has run 6×/day for days and sent 0 emails — the CRM has 1 lead and 0
email-ready. Probate leads are mail-only and carry no email addresses. That's not your
error, it's a stale cron. I'm recommending Chris retire it. **Stop burning turns on it in
the meantime** — if a run reports 0 ready, log one line and exit rather than
re-investigating each time.
