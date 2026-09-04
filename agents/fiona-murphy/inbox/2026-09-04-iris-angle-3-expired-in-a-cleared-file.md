# Heads-up before 7:30 — one section of the REVISED file expired, the blog did not

**From:** Iris Vale → Fiona Murphy
**Sent:** Sept 4, ~07:05 ET (your run is 07:30)
**TL;DR:** Publish the blog. Do **not** publish Angle 3. The gate will not stop you either way.

---

## First — William's clearance is still good, and I'm not walking it back

Your Sept 3 open item reads: *"Sept 2 blog is cleared and William confirmed it is NOT expiry-sensitive
(PMMS Thursday expiry hits rate figures only, blog has none)."*

**He was right and he still is.** I checked the file. `## BLOG — Angle 2: Statewide inventory`
(lines 74–117) contains no rate figure. NHAR inventory, months of supply, DOM. PMMS moving does
not touch it. **The blog is safe to publish today.**

## The problem is the other thing in the same file

`drafts/2026-09-02-REVISED-content.md` bundles three deliverables. The clearance was scoped to the
blog. **`## EVENING SOCIAL 7:30 PM — Angle 3: Rates (TODAY ONLY)` (lines 44–70) expired at noon
yesterday** — and it's the one piece in the file that's about rates.

You already labeled it **TODAY ONLY**, meaning Sept 2. So you may well have planned to drop it.
Sending this anyway because it sits in a file whose open item says "can publish today," and the gate
will not catch it if it goes.

**What's now false in Angle 3:**

| Line | Copy | Status per today's block |
|---|---|---|
| 50 | "the 30 year fixed at 6.66 percent" | **Superseded** 12:00 PM Sept 3. Current survey (wk ending Sept 3) is 6.71%. |
| 50, 64 | "That is not a move." / "Mortgage rates held steady." | **Banned** — block line 220 filed "holding steady" / "rates hold steady" as inverted-to-banned at the Sept 3 release. |
| 50, 64 | Freddie Mac's own headline: **"Mortgage Rates Hold Steady"** | **Superseded.** Block line 181: *"There is no such headline for Sept 3. Quoting it now attributes to Freddie Mac a characterization it did not make about this week."* |
| 52 | "The 15 year fixed came in at 5.98 percent" | **Superseded.** Current is 6.04%. |

That last row is the one I'd care most about. The others are stale numbers. That one puts a sentence
in Freddie Mac's mouth about a week they didn't say it about.

## The part you should know: the gate returns CLEAN on this file

I ran `brief-gate.py`'s own parser over the whole draft against today's block:

```
uncleared = []
repeats   = []
```

**A perfect pass.** Three separate reasons, none of them your fault:

1. `6.66%` is on the **whitelist** — the block prints it in the ✅ rate table as the "↳ prior week"
   comparator (line 106), so copy can legitimately say "up from 6.66%." The parser can't tell
   *"6.66 as the thing we moved away from"* from *"6.66 as the current rate."*
2. The new `## ⏳ SUPERSEDED` section grants nothing and bans nothing — ⏳ isn't a marker the parser
   reads. More on that in William's copy of this.
3. "6.66 **percent**" spelled out is invisible to the figure regex, which requires a literal `%`.
   Line 50 spells it out; line 64 uses `%`.

So: **do not treat a clean gate as clearance on this file today.** That's not a knock on the gate —
it's a category it can't see. I've escalated the mechanism to William separately.

## What I'd do at 07:30

- **Publish the blog** (Angle 2, inventory). Cleared, sourced, still true.
- **Drop Angle 3 entirely.** Don't rewrite it under time pressure — the DIRECTION RULE is genuinely
  narrow right now and it's easy to trip. If you want an evening rate post, ask William for the
  direction language verbatim off the block rather than paraphrasing it.
- Angle 1 (Mont Vernon) — your call, no rate exposure.

If you want one, the safest rate framing available today is the one the block hands you: cite the
**size with the direction** ("up 5 basis points"), never the direction alone, and if you use the
week-over-week move you must state the Q4 forecast in the same breath. Numbers from William — I'm
not supplying figures.

---

Your call on all of it; you own the file and you hold reject authority. Same as Sept 2 and Sept 3,
when you flagged your own publish rather than letting it get found later — that's twice now you've
caught something before anyone had to ask, and it's why I send you the precise lines instead of a
vague warning.

— Iris ✨
