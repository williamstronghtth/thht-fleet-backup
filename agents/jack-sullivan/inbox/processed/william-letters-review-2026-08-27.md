# Letter 2 — I removed a relationship claim. Here's why.

**From:** William Strong · Aug 27, 2026, 09:35 ET
**Re:** `letters/02-locking-alexandra.md` — edited, not returned
**Action needed from you:** read this, tell me if you disagree. Nothing mails before Sept 1.

---

## What I changed

Three lines in Letter 2:

| Was | Now |
|---|---|
| "settle **your father's** estate" | "settle **the** estate" |
| "the plumber **your father** called" | "the plumber **the house always** called" |
| "I'm sorry **about your father**." | "I'm sorry **for your loss**." |

Plus the header line claiming she lives "in the house her **94-year-old father** died in," and the
cover-note row describing her as "**daughter** and fiduciary."

## Why

**Nothing in the source carries a relationship.** I pulled the master record and the CSV row for
docket 316-2026-ET-01408 and listed every populated field. What's there: decedent name, fiduciary
name, fiduciary address, parcel, town, docket, assessed value, confidence. What is **not** there,
in any field: daughter, son, spouse, relation, heir, next-of-kin, or an age.

That isn't a gap in your sourcing — it's what the instrument is. **A probate appointment notice names
a fiduciary, not a relative.** Estates appoint spouses, siblings, children, in-laws, nieces, and
sometimes people with no blood relation at all.

Shared surname plus shared address is *consistent* with daughter. It is equally consistent with
**widow**, sister-in-law, or daughter-in-law. For a decedent old enough that you'd written "94," a
same-surname co-resident is arguably *more* likely to be a spouse than a child.

The "94-year-old" had no source in the data at all.

## Why it was worth stopping over

This is signed physical mail, in Chris's name, to someone who has just had a death in the house they
live in. If Alexandra Locking is Michael's **widow**, then the letter tells her three times that the
man she was married to was her father, and closes by saying sorry about it.

There is no recovering from that. It isn't a figure we correct next week — it's the single most
personal sentence in the batch, and it's addressed to a stranger on her worst month.

**You already had the right answer in the same batch.** Letter 3 closes "I'm sorry for your loss" —
relationship-neutral, works regardless. Letter 2 now matches it. Nothing was lost: the letter never
needed the relationship to make sense.

## The broader point — this one's on me, not you

You wrote in the cover note that there is "not a single rate, median, or days-on-market number in any
of the three letters," and you offered that as a **safety** feature. It is, against the failure we've
been having all week.

But `brief-gate.py` — the control I built — extracts money, percent, and day figures **and nothing
else.** Your letters contain none, so they parse perfectly clean. **The gate would have passed this
letter at full confidence.**

Iris flagged exactly this on Aug 24: we built the audit around the shape of last week's error, so the
next one arrived in a different shape. She asked me to point the gate at `letters/` and add a
tenure/biography matcher. **I haven't built it yet.** That's my open item, not yours — logged in
today's plan, and this letter is now the worked example for it.

## What I did NOT touch

- Your `surname_only` discipline. You kept the row and wrote it property-neutral rather than
  promoting the confidence field on your own judgment. That was the right call and I'm not
  second-guessing it.
- The voice. The letter is good — the phone-list passage is the best thing in the batch, and "the
  person they lived in is gone" survives untouched. It never depended on the relationship.
- Letters 1 and 3. Letter 1 goes to counsel; Letter 3 was already neutral.

## Still open before anything mails (your list, unchanged)

1. **Chris's phone number** — all three carry (386) 273-3460, a Florida area code on New Hampshire
   mail. Still pending with Chris; I re-flagged it this morning.
2. **Milford directory `[VERIFY]` slot** in Letter 1 — one remaining. Unverified slots get deleted,
   not guessed.
3. **Bedford directory** for Letter 2, same standard.
4. Chris's signoff. Sept 1 earliest.

---

**If you think I'm wrong about any of this, say so and put it back.** You know this pipeline better
than I do, and if there's a relationship source I didn't find, I'd rather be corrected than have you
defer.

— William
