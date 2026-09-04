# Fiona Posting Protocol

## Pre-Post Verification (MANDATORY)

Before posting ANY content, follow this checklist:

### Step 1: Check Recent Posts
```bash
curl -s -H "Authorization: Bearer $LATE_API_KEY" \
  "https://getlate.dev/api/v1/posts?limit=10" | jq '.posts[] | {createdAt, content: .content[0:50]}'
```

### Step 2: Verify No Duplicates
- Check if similar content was posted in the last 2 hours
- Compare key phrases (e.g., "mortgage rates", "3-year low")
- If match found → **STOP, do not post**

### Step 3: Single Post Per Topic Per Day
- Only ONE rates post per day
- Only ONE listing feature per day
- Only ONE market update per day

### Step 4: Post, Then Verify
After posting:
1. Wait 30 seconds
2. Pull history again to confirm it went through
3. Log the post ID

## Session Interruption Recovery

If your session gets interrupted:
1. **FIRST** check Late API history for recent posts
2. **NEVER** retry without checking what's already out there
3. When in doubt, wait and verify

## Red Flags (DO NOT POST)
- Content matches something from last 2 hours
- Same image URL already used today
- Session was recently interrupted
- Unsure if previous attempt succeeded

## Daily Limits
- Max 4 posts per day across all platforms
- Space posts at least 2 hours apart
- No more than 1 rate-related post per day

---

*Last updated: 2026-02-23 after duplicate incident*
