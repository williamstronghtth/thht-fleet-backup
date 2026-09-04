# Weekly Marketing Review — June 28, 2026
**Period:** June 22 – June 28, 2026
**Prepared by:** Fiona Murphy, Marketing Specialist
**For:** Chris Hoover, The Hoover Home Team

---

## The Big Picture

A rough week under the hood, even if it mostly looked fine from the outside. Social posts ran every day. Blog publishing, however, broke down on four of seven days due to cascading API and server issues: Late API returned 401 on June 24 and 25, WordPress REST API failed on June 27 and 28. The pre-scheduled posts from June 20 fired on June 24, 25, and 28 with images already used on June 13 (ne-04, ne-05, ne-06), a reuse violation that was flagged as urgent in last week's review but was not corrected in time.

The other number that matters this week: **July 1 is three days away.** Chris moves to Mont Vernon on Tuesday. The YouTube channel still has no name and no first episode confirmed. The entire Unsplash image library (all 20 images) is now exhausted. Heading into next week with zero image runway is not sustainable.

---

## Social Media

### Posts Published (June 22 – June 28)

| Date | Time | Platforms | Topic | Image | Status |
|------|------|-----------|-------|-------|--------|
| Jun 22 | 8 AM ET | FB, IG, LI, TW | Buyer angle: inventory up, prepared buyers winning | unsplash-ne-17.jpg | ✓ Scheduled |
| Jun 22 | 7:30 PM ET | FB, IG, LI, TW | Seller angle: fast market advantage | unsplash-ne-18.jpg | ✓ Scheduled |
| Jun 23 | 8 AM ET | FB, LI, TW | NH #1 hottest market, buyer focus | none (no image) | ✓ Posted — Instagram skipped |
| Jun 23 | 7:30 PM ET | FB, LI, TW | Market cooling, buyer power angle | none (no image) | ✓ Posted — Instagram skipped |
| Jun 24 | 8 AM ET | FB, IG, LI, TW | 32 days to sold, seller opportunity | unsplash-ne-04.jpg ⚠️ reuse | Pre-scheduled from June 20, fired automatically |
| Jun 24 | 7:30 PM ET | FB, IG, LI, TW | 410 Nashua sales in 30 days, buyer prep | unsplash-ne-04.jpg ⚠️ reuse | Pre-scheduled from June 20, fired automatically |
| Jun 25 | (no new posts) | — | API blocked, Late API 401 | — | ⚠️ No original posts created |
| Jun 26 | 8 AM ET | FB, IG, LI, TW | First-time buyers winning, rates + inventory power | unsplash-ne-19.jpg ✅ | ✓ Scheduled (Post ID 6a3e6338) |
| Jun 26 | 7:30 PM ET | FB, IG, LI, TW | Market data: 35% first-time buyers, Northeast advantage | unsplash-ne-19.jpg ✅ | ✓ Scheduled (Post ID 6a3e634a) |
| Jun 27 | 8 AM ET | FB, IG, LI, TW | The Buyer's Moment: market shift, Q1 median down 1.7% | unsplash-ne-20.jpg ✅ | ✓ Scheduled (Post ID 6a3fb4a4) |
| Jun 27 | 7:30 PM ET | FB, IG, LI, TW | Million-Dollar Milestone: 373% increase, equity narrative | unsplash-ne-20.jpg ✅ | ✓ Scheduled (Post ID 6a3fb4b9) |
| Jun 28 | 8 AM ET | FB, IG, LI, TW | Buyer's Window: rates at 6.25%, concessions returning | unsplash-ne-06.jpg ⚠️ reuse | ✓ Scheduled (Post ID 6a410647) |
| Jun 28 | 7:30 PM ET | FB, IG, LI, TW | Hillsborough median down 1.7%, stabilization angle | unsplash-ne-06.jpg ⚠️ reuse | ✓ Scheduled (Post ID 6a41064a) |

**⚠️ IMAGE REUSE VIOLATIONS THIS WEEK:**
- **June 24:** Both posts used unsplash-ne-04.jpg. That image was used June 13 (blog) and June 20 (social). Pre-scheduled June 20 — not corrected before firing.
- **June 28:** Posts used unsplash-ne-06.jpg. That image was used June 13 and also pre-scheduled for June 28 from the June 20 session, creating a double-schedule conflict.

**⚠️ JUNE 26 POTENTIAL DUPLICATES:**
June 26 had both pre-scheduled posts (unsplash-ne-05.jpg, scheduled June 20) and manually-created posts (unsplash-ne-19.jpg, created June 26). It's possible two separate post pairs went live that day. This should be verified in the Late API dashboard.

**Total posts published/scheduled: 12–14 (estimated, including potential June 26 duplicates)**

### Platform Health

| Platform | Status | Notes |
|----------|--------|-------|
| Facebook | ✓ Active | Daily throughout the week |
| Instagram | ⚠️ Inconsistent | Skipped June 23 (no image in that session's posts). |
| LinkedIn | ✓ Active | Daily AM + PM |
| Twitter/X | ✓ Active | All posted separately, under 275 chars |
| Google Business | ⚠️ Absent | Not included in any post this week. GMB may have gone dark. |

---

## Blog Posts

| Date | Title | Post ID | Yoast | Notes |
|------|-------|---------|-------|-------|
| Jun 22 | Southern New Hampshire Real Estate Market Update: Week of June 22, 2026 | 49340 | ✓ Green | Full green score, 5 market angles, featured image set |
| Jun 23 | Manchester-Nashua Ranked #1 Hottest Housing Market in America | 49342 | ✗ Missing | Published with no featured image, Yoast blocked by ModSecurity — incomplete |
| Jun 24 | After Two Years of Bidding Wars, Buyers Finally Have Breathing Room | ✗ Not published | — | Draft in /drafts/ — blocked by Late API 401 |
| Jun 25 | Buyer's Guide: Why June 2026 Is the Time for Southern New Hampshire | ✗ Not published | — | Draft in /drafts/ — blocked by Late API 401 |
| Jun 26 | Why First-Time Home Buyers Are Winning Right Now in Southern New Hampshire | 49344 | ✓ Green | Full green score, 400+ words, internal link, featured image |
| Jun 27 | Southern New Hampshire Real Estate Market Update: June 2026 | ✗ Not published | — | Draft in inbox/processed/ — WordPress auth failure (401) |
| Jun 28 | Why 44 Days? (And What You Can Do About It) | ✗ Not published | — | Draft in inbox/processed/ — Mod_Security blocking REST API (406) |

**Blog record: 2 of 7 days published cleanly. 1 published with missing image + SEO (June 23). 4 missed due to technical blockers.**

This is the worst blog week since the April gaps. The mandatory daily blog requirement broke down across four consecutive days (June 24-25: Late API 401, June 27-28: WordPress failures). The drafts exist — they just need to be published. Three drafts ready right now:
- `/root/agents/fiona-murphy/workspace/drafts/blog-buyers-market-june-24.md`
- `/root/agents/fiona-murphy/workspace/drafts/blog-buyers-market-june-25.md`
- `/root/agents/fiona-murphy/workspace/inbox/processed/daily-content-2026-06-27-blog-draft.md`
- `/root/agents/fiona-murphy/workspace/inbox/processed/daily-content-2026-06-28-blog-draft.md`

**Action required:** Chris needs to either manually publish these via WordPress admin, or the Mod_Security WAF configuration needs to be fixed. Featured image for June 28 post is already uploaded (Media ID 49346).

Also: **Post 49342 (June 23) is missing its featured image and Yoast SEO.** It should be updated with a featured image and have focus keyphrase + meta description set via XML-RPC. Focus keyphrase: "Manchester-Nashua hottest housing market."

---

## Just Sold Pipeline

No new Just Sold posts this week.

| Property | Status | Blocker | Outstanding Since |
|----------|--------|---------|-------------------|
| 17 Legacy Drive | ⏳ Pending | Exterior photo needed from Chris | Jun 7 (3 weeks) |
| 14 Boylston Terrace | ⏳ Pending | Closing status + exterior photo in Drive | Unknown |
| Inbox PDFs (June 10 batch) | ⏳ Deferred | ~15 PDFs, closing status unknown | Jun 10 |

The 17 Legacy Drive post has been waiting three weeks. At this point, a decision is needed: either the photo arrives and the post goes live, or Chris confirms there is no exterior photo and we handle it as an exception (interior shot, like Chandler Way).

---

## Content Themes This Week

| Theme | Frequency | Notes |
|-------|-----------|-------|
| Buyer leverage and market shift | 4x | Median down 1.7%, 44 days, buyer's window — heavy rotation this week |
| Market rankings and data | 2x | NH #1 hottest, Manchester-Nashua angle |
| First-time buyers | 1x | Strong post June 26, timely with 35% first-time buyer share |
| Million-dollar market strength | 1x | June 27 evening — 373% five-year surge angle |
| Seller advantage | 1x | June 22 evening |

The buyer angle dominated this week, which is appropriate given the market data (median down 1.7%, DOM up 38%). That said, the rotation was narrower than usual — seller content, local spotlight, and community content were mostly absent. Next week should include a town spotlight (Mont Vernon, especially with Chris's move) and a seller education piece.

---

## Image Management

**Status: CRITICAL — Zero images remaining.**

All 20 Unsplash New England images (ne-01 through ne-20) are now used. All numbered PNG images (1 through 85) are used. There are no available images for next week's posts without a new batch.

| Image Batch | Status |
|-------------|--------|
| Numbered PNGs 1–85 | All USED |
| Unsplash ne-01 through ne-20 | All USED (ne-20 used June 27, ne-06 reused June 28) |
| Google Drive new batch (86+) | Not yet synced |
| New Unsplash pull | Not yet done |

**Action required immediately:**
1. Chris to upload new numbered batch (86+) to the Google Drive Photos for Fiona folder, OR
2. Pull a new 20-image Unsplash batch (New England real estate, same CC0 license approach)

Without new images, Monday's posts cannot go out with fresh visuals.

---

## Technical Issues This Week

### 1. Late API 401 (June 24-25)
The Late API returned 401 Unauthorized on June 24. Cause may have been an API key rotation or session expiry. Telegram sent to Chris on June 24. API was working again by June 26 (possibly after a key refresh or automatic reset). No root cause confirmed.

**Status:** Resolved by June 26, but no explanation logged. If it happens again, check the API key in TOOLS.md first before escalating.

### 2. WordPress REST API Failures (June 27-28)
- **June 27:** WordPress returned 401 (App Password authentication failed)
- **June 28:** WordPress returned 406 (Mod_Security WAF blocking JSON POST requests)

This is the same Mod_Security issue that first appeared months ago. Chris fixed it temporarily, but it appears to have recurred or the fix was partial. Image uploads work (binary upload bypasses the WAF), but creating posts via REST API does not.

**To fix:** Chris needs to either:
- Add a WAF rule exception for the WordPress REST API endpoint, or
- Use a plugin like WP REST API Authentication to bypass the restriction

**Workaround in use:** Blog drafts are being saved to inbox/processed/ and require manual publish via WordPress admin.

---

## What Worked

**June 22 Sunday post.** Consistent, full platform execution — blog with green Yoast score, AM buyer angle, PM seller angle, all four platforms including Instagram. Clean execution day.

**First-time buyer angle (June 26).** The 35% first-time buyer share is a compelling data point, and the post landed cleanly. Full green Yoast, 400+ words, sharp angles. This topic should be revisited — it has strong engagement potential with the younger relocator audience.

**Million-Dollar Milestone (June 27 PM).** The 373% five-year surge in $1M+ sales is one of the most dramatic data points in the market. The equity narrative paired with Boston spillover is a strong seller-confidence piece.

**Content drafts ready.** Even on blocked days, the content brief was processed and drafts were written. Four complete post-ready drafts sitting in the workspace. The execution pipeline did not break down — only the publishing layer did.

---

## What Needs Attention

### 1. ⚠️ CRITICAL: Blog Post Backlog (4 Drafts Unpublished)
June 24, 25, 27, and 28 blog posts were drafted but never published. Chris should manually upload these via WordPress admin. The June 28 featured image (Media ID 49346) is already uploaded. This is an SEO gap that compounds over time.

### 2. ⚠️ CRITICAL: Image Inventory at Zero
No images remain for next week. Without a new batch, posts next week will require reusing already-used images or going imageless. Instagram requires media — no new images means no Instagram posts.

### 3. ⚠️ CRITICAL: July 1 Move — YouTube Still Undecided
Chris moves to Mont Vernon in **3 days.** The YouTube channel has no name, no first episode, and no launch content. Three weeks ago the channel was "10 days away." Now it is closer. Decisions needed:
- Channel name: "The Granite Real" vs "Live Southern NH" (or another option)
- Episode 1 topic
- Will there be a launch-day video?

If the answer is "not yet," that is fine — but it needs to be said explicitly. The content machine is primed to support a launch.

### 4. ⚠️ Fix Post 49342 (June 23 Blog)
The Manchester-Nashua #1 hottest market post (49342) published without a featured image and without Yoast SEO metadata. It needs:
- A featured image added (any available unsplash image, or pull a fresh one)
- Focus keyphrase set: "Manchester-Nashua hottest housing market"
- Meta description set via XML-RPC (120–156 chars)

### 5. ⚠️ Verify June 26 for Duplicate Posts
The June 26 session created new posts (ne-19.jpg) while pre-scheduled posts (ne-05.jpg from June 20) may also have fired. If both sets went live, there are duplicate posts on Facebook, LinkedIn, and Twitter for June 26. Worth checking the Late API dashboard.

### 6. Google Business — Dark Again
GMB was not included in any posts this week. Posts expire after 7 days per Google's policy. The GMB profile is likely dark heading into next week. Include GMB in every batch from July 1 forward.

### 7. Just Sold — 17 Legacy Drive at 3 Weeks
This draft has been waiting for an exterior photo since June 7. Either the photo comes or we make a call on an alternative. Three weeks is too long to leave a closed sale unannounced.

---

## Integrations Status

| Integration | Status | Notes |
|-------------|--------|-------|
| Late API (social) | ✓ Active | Working as of June 26; was down June 24-25 |
| WordPress Blog | ⚠️ Broken | REST API blocked by Mod_Security; requires manual publish |
| Google Business | ⚠️ Dark | Not posted this week; profile may have gone silent |
| Instagram | ⚠️ Inconsistent | Skipped June 23 (no image attached to that session) |
| Google Drive | ⚠️ Critical | Image inventory at zero; new batch not yet synced |
| GA4 Analytics | ✗ Blocked | Service account still needs Viewer access from Chris |

---

## Looking Ahead (Week of June 29 – July 5)

**The week of July 1 is a brand milestone.** Chris Hoover moves to Mont Vernon, NH on Tuesday. Everything the content machine has been building toward — Boston relocators, Southern NH lifestyle, community focus — becomes personal and credible the moment Chris is physically there.

Priorities for the week:
- **Publish the 4 unpublished blog drafts** via WordPress admin (or fix Mod_Security)
- **Pull a new Unsplash image batch** (20 New England real estate images, CC0) before Monday posts
- **Fix Post 49342** (featured image + Yoast SEO)
- **Mont Vernon move content:** A post about Chris arriving, personal narrative ("I made the move I've been telling clients to make"), or a "first impressions" angle. This is the most authentic content the team can produce right now.
- **YouTube: final decision.** If it launches around the move, this is the week.
- **GMB back in every batch.**
- **17 Legacy Drive Just Sold decision:** photo or proceed without.
- **Check June 26 for duplicate posts** and clean up if needed.

---

## The Number That Matters

**3.** Three days until Chris is in Mont Vernon. The content is ready for this moment. The question is whether we shape the narrative around the move or let it pass without content. A founder relocating to serve a market he believes in — that is a story. Tell it.

---

*Review prepared: June 28, 2026 — 7:00 PM ET*
*Fiona Murphy, Marketing Specialist, The Hoover Home Team*
