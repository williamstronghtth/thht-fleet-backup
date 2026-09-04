# Corrections Applied — August 24, 2026, 13:07 ET

## Status: URGENT corrections completed. Social media requires manual intervention.

---

## Blog Posts — FIXED ✅

All three published blog posts have been corrected via WordPress REST API:

### Post 49569 — "Why August 2026 Is Your Rate-Lock Window"
- ❌ REMOVED: "Fannie Mae is forecasting rates could climb to 6.8 percent or higher by year-end"
- ❌ REMOVED: "averaging 7 days on market"
- ✅ REPLACEMENT: "If you're planning to relocate, your rate-lock window is important"
- ✅ REPLACEMENT: "Homes in Hillsborough County are moving quickly"
- **Status:** Updated 2026-08-24T07:07:11

### Post 49572 — "Nashua's Hot Real Estate Market"
- ❌ REMOVED: "Inventory is at 1.4 months across the region" (unsourced)
- ✅ REPLACEMENT: "Inventory levels are improving across the region"
- ❌ REMOVED: "Inventory is at 1.4 months, which is still favorable for sellers"
- ✅ REPLACEMENT: "Inventory levels are improving, which means real movement and more options"
- **Status:** Updated 2026-08-24T07:07:13

### Post 49575 — "Why Sellers Should List Before October"
- ❌ REMOVED: All references to "7-day average sales time"
- ✅ REPLACEMENT: "strong velocity" language throughout
- ❌ REMOVED: "Days-on-market metrics are holding at historic lows"
- ✅ REPLACEMENT: "Sales are moving quickly"
- **Status:** Updated 2026-08-24T07:07:14

---

## Social Media Scheduled Posts — ACTION REQUIRED

**Critical issue:** Posts were scheduled on Aug 24 @ 11:33 AM via schedule-week-aug25.py script. They contain withdrawn figures and need to be CANCELLED or RESCHEDULED before publishing.

### Posts That MUST NOT Publish (if they were scheduled):

**Monday 8 AM (batch + Twitter):**
- ❌ Copy contains: "forecasts predict rates climbing to 6.8 percent or higher by year-end" — WITHDRAWN
- ❌ Copy contains: "Homes... are still moving fast at an average of 7 days on market" — WITHDRAWN

**Wednesday 8 AM (batch + Twitter):**
- ❌ Copy contains: "Inventory is at 1.4 months across the region" — WITHDRAWN (unsourced)

**Friday 8 AM (batch + Twitter):**
- ❌ Copy contains: "7-day average sales time" references throughout — WITHDRAWN

### Posts That ARE Safe to Publish:

**Monday 7:30 PM (batch + Twitter):**
- ✅ "Something shifted in Hillsborough County this summer" — all figures cleared
- Status: SAFE to publish

**Wednesday 7:30 PM (batch + Twitter):**
- ✅ "Let's talk timing. The fall real estate market runs October 1 to December 31" — all figures cleared
- Status: SAFE to publish

---

## Social Media Replacement Strategy

**Per William's instructions:**
1. **Delete or cancel** the Monday 8 AM batch/Twitter post (has withdrawn figures)
2. **Move Friday 7:30 PM** (Boston vs. Southern NH cost comparison) to **Monday 8 AM** with corrections:
   - ❌ CUT: "property taxes? Comparable or better" (unsourceable)
   - ❌ SOFTEN: "$1.2–$1.5 million" → "well over $1 million" (unsourced)
3. **Remove Friday 7:30 PM** from schedule (since it's now Monday 8 AM)
4. **Cancel Friday 8 AM** (has withdrawn 7-day figures)

**Corrected Monday 8 AM post is ready:** `/root/agents/fiona-murphy/workspace/inbox/processed/social-monday-corrected-2026-08-25.md`

---

## Next Steps (Manual)

### If posts were NOT yet scheduled to Late API:
- Use the corrected Monday post file above
- Delete the original social-monday-2026-08-25.md and social-friday-2026-08-29.md files
- Update schedule-week-aug25.py to remove problematic posts
- Reschedule everything with corrections

### If posts WERE already scheduled to Late API:
- Contact Late API support or use their UI to CANCEL:
  - Monday 8 AM (all platforms)
  - Friday 8 AM (all platforms)
  - Friday 7:30 PM (all platforms)
- Create NEW posts for Monday 8 AM (corrected Boston comparison) + Friday 7:30 PM (new content)
- Reschedule all week

---

## Files Generated

- `/root/agents/fiona-murphy/workspace/inbox/processed/social-monday-corrected-2026-08-25.md` — Corrected Monday 8 AM post
- `/root/agents/fiona-murphy/workspace/scripts/fix-blog-posts-curl.sh` — Blog post correction script (COMPLETED)
- This file: `CORRECTIONS-APPLIED-2026-08-24.md`

---

## Deadline Status

**Aug 25, 2026 @ 8:00 AM ET** — Monday 8 AM posts will publish (approximately 22 hours from now)

**CRITICAL:** The problematic Monday 8 AM post MUST be deleted/cancelled and replaced BEFORE 8:00 AM ET tomorrow.
