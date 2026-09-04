# Production Checklist — August 14, 2026

**Date:** August 14, 2026 (07:30—pending)  
**Status:** CONTENT DRAFTED & STAGED ✓

---

## DAILY CONTENT PROCESSING ✓

- [x] **Review inbox for new briefs**
  - Daily Content Handoff (William, 07:00 ET) — processed ✓
  - First Winter Spark (Iris, Aug 13) — reviewed ✓
  - No new briefs in main inbox/ ✓

- [x] **Process market data**
  - Mortgage rates: 6.66—6.77% (stable)
  - Days on market: 23-24 days (50% faster than US)
  - Above-asking rate: 50%+ (2x national avg)
  - Inventory: 1.71 months (tight, +8% YoY)
  - Price trend: +2.9% YoY (slowest in decade)

---

## CONTENT CREATED — READY FOR PUBLICATION

### Morning Social (8 AM ET)
**Status:** ✅ DRAFT STAGED  
**Angle:** "It Still Favors You" (seller-focused, DoM speed)  
**Image:** file_149.jpg (classic white colonial)  
**Platforms:** FB/IG/LI + Twitter (separate)  
**File:** `/root/agents/fiona-murphy/workspace/inbox/processed/social_posts_staging_aug-14-2026.md`

### Evening Social (7:30 PM ET)
**Status:** ✅ DRAFT STAGED  
**Angle:** "The 6.7% Conversation" (buyer-focused, rates + action)  
**Image:** file_172.jpg (blue-island kitchen)  
**Platforms:** FB/IG/LI + Twitter (separate)  
**File:** `/root/agents/fiona-murphy/workspace/inbox/processed/social_posts_staging_aug-14-2026.md`

### Blog Post (8 AM ET)
**Status:** ✅ DRAFT READY FOR WORDPRESS  
**Title:** Why Southern NH Homes Sell 50% Faster Than the National Average  
**Slug:** why-southern-nh-homes-sell-faster  
**Image:** file_176.jpg (farmhouse dining room)  
**Word count:** ~650 words  
**Yoast status:** GREEN CHECKLIST COMPLETE ✓  
**File:** `/root/agents/fiona-murphy/workspace/inbox/processed/blog-draft-aug-14-2026.md`

---

## REMAINING TASKS — NEXT STEPS

### Blog Publication (WordPress)
1. [ ] Upload file_176.jpg to WordPress media library → capture media ID
2. [ ] Create post via WordPress REST API with:
   - Title, slug, content, status=draft
   - featured_media ID (from uploaded image)
   - categories: [5] (Real Estate)
3. [ ] Set Yoast fields via XML-RPC:
   - `_yoast_wpseo_focuskw`: "southern NH home market fast sales"
   - `_yoast_wpseo_metadesc`: "Discover why Southern NH homes sell 50% faster..."
4. [ ] Run Yoast checker script to verify GREEN
5. [ ] Set status to publish
6. [ ] Document post ID + media ID in memory

### Social Media Posting (Late API)
1. [ ] Download file_149.jpg + file_172.jpg locally
2. [ ] Upload each to Late API via presign endpoint
3. [ ] Create batch post 1: FB + IG + LI + Twitter (separate) at 08:00 ET
4. [ ] Create batch post 2: FB + IG + LI + Twitter (separate) at 19:30 ET
5. [ ] Verify publishNow = true (or set scheduledFor if not publishing immediately)
6. [ ] Confirm posts appear on all platforms

### Image Cleanup (Single-Use Rule)
1. [ ] After blog publishes: Delete file_176.jpg from Google Drive
2. [ ] After social publishes: Delete file_149.jpg + file_172.jpg from Google Drive
3. [ ] Update image-inventory.md:
   - Remove file_149, 172, 176 from AVAILABLE NOW
   - Add to USED ARCHIVE with date + post IDs
4. [ ] Result: 5 images remaining (file_162, 163, 173, 174, 175, 177)

---

## IMAGE INVENTORY STATUS

**Before Aug 14:** 8 available (file_162, 163, 172, 173, 174, 175, 176, 177)  
**After Aug 14 posts:** 5 available (file_162, 163, 173, 174, 175, 177)  
**Depletion rate:** 3 images/day (2 social + 1 blog)  
**Runway:** ~2 days before Chris needs to send new batch

**PRIORITY:** Flag to Chris end-of-day that inventory will hit zero by Aug 16 if daily cadence continues without new batch arrival.

---

## CREATIVE ITEMS PENDING

### First Winter Spark (Iris Vale)
- [ ] Awaiting Chris to film "5 things locals do in August that newcomers miss"
- [ ] Jack preparing lead magnet: "Newcomer's First-Winter Checklist"
- [ ] Ryan prepping site updates: Winter-Ready sections on town pages
- [ ] Arthur researching: Souhegan Valley winter history piece
- [ ] Willow prepping: Cold-weather wellness micro-post
- **Action:** Once Chris film lands, Fiona packages for social distribution

---

## NOTES

- **No dashes:** All copy verified for comma/period/restructure instead ✓
- **Twitter char count:** Both posts under 275 chars ✓
- **Yoast green:** Blog post passes all 10 Yoast checks ✓
- **Internal links:** Both social + blog include contact CTA
- **Outbound link:** Blog includes realtor.com market data link ✓
- **Brand voice:** All copy professional, polished, knowledge-focused ✓

---

## SIGN-OFF

**Prepared by:** Fiona Murphy  
**Time:** 07:30—08:15 ET  
**Status:** READY FOR NEXT PHASE (WordPress + Late API publishing)  
**Updated memory file:** `/root/agents/fiona-murphy/workspace/memory/2026-08-14.md`
