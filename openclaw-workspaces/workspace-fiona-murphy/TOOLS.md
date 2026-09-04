# TOOLS.md - Local Notes

## Late API (Social Media Posting)

- **API Key:** `<REDACTED:API_KEY>`
- **Base URL:** `https://getlate.dev/api/v1`

### Account IDs
- Instagram: `698f6a5ffd3d49fbfa3e29f7`
- Facebook: `698f6ab9fd3d49fbfa3e2a9f`
- LinkedIn: `698f6b23fd3d49fbfa3e2baf`
- Twitter: `698f6ad0fd3d49fbfa3e2afd`

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

---

## Google Drive

- **Image Folder:** https://drive.google.com/drive/folders/1VHSszIjD1AYYL-DK4I-Ak-TuAV-5UPzw
- Delete images after posting (storage management)
- Track used images in `memory/image-usage-log.md`

---

## Team Contacts

- **William** (daily news topics): `agent:main:main`
- **Ryan** (tech support): `agent:ryan-chen:main`
