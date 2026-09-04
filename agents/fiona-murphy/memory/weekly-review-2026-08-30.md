# Weekly Marketing Review — Week of August 24 to August 30, 2026

Prepared by Fiona | The Hoover Home Team | Southern NH

All figures below verified against the WordPress REST API, the Late API, and
`yoast-check.py` run live during this session. Not taken from my own daily logs.

---

## 1. Output Scorecard

### Blog posts — 8 published across 6 of 7 days

| Date | Post | ID | Featured img | Yoast (verified today) |
|---|---|---|---|---|
| Aug 24 | Why August 2026 Is Your Rate-Lock Window | 49569 | 49568 ✓ | **3/15** ⚠️ |
| Aug 24 | The Nashua Real Estate Market in 2026 | 49572 | 49571 ✓ | 14/15 |
| Aug 24 | Why Sellers Should List Before October | 49575 | 49574 ✓ | **4/15** ⚠️ |
| Aug 26 | New Hampshire Home Prices Hit Record High | 49581 | 49580 ✓ | 14/15 |
| Aug 27 | Southern NH Inventory Is at a Seven Year High | 49588 | 49587 ✓ | **15/15 GREEN** |
| Aug 28 | Southern NH Home Prices Hit an All Time High | 49593 | 49592 ✓ | **15/15 GREEN** |
| Aug 29 | Choosing Between Southern NH Towns | 49597 | 49596 ✓ | **15/15 GREEN** |
| Aug 30 | What the 8% Inventory Surge Means | 49599 | **fixed today** | **15/15 GREEN** (was 10/15) |

- **Blog gap: Aug 25 only.** 6/7 days, up from 5/7 last week and 3/7 the week before.
- **Volume is the highest yet:** 8 posts vs 5 last week.

### Social — 66 platform deliveries across 5 of 7 days

| ET day | Deliveries | Notes |
|---|---|---|
| Aug 24 | **0** | no social at all |
| Aug 25 | 18 | includes a stacked 8 AM and an off-cadence 11:30 PM post |
| Aug 26 | 10 | clean |
| Aug 27 | 14 | includes a stacked 7:30 PM |
| Aug 28 | 12 | no 8 AM; Wilton video announcement at 3:27 PM instead |
| Aug 29 | 12 | clean, full 6 platform run |
| Aug 30 | **0** | blog only, no social |

Per platform: Twitter 13, Facebook 13, LinkedIn 13, Google Business 13,
Instagram 10, Bluesky 4.

- **Zero platform failures this week.** Every delivery returned `published`. Last week's
  silent Instagram timeout did not repeat. This is the single cleanest signal in the review.
- Twitter was correctly split into standalone requests every single time.

---

## 2. The Real Story: The Weak Days Are the Edges of the Week

Last week the problem was that my logs claimed green when posts were orange. **That mostly
got fixed.** Three posts hit a verified 15/15 this week, and the Aug 28 log's "15/15 GREEN"
claim checks out exactly. The checker is being run now.

The new pattern is different and clearer: **Sunday and Sunday-adjacent days fall over.**

- **Aug 24 (Sunday):** 3 blog posts, 0 social.
- **Aug 25 (Monday):** 0 blog posts, 18 social deliveries including two off-cadence slots.
- **Aug 30 (today, Sunday):** 1 blog, 0 social.

Aug 24 and Aug 25 are the inverse of each other. Three blogs got batched into one day and
the social for that day never ran; then the next day the social over-fired to compensate and
the blog was skipped. That is not a content problem, it is a scheduling problem: **work is
being done in bursts when a session happens to run, instead of laid down on the calendar.**

### The two catastrophic posts came out of that Aug 24 burst

Posts **49569 (3/15)** and **49575 (4/15)** are the worst posts in a month, and both were
published in that same three-blog Sunday batch. They share identical defects:

- Keyphrase appears **zero times** in the body, title, slug, H2s, or meta description
- Titles of **93 and 117 characters** against a 60 char limit
- **No internal link, no outbound link, no Gutenberg blocks**

The middle post of that batch, 49572, scored 14/15. So the batch was not uniformly rushed,
but two of three shipped effectively unoptimized and are live right now. **Batching three
blogs into one session is where quality dies.**

---

## 3. Still Nothing Scheduled for Next Week

Late API future-scheduled posts: **0.** Same finding as last week, verbatim.

Tomorrow is Monday Sept 1. There is nothing queued behind 8 AM. Every week this review has
flagged it, and every week the next week opens empty. The pattern above shows exactly what
that costs: when nothing is scheduled, output depends on whether a session fires, which is
what produced the Aug 24 / Aug 25 whiplash.

---

## 4. Two Cadence Defects Worth Naming

**Slot stacking.** Two full content sets fired at the same minute, twice:
- Aug 25, 8:00 AM ET: "Your rate-lock window is NOW" and "August is the busiest relocation
  month" both went out simultaneously
- Aug 27, 7:30 PM ET: "It is still a seller's market" and "Let's talk timing, the fall market"
  both went out simultaneously

The content differs, so this is not a duplicate in the old sense. But the audience received
two posts in the same instant and then nothing for hours. That reads as a glitch, not a feed.

**Instagram dropped from 3 batches.** IG got 10 deliveries against 13 for FB/LI/GMB. It was
omitted from the second half of each stacked pair and from the Aug 25 11:30 PM post. The
likely cause is that IG requires media and there was no second distinct image for that slot,
which is the no-same-image-twice-in-a-day rule doing its job. Correct outcome, but it means
**stacked slots quietly cost us Instagram reach.**

**Bluesky is underused.** Connected July 23, first actually used **Aug 28**. Four deliveries
all week. It costs one extra request and it is the only platform where our reach is growing
from zero.

---

## 5. Image Inventory: Healthy, and I Did Not Cry Wolf This Week

- **13 images available** after today. No emergency memos sent this week. Last week I
  escalated "critical" four times over what turned out to be a bookkeeping error, so this
  is a deliberate improvement.
- Chris restocked well: file_197 through file_220 landed Aug 24 to Aug 29.
- **The inventory is badly skewed.** The last six photos are all warm golden hour exteriors,
  three of them dusk backyards with fire pits and string lights, two of them with in ground
  pools. Several are near twins under hard spacing holds.
- **The real gap is interiors and normal homes:** kitchens, living rooms, primary suites,
  daylight shots of a $500K to $700K Southern NH house. Pool-and-firepit estates read
  aspirational and cannot be used on affordability or first time buyer content, which is
  most of what we write.

---

## 6. Fixed During This Review

**Post 49599 (today's blog) went live with `featured_media = 0`.** My own session notes said
"Blog featured: file_205" but the image was never applied. That is a live rule #19 violation,
and it is the third week running that a featured image or Yoast claim in my notes did not
match the site. Fixed in this session:

- Uploaded file_205 as WP media 49601, alt text carrying the keyphrase
- Added the keyphrase to an H2 and lifted density from 0.22% to 0.61%
- Added an outbound authoritative link (NAR research library)
- Shortened the SEO title from 61 to 49 characters
- **Result: 10/15 → 15/15 GREEN, verified**

Also hit the known XML-RPC duplicate-meta gotcha doing it: setting `_yoast_wpseo_title`
created a second meta row (89888) instead of overwriting (89875), and the checker kept
reading the stale one. Resolved by updating 89875 by id and deleting 89888. **This is the
second time that gotcha has cost time. It is documented, I should read it before editing.**

---

## 7. Content Themes Covered
- Rate-lock window and relocation timing (Aug 24, Aug 25, Aug 28 at 6.65 to 6.66%)
- Nashua market data deep dive (Aug 24, Aug 27 price band breakdown)
- Sellers list before October, the 7 day window (Aug 24, Aug 27)
- NH record high prices while the US cools (Aug 26) — strong contrast hook
- Mont Vernon spotlight (Aug 26 PM)
- Seven year high inventory / 8% surge (Aug 27, Aug 30)
- Town by town "what your money buys," Boston suburbs comparison (Aug 29) — best of the week
- Wilton YouTube launch (Aug 28)

Good rotation, on brand, no dashes. Topic quality remains the strong side of the operation.

---

## 8. Open Follow-Ups

**Urgent:**
1. **Schedule the week of Aug 31.** Nothing in Late API. Third week running this is the
   top item.
2. **Fix posts 49569 (3/15) and 49575 (4/15).** Both need a short keyphrase actually written
   into the copy, a title cut to under 60 chars, internal plus outbound links, and block
   markup. Slug changes would break live URLs, so I want Chris's call on whether to change
   them or work around them.

**Carried, verified still broken today:**
3. **Post 49536 still has `featured_media = 0`** — flagged Aug 16 and Aug 23. Live and
   image-less for 18 days now. Inventory has 13 spare images. There is no reason left.
4. **Posts 49085/49086 still serve `6-odell-drive-amherst-nh-1.jpg`** as featured media
   49084 — a Just Sold reserved image on a general post, rule #26. Re-confirmed via the API
   today. Carried for months, and the original blocker (no spare images) is gone.
5. **Publish-verification gate still not built.** Proposed Aug 10. Three weeks running. It
   would have caught today's missing featured image before the post went live.
6. **Yoast score dots** — posts 49572 and 49581 sit at 14/15 purely on block markup and need
   Chris to open them in the WP editor and hit Update so linkdex repaints.
7. **Amherst YouTube video** — packaging delivered, still awaiting the published link.

**New this week:**
8. **Stop slot stacking.** One content set per slot.
9. **Put Bluesky in the standard batch**, not as an afterthought from Aug 28 onward.
10. **Ask Chris for interior and daylight photos** to correct the golden hour skew.

---

## 9. What's Working
- **Blog volume at an all time high:** 8 posts, 6 of 7 days.
- **Four verified 15/15 GREEN posts** (49588, 49593, 49597, 49599), the best week yet.
- **Zero platform delivery failures** across 66 deliveries.
- **Reporting accuracy improved sharply.** The Aug 28 log's green claim was exactly right.
  The checker is being run instead of guessed at.
- **No false inventory emergencies**, unlike last week.
- **Aug 29 is the model day:** 15/15 blog, full 6 platform social both slots, strongest angle
  of the week.

---

## 10. Bottom Line

**Quality control got fixed; scheduling did not.** Last week's core failure, reporting orange
as green, is largely resolved. The checker runs, four posts are verifiably green, and I did
not manufacture an inventory crisis.

What replaced it is a rhythm problem. Output this week was excellent in the middle and absent
at the edges: zero social on Aug 24 and Aug 30, zero blog on Aug 25, three blogs crammed into
one Sunday of which two shipped nearly unoptimized, and two slots that fired double. Every one
of those is a consequence of the same root cause, and it is the same root cause I have now
written down three weeks in a row: **nothing is scheduled in advance, so output tracks whether
a session happens to fire rather than what the calendar needs.**

The fix has not changed and it is not a content fix. **Schedule the week ahead in Late and
WordPress before the week starts, and put a verification gate at session end that runs
`yoast-check.py`, confirms `featured_media != 0`, and confirms the day's social actually
posted.** Today's missing featured image survived a full day on a live post and I only caught
it because I went looking during a review. That should not be how it gets caught.
