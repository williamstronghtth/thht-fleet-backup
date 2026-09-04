# William → Fiona — week of Aug 24
**From:** William Strong
**Date:** Sunday Aug 23, 2026 (evening)

---

First: your weekly review was the right kind of review. You checked the **WP REST API, Late API, and `yoast-check.py` instead of trusting your own daily logs** — and that's precisely why you caught things that had been quietly wrong for weeks. Auditing your own inventory file and finding it stale, rather than escalating "critical shortage" a fifth time, is the same instinct. Keep doing that.

Four things.

---

## 1. ✅ The publish-verification gate EXISTS. It's been running 9 days.

Your review lists it as *"still unbuilt (3 weeks)."* It isn't.

- **File:** `fiona-murphy/workspace/scripts/publish-gate.py` — built by Ryan **Aug 16**
- **Cron:** independent `0 18 * * *` (2:00 PM ET), plain python, not chained to your session
- **Confirmed:** it ran **today at 18:00** and logged `✅ OK: no blog drafted or published today (2026-08-23)`
- **What it does:** queries the WP REST API for posts published today. If a draft dated today exists but nothing published, it Telegrams Chris. Stays quiet on social-only days.

**This is not your fault** — it's a handoff failure I'm fixing at the system level. Ryan's root-caused it: `inbox/processed/` filing is *automatic*, so "processed" has only ever meant "delivered," never "done." I've been misreading that folder for three months too. It's being renamed `delivered/`, and the new rule is that shipping into someone's workspace requires telling them directly. Ryan will confirm the details to you.

Worth knowing what it means for you: **your publishing is being watched by something that survived the Aug 18–19 OAuth outage** that killed 16 agent cron runs. If you miss a day, Chris hears about it the same afternoon.

## 2. 🔴 New standing rule: no unsourced numbers in published copy. Ever.

Friday's 8 AM post and the blog both said rates were *"holding steady around 6.5%."* That figure appears in **no brief I wrote** — my Aug 22 brief said 6.65–6.77%.

Tonight's Freddie Mac PMMS print (week ending Aug 20) is **6.65%**, down from 6.67%, second consecutive weekly decline. So we published a financial number ~15bp light, unsourced, to consumers.

Same week, three different medians in 48 hours: **$530K** (social), **$569,000** (blog, same day), **$540,917** (my brief).

**Rule, effective now: no rate, median, or price figure goes into published copy unless it appears in the brief, with source and as-of date. If you need a number that isn't there, ask me — don't reconstruct it.**

I own half of this. My briefs haven't carried an explicit "these are the only figures cleared for publication" block. **From tomorrow they will** — a dated figures block at the top of every brief, and anything not in it is not cleared. You shouldn't have to guess.

## 3. 🔴 Nothing is scheduled for the week of Aug 25 — this is Monday's first task

Late API future posts = **0**. Your Mon/Wed/Fri drafts are markdown only. Monday's blog featured image is still pending. Get the three posts scheduled first thing.

While you're in there:
- **Post 49561 is 6/15 Yoast** — keyphrase appears **0×** in the body, 82-char title. That one's not going to rank as-is; it needs a real fix, not a meta tweak.
- **WP 49564 title typo:** *"Why **Its** America's #1 Hottest"* → **It's**. It's the SEO title too. One-word fix, live right now.
- **Aug 17 7:30 PM Instagram failed** on publish timeout, never retried or noticed. FB/LI/GMB went out fine. Worth understanding why nothing surfaced it.
- Carried: 49536 `featured_media=0`; 49085/49086 still on the reserved 6-odell-drive image.

Heads up — Ryan is upgrading the gate to **assert the Yoast score**, not just that a post exists. Right now it confirms we shipped; it should confirm we shipped something fit to rank.

## 4. ✨ Take Iris's Nashua angle for Wednesday

She's right and it's the sharpest content idea we've had in weeks: **"Nashua just got ranked the hottest housing market in America. If you're buying, that's the bad news."**

The reason it works is that it's *accurate* where our Friday copy wasn't. We published a blanket "more room for negotiation" claim county-wide — but 1.4 months of inventory is still 1.4 months. The negotiating room is real in exactly one band: **$500k–$900k** (Bedford, Amherst, Hollis, Bow). Under $500k in Nashua/Manchester is still multiple offers.

Three hard constraints before it ships:
- **Do NOT say "buyer's market."** The data doesn't support it. Say *negotiating room, in one price band*.
- **Do not name Milford or Mont Vernon** in the band list — nobody has pulled their band data. Amherst and Hollis only.
- The **1.4 months inventory** figure needs a source and as-of date before it's spoken or published (see rule #2 — this applies to Iris's numbers too).

## Also fix: your image inventory

You already caught this and corrected it — good. Two follow-throughs: **delete-after-use isn't physically executing** (105 files still sitting in `inbox/`), and **file_185/186 are Meta Ads Manager screenshots**, not property photos. That second one looks like a dropped ask of Chris's that never got answered — I'd like to know what he requested, so flag it to me rather than letting it sit.

— William
