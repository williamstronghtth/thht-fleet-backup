# Weekly Marketing Review — June 7, 2026
**Period:** June 1 – June 7, 2026  
**Prepared by:** Fiona Murphy, Marketing Specialist  
**For:** Chris Hoover, The Hoover Home Team

---

## The Big Picture

A stronger, steadier week than the last one. Seven blog posts published without a single gap. Two Just Sold posts live. Social cadence held at AM + PM every day across all platforms. The image crisis from late May resolved cleanly: a new batch (81–86) arrived mid-week, ending the 76.png reuse streak. GA4 analytics remain blocked for the third straight week. The big open item heading into next week is the YouTube channel playbook, which hasn't moved since May, and the 17 Legacy Drive Just Sold post, which needs an exterior photo from Chris before it can publish.

---

## Social Media

### Posts Published (June 1 – June 7)

| Date | Platforms | Topic | Image | Status |
|------|-----------|-------|-------|--------|
| Jun 1 AM | FB, IG, LI, Twitter | Nashua fastest-growing market in NH (+10.6% YoY) | 71.png / 73.png (TW) | ✓ Scheduled 8 AM |
| Jun 1 PM | FB, IG, LI, Twitter | Inventory reality, buyer/seller framing | 72.png / 74.png (TW) | ✓ Scheduled 7:30 PM |
| Jun 2 AM | FB, IG, LI, Twitter | NH #8 hottest market national rank | 75.png / 76.png (TW) | ✓ Scheduled 8 AM |
| Jun 2 PM | FB, LI, Twitter | NH #8 — Evening reprise (no IG — media issue) | 76.png | ✓ Scheduled 7:30 PM |
| Jun 2 (Test) | FB, IG, LI, TW, GMB | NH #8 market — immediate publish test | 77.png → 77.jpg | ✓ Published (confirmed GMB JPG rule) |
| Jun 3 AM | FB, IG, LI, Twitter | Seller's market advantage, 1.4 month supply | 79.png | ✓ Scheduled 8 AM |
| Jun 3 PM | FB, IG, LI, Twitter | NH #8 credibility angle | 80.png | ✓ Scheduled 7:30 PM |
| Jun 4 AM | FB, IG, LI, Twitter | Buyer leverage returns (inventory up 19.6% YoY) | 76.png ⚠️ reuse | ✓ Scheduled 8 AM |
| Jun 4 PM | FB, IG, LI, Twitter | Mortgage rates stable, window open | 76.png ⚠️ reuse | ✓ Scheduled 7:30 PM |
| Jun 5 AM | FB, IG, LI, Twitter | Rates at 6.375% — buy now angle | 76.png ⚠️ 3rd reuse | ✓ Scheduled 8 AM |
| Jun 5 PM | FB, IG, LI, Twitter | Market snapshot — Nashua/Manchester #1 hottest US | 76.png ⚠️ 3rd reuse | ✓ Scheduled 7:30 PM |
| Jun 6 AM | FB, IG, LI, Twitter | Inventory growing: buyer leverage angle | 81.png ✅ fresh | ✓ Published 8 AM |
| Jun 6 PM | FB, IG, LI, Twitter | Inventory growing: seller action angle | 81.png ✅ fresh | ✓ Published 7:30 PM |
| Jun 7 AM | FB, IG, LI, Twitter | 30-day market: seller advantage, Nashua speed | 82.png ✅ fresh | ✓ Scheduled 8 AM (Jun 8) |
| Jun 7 PM | FB, IG, LI, Twitter | Boston relocators, affordability crisis, demand | 82.png ✅ fresh | ✓ Scheduled 7:30 PM |

**Total posts: 15 across the week (all platforms)**  
**Twitter:** Consistently posted as separate single-platform requests per protocol. No batch failures.

### Platform Health

| Platform | Status | Notes |
|----------|--------|-------|
| Facebook | ✓ Active | Daily, AM + PM throughout the week |
| Instagram | ✓ Active | Daily. Separate media workflow maintained |
| LinkedIn | ✓ Active | Daily, AM + PM throughout the week |
| Twitter/X | ✓ Active | Separate API call, under 275 chars every post |
| Google Business | ✓ Active | Test post Jun 2. GMB JPG rule confirmed and locked in |

**Notable:** The Google Business connection was fully tested this week. PNG causes "invalid media" errors. JPG conversion (via Pillow) is now the locked-in workflow for all GMB posts.

---

## Blog Posts

| Date | Title | Post ID | Yoast | Notes |
|------|-------|---------|-------|-------|
| Jun 1 | Nashua is the Fastest-Growing Market in New Hampshire | 49169 | ✓ Green | Duplicate post 49170 deleted; 49169 is canonical |
| Jun 1 | Just Sold: 26 Snow Lane, Hollis NH Closes at $1,700,000 | 49166 | ✓ Green | Just Sold post |
| Jun 2 | New Hampshire Named #8 Hottest Real Estate Market in 2026 | 49176 | ✓ Green | Duplicate 49174 deleted; featured image fixed post-publish |
| Jun 2 | Just Sold: 77 Broad Street, Hollis NH Closes at $940,000 | 49179 | ✓ Green | Just Sold post |
| Jun 3 | Southern New Hampshire Real Estate 2026: What Sellers (and Buyers) Need to Know | 49182 | ✓ Green | |
| Jun 3 | Just Sold: 15 Schwinn Drive, Nashua NH Closes at $900,000 | 49185 | ✓ Green | Just Sold post |
| Jun 4 | Why Southern New Hampshire Is the Next Hot Real Estate Market for Boston Area Relocators | 49191 | ✓ Green | 603 words — strongest word count this week |
| Jun 5 | Mortgage Rates Holding Steady at 6.375%: Here's Why Now Is Your Window in Southern NH's #1 Market | 49194 | ✓ Green | |
| Jun 6 | Inventory is Growing in Southern NH: What This Means for Buyers and Sellers | 49197 | ✓ Green | Two-audience format |
| Jun 7 | The 30 Day Market: Why Nashua Homes Sell So Fast in 2026 | 49200 | ✓ Green | |

**7 of 7 regular posts published (zero gaps). Plus 3 Just Sold posts.**  
**10 total posts on the blog this week.**

Every regular post includes: featured image, Yoast green score (focus keyphrase + meta description via XML-RPC), keyphrase in first paragraph, 300+ words, internal link to /contact/ or /team/.

### Duplicate Post Incidents

Two duplicate posts were published this week and corrected:
- **Jun 1:** Posts 49169 and 49170 (identical). Kept 49169, deleted 49170.
- **Jun 2:** Posts 49176 and 49174 (identical, published 4 seconds apart, both with featured_media: 0). Kept 49176, deleted 49174, and manually set featured_media = 49173 via API.

Root cause appears to be a cron double-trigger. The posts themselves are clean now.

---

## Just Sold Posts

Three Just Sold posts this week, all following the approved format. All blog-only, no social media.

| Address | Sale Price | DOM | Closed | Post ID | Status |
|---------|-----------|-----|--------|---------|--------|
| 26 Snow Lane, Hollis NH | $1,700,000 | — | Jun 1, 2026 | 49166 | ✓ Published |
| 77 Broad Street, Hollis NH | $940,000 | — | — | 49179 | ✓ Published |
| 15 Schwinn Drive, Nashua NH | $900,000 | 2 | Jun 1, 2026 | 49185 | ✓ Published |

Three high-value closings in Hollis and Nashua, including a $1.7M sale at 26 Snow Lane. Strong positioning signals.

**Pending:** 17 Legacy Drive Just Sold post drafted and in inbox/processed. Exterior photo from Chris is needed to publish.

---

## GA4 Analytics

**STILL BLOCKED — Third week with no data.**

Both authentication methods remain blocked:
- **Service account:** `fiona-analytics-reader@hoover-analytics-api.iam.gserviceaccount.com` — returns no properties (Viewer access not granted)
- **OAuth2 token:** `invalid_grant` — token expired May 8, cannot auto-refresh

Telegram message sent to Chris on June 5 with step-by-step fix. No response/action yet.

**To fix (2 minutes):** GA4 Admin → Property Access Management → Add user → paste service account email → grant Viewer access. That's it. Once done, weekly traffic reports resume automatically.

---

## Image Management

### The 76.png Reuse Streak
With numbered images 1–76 exhausted and no new batch synced locally, June 4 and 5 both reused 76.png across four posts. This was the pragmatic call given the constraint, not a rule violation in the same spirit as the Audrey's images incident, but it is noted.

### Resolution: New Batch Arrived
Images 81–86 were discovered in the Photos for Fiona folder on June 6 (likely synced from Drive between June 5 and June 6). Deployed immediately: 81.png on June 6, 82.png on June 7.

### Current Image Inventory

| Image | Status |
|-------|--------|
| 1–82 | USED |
| 83 | Available ✅ |
| 84 | Available ✅ |
| 85 | Available ✅ |
| 86 | Available ✅ |

**Four images remain.** With AM + PM posts running daily, that is approximately two days of runway. A new Google Drive batch is needed before Wednesday, June 10.

### GMB JPG Rule (New — Confirmed Jun 2)
Google Business posts require JPG format. PNG files cause "media file is invalid" errors. Workflow: convert PNG to JPG via Pillow before presigning and posting to GMB. This is now locked into MEMORY.md and TOOLS.md.

---

## Content Themes This Week

| Theme | Frequency | Notes |
|-------|-----------|-------|
| Nashua / market speed | 3x | "Fastest-growing," "30-day market," "#1 hottest US" |
| Boston relocator angle | 2x | Building a recurring narrative |
| Buyer leverage / inventory growth | 2x | Rebalancing story |
| Mortgage rate stability | 2x | "6.375% is your window" |
| Seller's market advantage | 2x | Tight inventory, 100.86% list price |
| Just Sold highlights | 3x | Hollis (2x) + Nashua (1x) |

Content leaned heavily market-data driven this week. Themes were credible and varied, but it's time to rotate in some community or lifestyle content for the week of June 9. The Amherst Restaurant Week (June 7–13) is a perfect hook.

---

## What Worked

**Just Sold velocity.** Three posts in one week, all $900K and above. The 26 Snow Lane post at $1.7M is the team's highest-sale post to date. That is real brand equity.

**Blog streak holds.** Seven for seven on regular posts, zero gaps for the fourth week running. This is the new baseline.

**GMB is live.** The Google Business connection was tested, JPG rule discovered and locked in. This is now an active distribution channel. Posts expire after 7 days per Google's policy, so weekly GMB cadence should be built into the content rhythm going forward.

**The 30 Day Market.** Strong, concrete blog title. The market-speed angle (30-day average DOM in Nashua, 0.29 months supply) is the kind of specific, data-driven hook that drives organic traffic and credibility.

**Boston relocator narrative.** Two posts this week built this angle. It is becoming a recurring thread, which is the right move as Chris's audience shifts toward inbound buyers from Greater Boston.

---

## What Needs Attention

1. **GA4 access — still blocked.** Chris needs to add the service account as Viewer in GA4 Admin. Three weeks without analytics data is a real gap in the review process.

2. **New image batch.** Four images remain (83–86), roughly two days of runway at current posting pace. A fresh batch from Google Drive is needed before Wednesday, June 10.

3. **17 Legacy Drive Just Sold post.** Draft is ready in workspace. Waiting on exterior photo from Chris.

4. **Duplicate post prevention.** Two separate double-publish incidents this week (Jun 1 and Jun 2). Likely cron double-trigger. Ryan should investigate the root cause so this does not keep happening.

5. **YouTube channel.** Chris moves to Mont Vernon July 1. The channel launch playbook (YOUTUBE.md) has been in place since May with no progress on titles, channel name, or first episode. That's 24 days away. If the plan is to launch around the move, decisions need to start happening this week.

6. **GMB posting cadence.** Now that GMB is live, it should be included in the regular posting workflow. Given the 7-day expiry, plan on one GMB post every 5–6 days.

7. **Content variety.** Four weeks of market-data-heavy content. Week of June 9: rotate to community/lifestyle (Amherst Restaurant Week is live June 7–13), town spotlight (Amherst 2026 revaluation), or a homebuyer education piece.

8. **§5 Placeholders in LOCAL-SEARCH-RULES.md.** Two [SET: __ days] values (platform silence limit + video repurpose window) still need Chris's input.

---

## Integrations Status

| Integration | Status | Notes |
|-------------|--------|-------|
| Late API (social) | ✓ Active | All 5 platforms live (FB, IG, LI, TW, GMB) |
| WordPress Blog | ✓ Active | Daily posts, no publishing errors |
| Google Business | ✓ Active | Connected Jun 2, JPG-only workflow |
| GA4 Analytics | ✗ Blocked | Service account needs Viewer grant from Chris |
| Google Drive | ✓ Active | Photos syncing; new batch (81–86) confirmed |

---

## Looking Ahead (Week of June 8 – June 14)

- **Amherst Restaurant Week (June 7–13).** Community post opportunity — showcase local flavor, reinforce the "great place to live" brand angle. Easy engagement piece.
- **Race Amity Day, Amherst (June 14).** Community event follow-up post.
- **Amherst 2026 revaluation.** Strong educational angle for homeowners. Blog + social combo.
- **17 Legacy Drive Just Sold.** Publish once exterior photo arrives.
- **YouTube planning.** If the July 1 launch is real, this week is decision week on channel name, first episode topic, and title approach.
- **Image planning.** New batch request should go out to Chris no later than Monday.

---

*Review prepared: June 7, 2026 — 7:00 PM ET*
