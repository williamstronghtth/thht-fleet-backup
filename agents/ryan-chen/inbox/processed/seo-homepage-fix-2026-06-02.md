# SEO Fix: Homepage Market Area — June 2, 2026

**Priority:** High  
**From:** William Strong  
**Issue:** Google showing wrong market area in search snippet for homepage

---

## What Google Is Showing

```
The Hoover Home Team: Homepage
thehooverhometeam.com
"If you're looking to buy, or sell real estate in Central Massachusetts or Florida 
let's get in touch. Chris Hoover writes..."
```

---

## Root Cause Analysis

There are **three layers** to this problem:

### Layer 1 — Meta Description ✅ Already Fixed
The Yoast meta description was updated on May 11, 2026:
> "Looking to buy or sell real estate in Southern New Hampshire? The Hoover Home Team serves Mont Vernon, Amherst, Milford, and surrounding towns. Let's talk."

This is correct. No action needed here.

### Layer 2 — Homepage BODY Content ❌ Still Wrong
Google often generates dynamic snippets from page body text instead of the meta description, especially when body content contradicts it. The homepage body currently contains:

**H2 tagline:**
> "Exceeding Expectations from New England to the Sunshine State, One Home at a Time"

**Mission statement:**
> "Our mission is simple: to work harder than anyone else to deliver outstanding results for our clients in **New Hampshire, Massachusetts, and Florida**, while building trust every step of the way."

**Supporting paragraph:**
> "We understand that buying or selling a home, whether it's **in New England or the Sunshine State** is a significant milestone."

**Phone number displayed in header:**
> 386-871-6017 ← this is a Volusia County FL area code

All of these need to be updated in WordPress to reflect Southern NH.

### Layer 3 — 500+ FL Blog Posts ❌ Major Signal Dilution
The blog has 500+ posts about Port Orange, Daytona Beach, Ormond Beach, and Volusia County. Google uses topical authority across the whole domain to determine market focus. This is why it keeps reverting to FL associations. This requires a content strategy fix (see below).

---

## Immediate Fixes (WordPress Admin)

### 1. Update Homepage H2 Tagline
**Current:** "Exceeding Expectations from New England to the Sunshine State, One Home at a Time"  
**Suggested:** "Your Southern New Hampshire Real Estate Experts — One Home at a Time"

### 2. Update Mission Statement
**Current:** "...deliver outstanding results for our clients in New Hampshire, Massachusetts, and Florida..."  
**Suggested:** "...deliver outstanding results for our clients across Southern New Hampshire — from Mont Vernon and Amherst to Milford, Nashua, and Salem..."

### 3. Update Supporting Paragraph
**Current:** "...whether it's in New England or the Sunshine State is a significant milestone..."  
**Suggested:** "...whether it's your first home or your forever home in Southern New Hampshire, it's a significant milestone..."

### 4. Update Page Title Tag (Yoast)
**Current:** "Homepage - The Hoover Home Team"  
**Suggested:** "Southern NH Real Estate Agent | The Hoover Home Team"

### 5. Consider Phone Number Header
The 386-871-6017 Florida number is still displayed. Once Chris has a NH number as primary, swap it in the header.

---

## After Edits: Request Re-Index

Once the homepage body is updated, go to **Google Search Console** → URL Inspection → `https://thehooverhometeam.com/` → Request Indexing. Google will re-crawl within 1-3 days.

---

## Longer-Term: FL Blog Posts

The 500+ FL posts are the biggest SEO headache. Options (in order of effort):

1. **No-index FL posts** (fastest): Add `noindex` to all FL/Volusia posts via Yoast bulk editor or a plugin. Google stops counting them against NH relevance, but they stay live.
2. **301 Redirect old posts**: High effort, not recommended for 500+ posts.
3. **Content velocity**: Publish NH content aggressively (Fiona's town digests, market updates). Over time this shifts topical authority. This is already in motion.

**Recommendation:** Do option 1 (bulk no-index FL posts) + option 3 (NH content velocity). This is the fastest path to Google seeing the site as an NH real estate authority.

---

## Summary of Actions

| Action | Where | Effort | Priority |
|--------|--------|--------|----------|
| Update H2 tagline | WP Homepage editor | 5 min | 🔴 High |
| Update mission statement | WP Homepage editor | 5 min | 🔴 High |
| Update supporting paragraph | WP Homepage editor | 5 min | 🔴 High |
| Update Yoast page title | Yoast SEO panel | 2 min | 🔴 High |
| Request re-index | Google Search Console | 2 min | 🔴 High (after edits) |
| Bulk no-index FL posts | Yoast bulk editor | 30 min | 🟡 Medium |
| NH content velocity | Ongoing (Fiona) | Ongoing | 🟡 Medium |

Let me know if you need help with the no-index bulk edit or any of the copy.
