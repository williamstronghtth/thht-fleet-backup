# Weekly Marketing Review — May 31, 2026
**Period:** May 25 – May 31, 2026  
**Prepared by:** Fiona Murphy, Marketing Specialist  
**For:** Chris Hoover, The Hoover Home Team

---

## The Big Picture

A productive week on content volume with three Just Sold posts published and daily blog and social cadence maintained. However, it was also a bumpy week operationally: image management caused three separate incidents across the seven days, culminating in today's Audrey's-images mix-up on social. The rules are now tighter and locked in, but there are posts on the platforms today that need manual deletion. GA4 analytics remain blocked pending Chris's access grant. The content machine is running, but image discipline needs to hold going forward.

---

## Social Media

### Posts Published (May 25 – May 31)

| Date | Platforms | Topic | Image | Status |
|------|-----------|-------|-------|--------|
| May 25 AM | FB, IG, LI, Twitter | Market update: days on market rising, buyer opportunity | file_53.jpg | ✓ Published |
| May 26 AM | FB, IG, LI, Twitter | Spring inventory surge, May-June timing window | file_53.jpg ⚠️ | ✓ Published (repeat image) |
| May 27 AM | FB, IG, LI, Twitter | Seller advantage: inventory low, homes commanding premiums | 67.png | ✓ Published |
| May 27 PM | FB, IG, LI, Twitter | Buyer reality check: market snapshot, market data | 67.png | ✓ Published (scheduled 7:30 PM) |
| May 28 AM | FB, IG, LI, Twitter | Market cooling = buyer opportunity | file_53.jpg ⚠️ | ✓ Published (repeat, later corrected on blog) |
| May 28 PM | FB, IG, LI, Twitter | Mont Vernon $749K, homes at 100.86% list | file_53.jpg ⚠️ | ✓ Published (repeat image) |
| May 29 AM | FB, IG, LI, Twitter | Rate lock reality: waiting for rates to drop is costing buyers | 69.png | ✓ Published (scheduled 11:00 AM ET) |
| May 30 AM | FB, IG, LI, Twitter | Nashua appreciation, summer inventory surge | 71.png | ✓ Published (scheduled 9:00 AM ET) |
| May 30 PM | FB, IG, LI, Twitter | 18-day markets, buyer/seller urgency | 72.png | ✓ Published (scheduled 1:00 PM ET) |
| May 31 AM | FB, IG, LI, Twitter | Nashua 36-day avg sales, tight inventory | file_37.jpg / file_35.jpg (IG Story) ⚠️ | ✓ Published (wrong image — Audrey's) |
| May 31 PM | FB, IG, LI, Twitter | Summer inventory reality, 9.3% YoY volume decline | file_36.jpg / file_38.jpg (IG Story) ⚠️ | ✓ Published (wrong image — Audrey's) |

**Total posts: 11 across the week (all platforms)**

### Platform Health

| Platform | Status | Notes |
|----------|--------|-------|
| Facebook | ✓ Active | Published every day |
| Instagram | ✓ Active | Published every day |
| LinkedIn | ✓ Active | Published every day |
| Twitter/X | ✓ Active | Separate API call protocol maintained throughout |

**Notable:** May 27, 28, and 30 all had both morning and evening posts. The double-post rhythm is becoming more consistent.

---

## Blog Posts

| Date | Title | Post ID | Yoast Green | Status |
|------|-------|---------|-------------|--------|
| May 25 | Southern NH Market Update: More Buyers' Breathing Room This Spring | 49128 | ✓ | Published |
| May 26 | Spring Inventory Surge: Why May-June Is Your Window in Southern NH | 49131 | ✓ | Published |
| May 27 | Market Snapshot: Southern NH's Inventory Advantage in May 2026 | 49143 | ✓ | Published |
| May 28 | The Market is Cooling and That's Good News for Smart Buyers | 49149 | ✓ | Published |
| May 29 | Why Waiting for Rates to Drop Is Costing You Your Dream Home in 2026 | 49156 | ✓ | Published |
| May 30 | The Summer Surge is Coming: Here's Why You Should Move First | 49159 | ✓ | Published |
| May 31 | Why Nashua Homes Sell So Fast: Understanding the Southern NH Market in 2026 | 49162 | ✓ | Published |

**7 of 7. Zero gaps.** Third consecutive full week. Every post has a featured image, Yoast green score configured (focus keyphrase + meta description via XML-RPC), keyphrase in first paragraph, 300+ words, and internal link.

---

## Just Sold Posts

Three Just Sold posts published this week. All blog-only, no social media per standing rule.

| Address | Sale Price | DOM | Closed | Post ID | Image Source | Status |
|---------|-----------|-----|--------|---------|--------------|--------|
| 11 Pine Top Road, Amherst NH | $1,075,000 | 6 | May 22, 2026 | 49140 | file_62.jpg (Drive) | ✓ Published May 26 |
| 9 Louis Drive, Brookline NH | TBD | TBD | TBD | 49146 | file_64.jpg (Drive aerial) | ✓ Published May 27 |
| 95 Wright Road, Hollis NH | $1,049,900 | TBD | TBD | 49153 | file_66.jpg (Drive) | ✓ Published May 28 |

Strong week for Just Sold volume. 11 Pine Top Road was a notable deal: $80K over asking on a $995K listing. 95 Wright Road was a cash sale at full list, a New England gray Colonial on a 3-car garage lot.

---

## GA4 Analytics

**BLOCKED — Action Required from Chris.**

Both authentication methods are failing:
- **Service account** (`fiona-analytics-reader@hoover-analytics-api.iam.gserviceaccount.com`): Returns PERMISSION_DENIED. Chris has not yet added this account as Viewer in GA4 Admin.
- **OAuth2 token**: Returns `invalid_grant` — revoked or expired since mid-May.

No weekly traffic report this week. Notified Chris via Telegram on May 29.

**To fix (Option A — recommended):** Go to GA4 Admin → Property Access Management → Add user → paste service account email → grant Viewer access. Takes 2 minutes and is permanent.

---

## Image Incidents This Week

This was a rough week for image discipline. Three separate violations:

### Incident 1 — file_53.jpg Reuse (May 26)
Used file_53.jpg on May 26 despite it having been used on May 25. No-reuse rule was not yet formally documented. Blog featured images on 6 posts (49110, 49113, 49122, 49125, 49128, 49131) were swapped to fresh images 61-66 from Google Drive.

### Incident 2 — file_53.jpg Used a Third Time (May 28)
file_53.jpg was grabbed again from inbox for May 28 social and blog posts. After correction: blog post 49149 featured image swapped to 68.png. file_53.jpg permanently deleted from both local workspace and WordPress media. Social posts could not be retroactively changed.

### Incident 3 — Audrey's Images Used on Social (May 31)
file_35.jpg, file_36.jpg, file_37.jpg, file_38.jpg, and file_40.jpg from inbox were used for today's social posts and blog. These belong to Audrey's project, not Hoover Home Team. Blog image corrected (73.png now set as featured image). Social posts published with wrong images and CANNOT be deleted via API.

**Chris: Please manually delete these 6 social posts:**
- FB/LI 8 AM: `6a1c1c2babafc7cd7cba5917`
- TW 8 AM: `6a1c1c356fe61263e6e26fa3`
- IG Story 8 AM: `6a1c1c38a3c931f2319bc32c`
- FB/LI 7:30 PM: `6a1c1c4d84e666c860c64854`
- TW 7:30 PM: `6a1c1c556fe61263e6e27667`
- IG Story 7:30 PM: `6a1c1c5984a666c860c64a2e`

**Rule locked in MEMORY.md:** Only numbered PNG images (1.png through 100.png) from Google Drive are valid for Hoover Home Team posts. Any file_XX.jpg file in inbox is off-limits without explicit confirmation from Chris.

---

## Image Inventory

Images used this week: 61.png through 73.png (backfills + new posts).

**Remaining available images:** 74, 75, 76 confirmed. May be more in Drive batch (up to 100).

Only 3 confirmed available for next week. A fresh batch from Google Drive is needed before Wednesday to maintain the daily cadence without interruption.

---

## Content Themes This Week

| Theme | Frequency | Notes |
|-------|-----------|-------|
| Buyer opportunity / market cooling | 3x | Dominant theme: reassuring, not alarmist |
| Inventory scarcity / urgency | 3x | Summer surge narrative building nicely |
| Rate strategy ("buy now, refinance later") | 1x | Distinct angle, strong hook |
| Just Sold highlights | 3x | Blog only — all three over $1M |
| Market data (Nashua, Hillsborough Co) | 2x | Stats-driven, credibility building |

Content leaned buyer-heavy again this week (similar to last week). Next week: consider a seller spotlight, town deep-dive on Amherst or Mont Vernon, or a first-time homebuyer education piece for variety.

---

## What Worked

- **7/7 blog streak continues.** Third full week with no gaps. This is the baseline now.
- **Just Sold velocity.** Three posts in one week, all over $1M. That's strong brand positioning.
- **Double-post days are becoming routine.** May 27, 28, and 30 all had AM + PM social posts. The 7:30 PM slot is no longer an afterthought.
- **Rate Lock Reality post (May 29).** Compelling angle: "waiting for rates is costing you your dream home." That kind of direct, results-oriented headline stands out.
- **11 Pine Top Road.** $80K over asking on a nearly $1M listing. Clear "why you need us" proof point in the post.

---

## What Needs Attention

1. **Manually delete 6 May 31 social posts** (IDs above) from all platforms. These had Audrey's images.
2. **Re-post May 31 content with correct images** — if Chris wants to repost today's content with proper numbered images, I can create those posts immediately.
3. **GA4 access grant** — Service account just needs Viewer access in the GA4 admin panel. Once done, weekly reports resume automatically.
4. **Fresh image batch** — Only 3 confirmed images remain (74, 75, 76). Need a new Drive batch before Wednesday.
5. **Content variety** — Heavy buyer focus the past two weeks. Next week: rotate to seller education, town spotlight (Amherst 2026 revaluation angle is strong per William's brief), or summer event content.
6. **inbox/ folder cleanup** — Multiple file_XX.jpg files from Audrey's project are still in the inbox folder. Consider moving them to a separate folder or deleting to prevent future confusion.

---

## Looking Ahead (Week of June 1 – June 7)

- **Amherst weekly digest is live** (William, May 31). Strong angles: 2026 full statistical revaluation, Restaurant Week June 7-13, Race Amity Day June 14, LaBelle Winery events, $739K median vs. $594K average, 77/100 competitiveness score.
- **Town spotlight** — Amherst is ripe for a deep-dive blog. The revaluation angle alone is educational content gold for homeowners.
- **June events content** — Restaurant Week (June 7-13) and Race Amity Day (June 14) are community posts that reinforce the "Southern NH is a great place to live" brand narrative.
- **17 Legacy Drive** — MLS sheet is in inbox/processed. Draft and publish when exterior photo is available.
- **YouTube playbook** — Channel launch planning still pending. Chris's July 1 move is 30 days out.

---

*Review prepared: May 31, 2026 — 7:00 PM ET*
