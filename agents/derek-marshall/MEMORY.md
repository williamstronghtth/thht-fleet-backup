# MEMORY.md - Long-Term Memory

*Curated learnings, not raw logs. Updated periodically from daily notes.*

---

## Who I Work With

**Chris Hoover** - My strategic lead. Direct, values efficiency, gives clear direction then lets me execute. Telegram: 8560812913

**Vladimir Vladimirov** - Company owner. Taking over the business. Telegram: 8773514384

## The Company

**Affordable Roofing & Construction**
- Owner: Vladimir Vladimirov (taking over from retiring owner)
- 20+ years in business
- Licenses: CCC 1327602 (Roofing) | CGC 1509441 (General Contractor)
- Phone: 386-392-8952
- Email: affordableroofing3@att.net (identity) / affordableroofing1@att.net (forms)
- Hours: Mon-Fri 8AM-5PM, Sat 9AM-2PM, Sun Closed
- Service area: Volusia County, Central Florida
- **Key differentiators:** Free estimates + **wind mitigation included with every roof** (saves homeowners on insurance premiums — huge selling point in FL hurricane season) + **5-year labor warranty**
- **CertainTeed credentials (CORRECTED by Vladimir 2026-07-23 21:52):** **ShingleMaster™** + dual **Master Craftsman** (Shingle Quality Specialist, Roofing Contractor — valid thru Apr 2028). THREE credentials. ⚠️ **NOT SELECT ShingleMaster.** Vladimir initially said SELECT, then corrected it same evening. Do NOT claim SELECT ShingleMaster or the **SureStart PLUS 5-Star warranty** (5-Star is SELECT-only). ShingleMaster DOES unlock SureStart PLUS extended coverage — but never name a specific star tier until Vladimir confirms with CertainTeed (1-800-233-8990). Strongest honest framing: "CertainTeed ShingleMaster credentialed + dual Master Craftsman certified."
- ⚠️ **HARDIE BOARD / SIDING IS NOT A FOCUS SERVICE** (Chris, 2026-08-31): "We do it but not our specialty." Do **not** write new Hardie/siding content, build city pages for it, spend SEO or link budget on it, or lead with it in GBP posts/ads/marketing. Roofing is the specialty; Hardie is a "yes, we can do that" mention only. Existing page 1352 + post 1353 stay as-is; their duplicate-content overlap is **closed as won't-fix — stop resurfacing it.**
- **Yelp:** TWO listings exist. Vladimir's = `/biz/affordable-roofing-and-construction-port-orange-2`; older unclaimed one = same slug without `-2` (3.0 stars, 2 old-owner-era negatives). Needs a merge. Yelp feeds Apple Maps reviews.

**Business Transition:** Vladimir getting 70% ownership, seller keeps 30% as license qualifier until Vladimir qualifies for his own license.

## Active Projects

### Website (affordableroofingconstruction.com) - LIVE ✅
- Hosted on Bluehost, WordPress with Blueprint theme
- Brand colors: white, black, navy blue (#1e4fa3)
- Logo: Has "20 Years" badge (Media ID: 97)
- Conversion-focused - CTAs for free estimates, contact forms
- 11+ local SEO blog posts (auto-publishing via cron)
- Contact form (Jetpack) - no email exposed on site
- **5-Year Labor Warranty** added to Homepage, Services, About pages
- **WordPress API**: username `ch`, app password `heec 7Pix lJC8 r85x lUih amuF`

### Marketing Materials - READY
- Facebook covers (3 options) - `/brand-assets/facebook-covers/`
- Yard signs finalized (white background, clean design) - `/brand-assets/yard-sign-mockup.html`
- DTF decals for shirts - `/brand-assets/decals/NinjaTransfers-Decals.zip`
- 10+ Facebook posts written
- Order yard signs at signsonthecheap.com (~$230 for 20 with stakes)

### Business Guides Created
- Tax deductions guide - `/documents/tax-deductions-guide.html`
- GBP optimization checklist - `/documents/google-business-optimization.html`

### Business Development - IN PROGRESS
- Partnership term sheet drafted (`/documents/term-sheet-draft.md`)
- Insurance agent outreach started
- Nextdoor business page setup underway (Vladimir handling)
- **Google Business Profile:** RECLAIMED ✅ — Vladimir now has full control, posting actively
- **Commercial job in progress:** Roof replacement with Titan shingles (130+ mph), photos being collected for "Our Process" page (Friday update planned)
- AT&T caller ID: Need to call 800-321-2000 to register business name

## ⚠️ SEO Consolidation — SETTLED (verified 2026-08-31)

**The "Phase 1/2 consolidation of ~55–65 duplicate posts is still outstanding" note was STALE and WRONG.**
It was carried forward in daily memory for 5+ weeks after the work was actually finished. Do not repeat it.

Verified live on 2026-08-31:
- 157 unique 301 redirects, **zero chains**, every source returns 301, every destination returns 200.
- 141 posts unpublished to draft; **140/141 have a redirect rule** (the 1 gap is an empty-slug auto-draft, not a real URL).
- Deleted the 24 redundant duplicate rules left behind by the July 23 concurrent-session collision.
- Published state: **107 posts, 40 pages.** Zero post-to-post duplicate content ≥30%.

**The real problem found instead:** the city service pages built in *August* were city-swapped templates —
wind-mitigation ×4 at 81–88% identical to each other and 70–73% to the hub; roof-repair ×3 at 78–89%.
That is Google's doorway-page pattern. Fixed 2026-08-31 (see daily note).

**Rule going forward: any new city page must be checked against its siblings before publishing.**
The generic explainer belongs on ONE hub page; city pages link to it and carry only local content
(neighborhoods, build eras, local failure modes, storm history, permitting authority).
Scripts: `fix-windmit-city-pages.py`, `fix-roofrepair-city-pages.py` (both have a dry-run + overlap check).

### Redirection plugin API gotcha
There is **no `DELETE /redirection/v1/redirect/{id}`** route (returns rest_no_route).
Bulk delete is `POST /redirection/v1/bulk/redirect/delete` with form-encoded `items[]=<id>` repeated.

---

## Technical Notes

- WordPress REST API works great for content updates
- Bluehost Blueprint is an FSE (Full Site Editing) block theme
- Domain DNS managed at Cloudflare, pointing to Bluehost

## Lessons Learned

1. **When WordPress shows 500 errors after domain change**: Settings → General URLs need to match the domain
2. **Phone numbers are everywhere**: When updating, check pages, posts, headers, buttons, footers
3. **Chris prefers action over questions**: Try to figure it out first, then ask
4. **Hearth over GreenSky**: Better for contractors just starting with customer financing
5. **Ford F-250 Super Duty (diesel)**: Recommended for debris hauling work trucks
6. **Lead priorities for roofers**: Google Business (70-80%) > Facebook (10-15%) > Instagram (1-5%)
7. **Section 179**: Trucks over 6,000 lbs GVWR can be fully deducted in year of purchase
8. **Women homeowners**: Over-communicate, uniforms, clean job sites, end-of-day walkthroughs build trust

---

*Last updated: 2026-03-05 - GBP reclaim in progress, commercial job underway, website warranty added, guides created*
