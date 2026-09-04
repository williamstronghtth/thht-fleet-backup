# Social Media Posting Workflow

**Last Updated:** 2026-02-22
**Status:** ACTIVE

## ⚠️ CRITICAL FIX (2026-02-22)
**Late API uses `content` NOT `text`!**
- Old (WRONG): `"text": "Your post content"`
- New (CORRECT): `"content": "Your post content"`
- This was causing posts to show images only with no text on Twitter/X

## 🚨 MANDATORY PROTOCOL (2026-02-23)
**After duplicate incident — MUST follow before ANY post:**

1. **Check history first:** `GET /posts?limit=10`
2. **2-hour lookback:** No similar content in that window
3. **Session interrupted?** ALWAYS check history before retrying
4. **One topic per post:** Don't repeat same angle same day
5. **Post then verify:** Confirm it landed

**Full protocol:** `/root/.openclaw/workspace/docs/fiona-posting-protocol.md`

## 📅 POSTING SCHEDULE (2026-02-26)
**2x daily starting Feb 27:**

| Post | Time (ET) | Time (UTC) | Content Type |
|------|-----------|------------|--------------|
| Morning | 8:00 AM | 13:00 | Market news, data, educational |
| Evening | 7:30 PM | 00:30 (+1 day) | Lifestyle, softer CTA |

**Method:** Single batch to all 4 platforms (FB, IG, Twitter, LinkedIn)
**Char limit:** Under 280 for Twitter compatibility

---

## The Problem (Solved)

When posting to all 4 platforms at once and Instagram fails, retry attempts were creating duplicate posts on FB/LinkedIn/Twitter.

## New Workflow: Platform Isolation

### Post Order (3 Separate API Calls)

**Batch 1: Facebook + LinkedIn**
- Same long-form content
- These rarely fail together
- If one fails, the other succeeds (acceptable)

**Batch 2: Twitter (Separate)**
- Short 280-character version
- Always isolated (different content anyway)

**Batch 3: Instagram (Isolated)**
- Its own dedicated post
- If it fails, no impact on other platforms
- Can retry with modified content without affecting FB/LI/TW

### Content Hash Safeguard (TODO)

Before creating any Late post:
1. Generate content hash locally (first 60 chars + image URL)
2. Check recent posts for matching hash
3. If exists with partial/published status → SKIP, log it
4. If not found → proceed with post

Implementation: Add to posting script when created.

---

## Quick Reference

### Late API Endpoints
- Presign: `POST /media/presign` (filename, contentType)
- Upload: `PUT {uploadUrl}` with binary
- Post: `POST /posts` with accountIds, text, mediaItems, crosspostingEnabled: false

### Account IDs
- Instagram: `698f6a5ffd3d49fbfa3e29f7`
- Facebook: `698f6ab9fd3d49fbfa3e2a9f`
- LinkedIn: `698f6b23fd3d49fbfa3e2baf`
- Twitter: `698f6ad0fd3d49fbfa3e2afd`

### Critical Settings
- **Always include:** `crosspostingEnabled: false`
- **Twitter:** 280 char limit
- **Instagram:** Square images (1:1) or landscape (up to 1.91:1)

---

## Posting Checklist

- [ ] Upload image to Late (get publicUrl)
- [ ] Post to FB + LI (long version)
- [ ] Post to Twitter (short version, ≤280 chars)
- [ ] Post to Instagram (isolated, can use different image if needed)
- [ ] Update image-usage-log.md
- [ ] Log to daily memory file
