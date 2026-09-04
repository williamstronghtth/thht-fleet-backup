# MEMORY.md - Fiona's Long-Term Memory

## Identity
- **Name:** Fiona Murphy
- **Role:** Marketing Specialist, The Hoover Home Team
- **Market:** Port Orange and Volusia County, FL

## Key Workflows

### Social Media Posting
- **Method:** Single batch to all 4 platforms (FB, IG, Twitter, LinkedIn)
- **Char limit:** Under 280 for Twitter
- **Schedule:** 2x daily - 8 AM ET + 7:30 PM ET
- **API:** Late API with `content` field (NOT `text`!)
- **Protocol:** Pre-check history, verify no duplicates, post, verify

### Blog Posts
- **WordPress:** thehooverhometeam.com
- **Category:** 5 (Real Estate)
- **Credentials:** In TOOLS.md

### Image Sources
- **Google Drive folder:** Photos for Fiona
- **Current batch:** Feb 25, 2026 images (15 total)
- **Listing photos:** Use Trulia (Zillow/Redfin/Realtor block scraping)

## Integrations

### Late API (Social Media)
- Configured in TOOLS.md
- Account IDs for all 4 platforms
- Must use `content` not `text` field

### Canva API (Connected Mar 2, 2026)
- OAuth tokens in ~/.clawdbot/canva-tokens.json
- Can list designs, export, upload assets
- Integration: "Fiona's Access"

### WordPress
- Direct REST API access
- Credentials in TOOLS.md

## Team
- **Chris Hoover** - Founder, my creator
- **William Strong** - Manager, sends daily content briefs
- **Ryan Chen** - Tech support

## Lessons Learned
1. **Duplicates:** Platform isolation caused 3x duplicates. Use single batch instead.
2. **Twitter limit:** Keep posts under 280 chars or Twitter fails.
3. **Late API field:** Use `content` not `text` - learned the hard way.
4. **Listing photos:** Trulia works when Zillow/Redfin block.
5. **Canva OAuth:** Scope changes require re-authorization. Tokens expire ~4 hours.
6. **Canva asset upload:** Header format is `{"name_base64":"<base64-filename>"}` (NOT double-encoded).
7. **Video autofill:** Video backgrounds need video asset IDs (start with V), images start with M.
8. **Content variety:** Rotate topics — rates, market data, team wins, thought leadership, local angles.
9. **NO DASHES:** Chris prefers no dashes/hyphens in all content. Use commas or restructure.
10. **Late API drafts:** If platforms array is empty, retry the request with publishNow: true.
11. **Google Drive sync:** Use gdown to download folders from public Drive links.
12. **Late API Twitter override:** platformSpecificData.twitter.content override does NOT work reliably — Twitter receives the full `content` field and fails on length. Always post Twitter as a separate single-platform request with its own short `content`.

## Content Rhythm (Established Mar 2026)
- **Daily:** 1 post morning (8 AM ET) + blog
- **Weekends:** Lighter topics, market snapshots
- **Avoid:** Repeating same topic within 3-4 days
- **Track:** Image usage in memory/image-usage-log.md
