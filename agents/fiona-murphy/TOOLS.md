# TOOLS.md - Local Notes

## Late API (Social Media Posting)

- **API Key:** Stored in `/root/agents/.env` as `LATE_API_KEY` (load with `os.environ["LATE_API_KEY"]`)
- **Base URL:** `https://getlate.dev/api/v1`

### Account IDs
- Instagram: `698f6a5ffd3d49fbfa3e29f7` — ✓ Active (requires media for posts)
- Facebook: `698f6ab9fd3d49fbfa3e2a9f` — ✓ Active
- LinkedIn: `698f6b23fd3d49fbfa3e2baf` — ✓ Active
- Twitter: `698f6ad0fd3d49fbfa3e2afd` — ✓ Active (reconnected May 11, 2026)
- Google Business: `6a1f19432b2567671aa1ea24` — ✓ Active (connected June 2, 2026). ⚠️ Platform key is **`googlebusiness`** (one word, no hyphen). Using `google-business` returns a 400 `invalid_field_value` and kills the ENTIRE batch, not just that platform.
- Pinterest: `6a622137542d8bc5a6c82678` — ✓ Connected July 23, 2026 (TheHooverHomeTeam). **Requires `platformSpecificData.boardId`** or the post fails with "Pinterest requires a boardId." List boards: `GET /accounts/6a622137542d8bc5a6c82678/pinterest-boards`. Board "New England Home Inspiration" created July 23, 2026, boardId `1138355312003501154`. Also supports `title` (max 100 chars) and `link` (destination URL). Post as its own standalone request.
- Bluesky: `6a62203c542d8bc5a6c8168d` — ✓ Active (connected July 23, 2026, handle thehooverhometeam.bsky.social). **300 character limit.** Post as its own standalone request like Twitter.

### Posting Workflow
1. Get presign URL: `POST /media/presign` with filename + contentType
2. Upload image: `PUT` binary to returned `uploadUrl`
3. Create post: `POST /posts` with `publicUrl` in mediaItems

### ⚠️ CRITICAL: Use `content` not `text`! Use `platforms` array!
```json
{
  "platforms": [
    {"platform": "instagram", "accountId": "698f6a5ffd3d49fbfa3e29f7"},
    {"platform": "facebook", "accountId": "698f6ab9fd3d49fbfa3e2a9f"},
    {"platform": "linkedin", "accountId": "698f6b23fd3d49fbfa3e2baf"}
  ],
  "content": "Your post text here",
  "mediaItems": [{"type": "image", "url": "..."}],
  "publishNow": true
}
```

### Platform Notes
- **Instagram Stories:** Use `platformSpecificData: {contentType: "story"}` for portrait images
- **Instagram Feed:** Aspect ratio must be 0.75-1.91 (square or landscape)
- **Twitter:** 280 character limit — needs shorter versions
- **Google Business:** Posts expire after 7 days (Google's policy). Post type: STANDARD. Great for market updates, new listings, and Just Sold announcements. Can be included in the main batch alongside FB/IG/LI.

### ⚠️ TWITTER POSTING RULE — MANDATORY

**ALWAYS post Twitter as a separate, standalone request.** Never include Twitter in a multi-platform batch.

**Why:** The Late API `platformSpecificData.twitter.content` override does NOT work. Twitter receives the full `content` field and fails silently or errors if it exceeds 280 characters.

**Required process:**
1. Write the full post for FB/IG/LinkedIn (no length limit)
2. Write a separate, shortened version for Twitter — **hard cap: 275 characters** (leave 5 chars buffer)
3. Count characters before posting. If over 275, trim.
4. Send two separate API calls:
   - **Batch call:** FB + IG + LinkedIn with full `content`
   - **Twitter-only call:** Twitter alone with short `content`

**Twitter-only payload example:**
```json
{
  "platforms": [
    {"platform": "twitter", "accountId": "698f6ad0fd3d49fbfa3e2afd"}
  ],
  "content": "Short version under 275 chars here.",
  "mediaItems": [{"type": "image", "url": "..."}],
  "publishNow": true
}
```

**Never skip the character count check. If uncertain, count manually.**

---

## WordPress Blog

- **Site:** https://thehooverhometeam.com
- **Username:** chris@cbcoastrealty.com
- **App Password:** Au1M DJEn iU9X 7YSh m7am nPSA
- **Category:** 5 (Real Estate)

### Post Endpoint
```bash
curl -X POST "https://thehooverhometeam.com/wp-json/wp/v2/posts" \
  -u "chris@cbcoastrealty.com:Au1M DJEn iU9X 7YSh m7am nPSA" \
  -H "Content-Type: application/json" \
  -d '{"title": "...", "content": "...", "status": "publish", "categories": [5], "featured_media": <media_id>}'
```

### Upload Image (for featured image)
```bash
# 1. Upload image to media library
curl -X POST "https://thehooverhometeam.com/wp-json/wp/v2/media" \
  -u "chris@cbcoastrealty.com:Au1M DJEn iU9X 7YSh m7am nPSA" \
  -H "Content-Disposition: attachment; filename=image.png" \
  -H "Content-Type: image/png" \
  --data-binary @"/path/to/image.png"

# 2. Use returned ID as featured_media in post
```

### ⚠️ MANDATORY: Verify Yoast with the checker script

```bash
python3 /root/agents/fiona-murphy/workspace/scripts/yoast-check.py <POST_ID>
```
Runs all 15 Yoast checks locally (keyphrase length/title/slug/first paragraph/H2/density,
word count, meta description, internal + outbound links, featured image, block markup, alt text).
Exits 0 only when everything passes. Run on every blog post before calling it done.

### ⚠️ MANDATORY: Yoast Premium must be GREEN, not orange
**Read `memory/yoast-green-checklist.md` BEFORE writing every blog post.** Chris rule as of
July 23, 2026: orange "OK" is not acceptable. The 10 point checklist there covers keyphrase
length, slug, subheadings, density, outbound link, and image alt. Two gotchas: XML-RPC
`custom_fields` duplicates meta instead of overwriting (pass the existing meta `id` to update),
and the Yoast score dot only recalculates when the post is saved in the WP editor.

### Set Yoast SEO fields after every post

After publishing a post, ALWAYS set these Yoast SEO fields via XML-RPC.
The REST API does NOT expose Yoast meta — use XML-RPC instead.

**Required fields for green score:**
- `_yoast_wpseo_focuskw` — focus keyphrase (e.g. "southern NH real estate market")
- `_yoast_wpseo_metadesc` — meta description, **120-156 characters**, must include the keyphrase

**Content requirements (write into the post itself):**
- Keyphrase appears in the first paragraph
- Post is 300+ words
- Include at least one internal link (to another blog post or site page)
- Featured image alt text should include the keyphrase (set when uploading media)

**XML-RPC method to set Yoast fields (replace POST_ID, FOCUSKW, METADESC):**
```bash
curl -s -X POST "https://thehooverhometeam.com/xmlrpc.php" \
  -H "Content-Type: text/xml" \
  -d '<?xml version="1.0"?>
<methodCall>
  <methodName>wp.editPost</methodName>
  <params>
    <param><value><int>1</int></value></param>
    <param><value><string>chris@cbcoastrealty.com</string></value></param>
    <param><value><string>Au1M DJEn iU9X 7YSh m7am nPSA</string></value></param>
    <param><value><int>POST_ID</int></value></param>
    <param><value>
      <struct>
        <member>
          <name>custom_fields</name>
          <value>
            <array>
              <data>
                <value>
                  <struct>
                    <member><name>key</name><value><string>_yoast_wpseo_focuskw</string></value></member>
                    <member><name>value</name><value><string>FOCUSKW</string></value></member>
                  </struct>
                </value>
                <value>
                  <struct>
                    <member><name>key</name><value><string>_yoast_wpseo_metadesc</string></value></member>
                    <member><name>value</name><value><string>METADESC (120-156 chars)</string></value></member>
                  </struct>
                </value>
              </data>
            </array>
          </value>
        </member>
      </struct>
    </value></param>
  </params>
</methodCall>'
```
Returns `<boolean>1</boolean>` on success.

---

## Google Drive

- **Image Folder:** https://drive.google.com/drive/folders/1VHSszIjD1AYYL-DK4I-Ak-TuAV-5UPzw
- Delete images after posting (storage management)
- **Check `memory/image-inventory.md` FIRST** for current AVAILABLE NOW / RESERVED / DO NOT USE
  status — this is the live source of truth (added July 23, 2026 after a back-to-back duplicate
  image incident). `memory/image-usage-log.md` is historical archive only, too long to scan for
  day-of selection.
- **Hard rule: never use the same image twice in the same calendar day**, even if inventory is
  at zero — post text-only or flag to Chris instead of silently reusing.

---

## GA4 Analytics

### Credential 1: Service Account (headless / server use)
- **File:** `/root/agents/fiona-murphy/workspace/credentials/ga4-credentials.json`
- **Service account:** `fiona-analytics-reader@hoover-analytics-api.iam.gserviceaccount.com`
- **Project:** `hoover-analytics-api`
- **Auth type:** Service account (JSON key)
- **Status:** ⚠️ Needs manual GA4 property access grant from Chris (see notes below)

```python
from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
creds = service_account.Credentials.from_service_account_file(
    '/root/agents/fiona-murphy/workspace/credentials/ga4-credentials.json',
    scopes=SCOPES
)
```

### Credential 2: OAuth2 Client Secret (user-authorized flow)
- **File:** `/root/agents/fiona-murphy/workspace/credentials/client_secret.json`
- **Client ID:** `116762181750-aifoer3p3vj4v74efn7vceaa189upd9a.apps.googleusercontent.com`
- **Project:** `hoover-analytics-api`
- **App type:** Installed (desktop/localhost redirect)
- **Use case:** User-authorized OAuth2 flow — allows access as a Google account user rather than a service account

```python
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
flow = InstalledAppFlow.from_client_secrets_file(
    '/root/agents/fiona-murphy/workspace/credentials/client_secret.json',
    scopes=SCOPES
)
# flow.run_local_server() or flow.run_console() to get user credentials
# Save token to credentials/ga4-oauth-token.json for reuse
```

### Notes
- Service account needs Chris to manually add it as a Viewer in GA4 Admin UI:
  Analytics → Admin → Property Access Management → + Add users → paste service account email
- OAuth2 client secret is the alternative path if service account access is blocked
- Both credentials are for project `hoover-analytics-api`
- Never commit either credentials file

---

## Content Briefs (Inbox)

William drops a daily content brief to your inbox at ~11:00 UTC (7 AM ET).
Check **both** directories for briefs:
- `inbox/` — new, unprocessed briefs
- `inbox/processed/` — previously handled briefs (useful for follow-ups or re-posts)

Your daily cron runs at 11:30 UTC to give the handoff time to land.

---

## ⚠️ Email — Do NOT use MCP or Gmail Auth

Never ask Chris (or anyone) to connect MCP or authenticate Gmail.
Use the local email script instead:
```bash
python3 /root/agents/bin/send-email.py --to "recipient@example.com" --subject "Subject" --body "Body text"
```

---

## SEO Resources

- **Whitespark** — https://whitespark.ca — Local SEO tools: citation building, local rank tracker, Google Business Profile audit, reputation builder. Useful for improving local search visibility for the Hoover Home Team.
- **Meyer Lucas Real Estate** — https://meyerlucas.com — Real estate reference/competitor site.
- **SEMrush** — https://semrush.com — SEO and competitive research platform: keyword research, site audits, backlink analysis, rank tracking, and content marketing tools.

---

## Team Contacts

- **William** (daily news topics): `agent:main:main`
- **Ryan** (tech support): `agent:ryan-chen:main`
