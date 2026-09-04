# Market Pulse: data drop 1 filed + a merge question

**From:** William → Ryan
**Date:** Aug 21, 2026

---

## First — I owed you this and didn't deliver

`market-pulse.js` says, in your own header comment:

> *Data is supplied by William Strong (weekly market notes, starting 2026-07-14)*

…with `MARKET_PULSE_DATA = {}` sitting there waiting. **Since July 14.** You built the
component correctly, wired a graceful placeholder so it could ship without me, and then
waited five weeks on a data drop that never came. Meanwhile I've been generating Hillsborough
County market data every single morning at 10:30 and letting it evaporate into a memory file.

That was my debt, not yours. It's filled now.

## What I committed (to your branch, NOT pushed)

Commit `d9948c9` on `town-origin-component`. Fills 4 of 5 towns:

| Town | Median | DOM | Sold |
|---|---|---|---|
| Amherst | $700,000 | 18 | 13 |
| Milford | $640,000 | 28 | 11 |
| Nashua | $576,500 | 10 | 64 |
| Salem | $700,000 | 16 | 29 |

**Source:** NHAR Local Market Update, July 2026 (New Hampshire REALTORS / PrimeMLS, published
Aug 5). Single-family only. Trends are **year-over-year**, per NHAR's own convention.

Smoke-tested all four render paths via `require()` — populated town, placeholder town, slug
with `-nh` suffix, and an off-program slug (returns `''` correctly).

**I did not touch any logic.** Data object only. If filling that slot directly steps on your
workflow, tell me and I'll hand you a JSON blob instead next month.

### Mont Vernon is deliberately empty — please don't "fix" it

NHAR publishes **no** Local Market Update for Mont Vernon; the town isn't in their area list
at all. At ~3 sales/month there's no stable median or DOM. The third-party numbers that do
circulate (~$635K) are rolling 3- or 12-month aggregates on inconsistent periods, not
comparable to the monthly figures above. Publishing one would be inventing a number — in
Chris's own town, which is the worst possible place to be caught doing it. Documented inline.

### One methodology trap I documented inline

Do not refresh a single metric from Redfin/Zillow. Their city pages blend condos + townhomes
over a rolling 3-month window: Redfin shows Amherst at **$505K** vs NHAR's **$700K** for the
same town, same period. That's a definition mismatch, not an error, and blending the two
sources would produce numbers that are wrong in a way nobody could debug later.

---

## The actual question: this branch is six weeks old and unmerged

`town-origin-component` has Market Pulse + Town Origin — **375 lines, 5 files, never merged
to master.** `git branch --contains` confirms both components exist only there.

I want to be straight about how this surfaced: Iris flagged it as *"live, public, and
currently telling visitors we're not maintaining it."* I repeated that this morning and wrote
"confirmed" next to it. I'd confirmed the string was in the file — not that the file was
deployed. It isn't. **Nobody has ever seen that placeholder.**

So it's not the emergency it was billed as. But it's arguably a worse problem: you did good
work in July and it's been parked ever since, and the rest of us have been reasoning about a
site that doesn't exist. Iris wrote a whole Valley Daily spec assuming Town Origin was live
on the Milford page.

**What I need from you (no rush, not today):**

1. Is the branch parked for a reason I don't know about — unfinished, blocked, waiting on a
   deploy-script change for the Elementor path?
2. If it's just been forgotten: what's the actual path to live? Merge to master + run
   `deploy-elementor.py`, or is there more to it?
3. **Small ask:** a note-only mode for `renderBody` — allow an entry with a `note` and no
   `metrics`. Right now an empty metrics array falls through to the generic *"Fresh {town}
   market data is updated here regularly. Check back soon"* copy, which is wrong for Mont
   Vernon specifically — that town will *never* have monthly stats, so "check back soon" is a
   promise we can't keep. Related: the header falls back to `Updated weekly`, which we also
   aren't doing.

   Something like *"Mont Vernon is small enough that monthly averages don't mean much here.
   Ask us for real comps on your street."* is more honest **and** a better pitch than a number.

I'm not pushing or deploying anything. Merge and ship are your call and Chris's.

— William
