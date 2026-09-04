# Back-Catalog Fair Housing Remediation — 12 files

**From:** William Strong
**Date:** 2026-09-01
**Priority:** High — this is live copy, not drafts in waiting.

## What happened

You flagged the Mont Vernon video description this morning. You were right, and
Iris was right. I went looking for the rest of it.

Our Fair Housing gate was built **Aug 31**. Everything published before that date
has never been checked by anything. I ran the gate backwards over the whole back
catalog this morning. It is not one video.

**19 blocking findings across 12 editable files.**

There are another 29 findings in 14 already-sent newsletters. Those are gone —
you cannot unsend email. I have logged them as a record and they are not your
problem. **Do not spend time on the newsletter files.**

## Two gate holes this exposed (now fixed)

Testing the gate against the live Mont Vernon copy found two phrases it missed:

- `"a wonderful place to raise a family"` — no pattern existed at all
- `"looking for space, safety, strong small schools"` — bare-noun "safety" in a
  list never touched a place noun, so the safety rule had nothing to anchor on

Both are now caught, both are locked into `test-fair-housing.py` (59 cases, all
passing). Re-run the gate before you consider any file done — it is stricter
than it was when you last used it.

## The rule, unchanged

> **A town may be described. The people who live in it may not.**

Facts survive. Verdicts do not.

- ✅ "Mont Vernon has one village school, grades K–6."
- ❌ "Mont Vernon has strong small schools."

## The list

## EDITABLE — 19 blocker(s) in 12 file(s) — FIXABLE NOW

   3 BLOCK  2026-08-03-mont-vernon-video2-description.md
           - [schools as verdict] strong small school
           - [safety proxy] looking for space, safety
           - [familial status] raise a family
   2 BLOCK  2026-08-02-blog-draft.md
           - [schools as verdict] best school
           - [steering to schools] NH for school
   2 BLOCK  blog-2026-05-28-market-cooling.md
           - [neighborhood character] desirable neighborhoods
           - [steering to schools] prepare for school
   2 BLOCK  blog-2026-06-01-nashua-fastest-growing.md
           - [schools as verdict] excellent school
           - [schools as verdict] Good school
   2 BLOCK  blog-buyers-market-june-25.md
           - [schools as verdict] good school
           - [schools as verdict] top school
   2 BLOCK  social-posts-2026-07-29.md
           - [schools as verdict] top school
           - [schools as verdict] Top school
   1 BLOCK  blog-2026-05-27-just-sold-9-louis-drive.md
           - [schools as verdict] top tier school
   1 BLOCK  blog-2026-05-27-market-snapshot.md
           - [schools as verdict] quality school
   1 BLOCK  blog-2026-05-28-just-sold-95-wright-road-hollis.md
           - [schools as verdict] strong school
   1 BLOCK  blog-buyers-market-june-24.md
           - [schools as verdict] good school
   1 BLOCK  just-sold-14-boylston-terrace-amherst-nh.md
           - [schools as verdict] top-rated school
   1 BLOCK  just-sold-26-snow-lane-hollis-nh.md
           - [schools as verdict] top tier school


## How to work it

```bash
cd /root/agents/william-strong/workspace/scripts
python3 backcatalog-audit.py --verbose   # the live list, always current
```

Exit 0 means the editable catalog is clean. That is the finish line.

**Order I would take it in:**

1. `2026-08-03-mont-vernon-video2-description.md` — **first.** It is live on
   YouTube right now, it is the town Chris actually lives in, and it is the
   anchor of the whole town series. Note the gate now flags 3 lines here, not 1.
2. The two `just-sold-*` files — these are property marketing, the highest-risk
   category we publish.
3. The blog drafts, oldest first.

**Do not** rewrite anything into vaguer marketing language. Replace each verdict
with the checkable fact underneath it, or cut the sentence. If there is no fact
underneath, there was never anything there to say.

## On the Mont Vernon retitle

Iris proposed reframing that video as *"The Town That Emptied Out"* — the 1890s
hotel era, Kittredge and the "u", 1930 population of 302 against 2,584 today.
That is a genuinely better video and it solves the Fair Housing problem by
replacing the copy rather than sanding it down.

**But treat the two as separate jobs.** The FH fix is not optional and ships
today. The retitle is a creative call that needs Chris. Do not hold the first
hostage to the second.

One caution from Iris worth repeating: we have **four different population
numbers** in circulation for Mont Vernon. Do not put one in copy until Chris
picks the source. Same for "no traffic light in town" and Purgatory Falls being
"minutes away" — neither is verified.

— William
