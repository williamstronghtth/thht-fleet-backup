# Weekly Marketing Review — Week of August 10 to August 16, 2026

Prepared by Fiona | The Hoover Home Team | Southern NH

---

## 1. Output Scorecard

### Blog posts (WordPress) — 3 published across 7 days
Verified against the WP REST API (published status, Aug 10–16):

| Date | Post | ID | Notes |
|---|---|---|---|
| Aug 10 | Rate Stability Is Here: What It Means for Southern NH Buyers in August | 49535 | Featured media 49534 (file_99). Yoast fields set, needs editor Update for green dot |
| Aug 12 | Southern NH Market Reality at 6.69%: Why Sellers Have the Advantage | 49536 | ⚠️ **featured_media = 0 — NO featured image set.** Violates rule #19. file_176 was planned but never uploaded |
| Aug 15 | Back-to-School Southern NH Homes: Why Families Move Now | 49539 | Featured media 49538 (file_179). All 15 Yoast checks GREEN |

- **Blog gaps: Aug 11, 13, 14, 16 — four missed days.** Drafts were written for Aug 12/13/14 (in inbox/processed) but Aug 13 and Aug 14 never published. Aug 16's blog got drafted as the *Aug 17* Saturday post (blog-publish-2026-08-17.md, media 49546 uploaded) and handed to Chris for manual entry, so today also has no live post.
- This is the **same publishing-consistency problem flagged last week**, and it got worse: 3/7 blog days this week vs 5 posts last week. The session-end publish-verification gate I proposed to William on Aug 10 was never implemented.

### Social posts — disrupted by a Late API blocker, then recovered
- **Aug 11–14: social posting was down.** A "120/120" limit/blocker on the Late API stopped batch and Twitter posts. Blog drafts continued on my end but social did not publish.
- **Aug 14: live-tested the API — all 6 accounts active, Bluesky test post published instantly.** Blocker cleared/reset. Aug 11–14 scheduled social did not backfill (those slots were simply lost).
- **Aug 15: full cadence restored** — 8 AM batch (FB/IG/LI) + Twitter + 7:30 PM batch + Twitter, all scheduled and confirmed (file_181 AM, file_180 PM).
- **Aug 16 (today): Milford "Emerging Buyer Window" post scheduled 8 AM across FB/IG/LinkedIn/GMB/Twitter** (Late 6a819fa9… batch + 6a819f99… Twitter), file_172.

---

## 2. Content Themes Covered
- Mortgage rates / rate stability at 6.69% (Aug 10, Aug 12 blogs + social)
- Seller's advantage in a shifting market
- Back-to-school / family relocation timing (Aug 15 blog + both social slots)
- Milford's emerging buyer window — 7% YoY price drop (Aug 16)
- YouTube: Amherst NH town deep-dive ("Living in Amherst, NH: The Complete Town Guide") — delivered full packaging (3 titles, hook, 25 tags, thumbnail concept, 3 short-form clip ideas). Awaiting final publish/link.

Good thematic rotation, on-brand, no dashes. The weak spot is **volume and consistency, not topic quality.**

---

## 3. The Big Story: An API Outage Broke the Streak
Last week the constraint was image supply (now solved). **This week the constraint was two failures stacking:**
1. **Late API blocker (Aug 11–14)** killed social for four days. Outside my control, but no fallback fired and lost slots were never recovered.
2. **Blog publishing consistency** kept slipping — the unenforced "publish" step at session end. Drafts written, never pushed (Aug 13, 14), plus one post shipped with no featured image (Aug 12).

Image inventory held up fine throughout: sits at **9 available** now (file_172, 173, 174, 175, 176, 177, 182, 183, 184). Chris kept the tap on — sent file_179/180/181 (Aug 14) and file_182/183/184 (Aug 16). Supply is NOT the problem.

---

## 4. Open Follow-Ups (carried + new)
1. **Publish-verification gate — STILL NOT BUILT.** NEW URGENT. Proposed to William Aug 10; this week proved why it's needed (4 blog gaps). A session-end check that queries the WP API for a post dated today, and blocks a clean close + alerts Chris if none exists.
2. **Post 49536 has no featured image (media 0).** NEW. Upload file_176 (or another general-use image) and set as featured, then run the Yoast checker. Currently can't be Yoast-green without it.
3. **Aug 13 + Aug 14 blog drafts never published.** NEW. Decide: backfill them or let them go. Drafts sit in inbox/processed.
4. **Aug 17 Saturday blog** — content + featured image (media 49546) ready; needs Chris to create the post in WP or me to push it via API.
5. **Yoast score dots** — posts 49535 (and 49536 once image added) need Chris to open in the WP editor and hit Update so the linkdex dot repaints green.
6. **Legacy image violation (49085/49086)** — CARRIED from prior weeks. Still using reserved "6-odell-drive" image as featured. Inventory is healthy now (9 available) — swap in a clean general-use image and close this.
7. **Amherst YouTube video** — packaging delivered; awaiting published link to finalize description/pinned comment and start staggered repurposing (Shorts/Reels/TikTok/X/LinkedIn/blog).
8. **Image inventory** — 9 on hand ≈ 3 days at 3/day. Ask Chris for a fresh batch by Aug 18–19 to keep the buffer.

---

## 5. What's Working
- **Image supply stayed solved** — zero shortage-driven misses, single-use-then-delete discipline held, no duplicate incidents.
- **Fast API recovery** — caught the blocker, live-tested, and had full 6-platform cadence back within a day (Aug 15).
- **Aug 15 was a clean day** — green blog + full 2x social, the template for what every day should look like.
- **YouTube distribution work** — Amherst deep-dive packaged to spec per YOUTUBE.md.
- Strong market-data storytelling from William's briefs (rates, above-asking %, DOM, Milford YoY).

**Bottom line:** Image supply is no longer the story — reliability is. Two things broke the week: an API outage (external, recovered) and the still-unbuilt blog publish gate (internal, fixable). Last week I said "close publishing consistency and we're at a 7-blog week." This week it went the wrong way — 3/7. The single highest-leverage fix remains the **session-end publish-verification gate.** Everything else is healthy.
