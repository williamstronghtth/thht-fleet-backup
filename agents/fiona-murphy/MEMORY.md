# MEMORY.md - Fiona's Long-Term Memory

## Identity
- **Name:** Fiona Murphy
- **Role:** Marketing Specialist, The Hoover Home Team
- **Market:** Southern NH (primary). Chris relocated to Mont Vernon NH on July 1, 2026. Volusia County / FL real estate content is RETIRED — FL geography applies only to Affordable Roofing (Derek's lane).
- **Approved towns to write about:** Mont Vernon, Amherst, Brookline, Hollis, Nashua, Lyndeborough, Wilton, Milford, Mason, Temple, Peterborough

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
- **⚠️ AS OF JULY 23, 2026: `memory/image-inventory.md` is the single source of truth for image selection** — AVAILABLE NOW / RESERVED / DO NOT USE, kept lean and current. Check it FIRST, every time, before picking an image. `memory/image-usage-log.md` is historical archive only (1000+ lines, too long to scan day-of) — do not rely on it to decide availability.
- **Current status (July 23, 2026): AVAILABLE NOW = 0.** All inventory through file_120/file_123 and all numbered 1-86.png used. Awaiting new batch from Chris — urgent.
- **Blog featured images:** Google Drive ONLY — images Chris sends directly. NO stock images of any kind (Unsplash approval revoked July 10, 2026). Never pull from Trulia, Coldwell Banker, Zillow, Redfin, or any external source. If image inventory is exhausted, ask Chris for more before posting.
- **Listing photos (reference only):** Trulia works when Zillow/Redfin block — for research only, NOT for blog images.
- **NO REUSE RULE (Chris-approved, May 26 2026):** Once an image has been used in ANY post (blog or social), it CANNOT be used again. Check `memory/image-inventory.md` before selecting an image.
- **NEW HARD RULE (Chris-flagged, July 23 2026): Never use the same image for both the 8 AM and 7:30 PM post on the same day**, even as a last resort when inventory is at zero. Root cause of the July 23 incident: file_120.jpg was the only image left after file_118/119 were used the day before, and it got reused for the evening slot instead of going text-only or flagging to Chris. That reuse pattern is now explicitly banned — see image-inventory.md rule #3.

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
13. **Late API presign:** Use lowercase `filename` not `fileName` in presign request.
13b. **Google Business images must be JPG.** PNG files cause a "media file is invalid" error on GMB. Always convert PNGs to JPG before posting to Google Business (use Pillow: `Image.open('x.png').convert('RGB').save('x.jpg', quality=90)`).
14. **Late API response:** Post ID is in `response.json().get("post", {}).get("_id")` not `response.get("id")`.
15. **Late API scheduling:** Can include `scheduledFor` (ISO timestamp) and `timezone` directly in POST /posts payload.
16. **WordPress WAF:** Server Mod_Security blocks `application/json` POST requests (406 error). Python `requests` `data=` dict also triggers 406. Use `curl --data-urlencode` for post creation. Image uploads now WORKING as of May 6, 2026 (Chris fixed server permissions). Upload via `curl -X POST /wp-json/wp/v2/media` with binary data directly.
17. **Blog posts:** MANDATORY daily — publish every single morning alongside social posts. No exceptions. Gaps happened Apr 12-27 and Apr 29-May 1 because the cron prompt didn't require it. The cron now explicitly requires it. Blog uses same market data as social posts. Do not skip.
18. **Yoast SEO green score:** REST API does NOT expose Yoast protected meta fields. Use XML-RPC to set `_yoast_wpseo_focuskw` (focus keyphrase) and `_yoast_wpseo_metadesc` (120-156 chars, includes keyphrase) after every post. Full XML-RPC snippet in TOOLS.md. Also: keyphrase must appear in first paragraph, post must be 300+ words, include at least one internal link.
19. **Blog featured image is MANDATORY at publish time:** Upload an image to WordPress media and set it as `featured_media` on the post BEFORE publishing. Do NOT publish first and add the image later. Pick from images/ folder or Google Drive. Every blog post must have a featured image — no exceptions.
20. **Just Sold post format (Chris-approved):** Title: "Just Sold: [Address], [Town] [State] Closes at $[Price]". Opening paragraph names the address, sale price, sale date, and a compelling "easy to see why" hook. Then use H2 sections: "Property Overview" (beds/baths/sqft/lot/built year/standout features), "The Listing Team" (list agent + buyer's agent, brokerage, days on market, final price), "What This Sale Tells Us About the Southern NH Market" (market insight + CTA with internal link to /contact). Close with italicized MLS number. No dashes anywhere. Conversational but polished. Blog only, no social media for these posts.
21. **Just Sold featured image MUST be the front exterior photo of the property.** Source from Google Drive ONLY (Chris sends photos to Drive). If no exterior photo is available in Drive, ask Chris before pulling from Trulia or CB. Alt text: "[Address] [Town] [State] just sold front exterior". Never use a stock interior shot for Just Sold posts.
23. **Blog images = Google Drive only (Chris-approved rule, May 13 2026, reinforced July 10 2026).** ALL blog post featured images must come from the Google Drive photos folder (images Chris sends). NO stock images of any kind — Unsplash approval is revoked as of July 10, 2026. Do not pull from Trulia, Coldwell Banker, Zillow, Redfin, or any external/stock source. If inventory is empty, ask Chris before posting.
24. **Image filename rule (Chris-approved, May 22 2026, updated May 31 2026, updated July 2 2026).** Images with a property address in the filename (e.g., "6-odell-drive-amherst-nh.jpg", "14-boylston-terrace-amherst-nh-exterior.jpg") are RESERVED for Just Sold posts of that specific property ONLY. For regular/general blog posts and social posts, use numbered PNG images from Google Drive (e.g., "73.png", "74.png") OR file_XX.jpg images that Chris explicitly sends. Early file_XX.jpg images (file_35 through ~file_53) belonged to Audrey's project — do NOT use. HOWEVER, file_85.jpg, file_86.jpg, file_87.jpg, file_88.jpg and any new file_XX.jpg images Chris sends going forward ARE approved for Hoover Home Team use (Chris confirmed July 2, 2026). Rule of thumb: if Chris sent the file directly to your inbox, it's approved for HHT.
22. **Just Sold Yoast SEO keyphrase = street number + street name ONLY.** Example: "10 Hobart Lane" (not "Hollis NH luxury home", not the full address with town). The meta description (120-156 chars) must include this keyphrase. The keyphrase must also appear in the first paragraph of the post.
25. **Blog and social featured images must look like a property (Chris-approved, July 21 2026, reinforced July 21 2026).** Only use images Chris sends directly that clearly look like a property: exterior shots, interior rooms, kitchens, living spaces, curb appeal photos, etc. NO charts, graphs, infographics, or data visualizations. NO lifestyle shots that don't show an actual property. NO stock images of any kind. If the image doesn't clearly look like a home or property, do not use it. When in doubt, ask Chris before posting.
26. **HARD RULE (Chris-reinforced July 23 2026): Address-tagged/Just-Sold photos NEVER appear in any blog post that is not that property's Just Sold post.** This is the same rule as #24 but Chris flagged it again, so treat it as zero-tolerance. Before setting any featured image, check the filename — if it names a street address (e.g. "6-odell-drive-amherst-nh.jpg", "150-greenville-road-mason-nh-exterior.png"), it may ONLY be used on the "Just Sold: [that address]..." post for that exact property. Never on market updates, buyer/seller education posts, neighborhood spotlights, or any general content. Audit on July 23 2026 found a legacy violation: posts 49085/49086 ("Why Now is the Buyer's Moment in Southern NH Real Estate," published May 16 2026, before this rule existed) used "6-odell-drive-amherst-nh-1.jpg" — reserved for the 6 Odell Drive Just Sold post. Flagged to Chris; he initially said he didn't see it used, but re-verified via WordPress REST API (featured_media field) AND the live page HTML source on July 23 2026 — the image is confirmed still set as featured_media 49084 and renders as the header image on both live URLs. Told Chris this is confirmed, not a false alarm. Still unfixed: image inventory was exhausted at the time (no clean unused replacement without violating no-reuse rule). Follow up when new images arrive — swap featured image on 49085/49086 to a proper general-use image.
27. **NEW PROCESS (Chris, July 23 2026, 8:20 AM ET): images are now single-use, then deleted for good — not archived.** Chris will label each photo he sends as "For Blog Posts" (general inventory) or "For Just Sold Posts" (reserved to that one property). Once an image is used anywhere (blog or social), delete it from Google Drive immediately after use — don't just log it as used and leave the file sitting around. This replaces the older "mark used in inventory, keep the file" habit and is meant to make accidental reuse physically impossible, not just rule-forbidden. See `memory/image-inventory.md` rule #2.

## YouTube Channel — Southern NH (New as of May 2026)
- **Role:** Packaging and distribution lead for Chris's Southern NH YouTube channel
- **Playbook:** See YOUTUBE.md for full workflow, title formulas, description template, repurposing plan
- **Channel name:** TBD — "The Granite Real" or "Live Southern NH" (Chris decides)
- **Launch:** Around Chris's July 1, 2026 move to Mont Vernon, NH
- **Four pillars:** Weekly News Roundup, Town Deep-Dives, Market Insights, Relocation/Problem-Solving
- **Script loop:** William gives topic + pillar → I return 3 title options + hook angle + SEO target → William drafts → I flag pull quotes + confirm title + draft description/tags
- **Repurposing:** Each video spawns Reels/Shorts, TikTok clip, X clip, LinkedIn post, blog reinforcement

## Content Rhythm (Established Mar 2026)
- **Daily:** 2 posts (8 AM ET + 7:30 PM ET) + 1 blog post (MANDATORY)
- **Weekends:** Lighter topics, market snapshots
- **Avoid:** Repeating same topic within 3-4 days
- **Track:** Image usage in memory/image-inventory.md (single source of truth as of July 23, 2026)
- **Current Status (Aug 21, 2026):** Image inventory CRITICAL. Posted Aug 21 content (2 social + 1 blog). Used 3 images today (file_176, 183, 189), leaving 4 available (file_188, 190, 191, 192). At 3 images/day burn rate, inventory depleted by Aug 22-23. URGENT: Message Chris for new batch immediately. William's brief provides angles through Aug 28.
28. **Yoast Premium must be GREEN on every blog post (Chris rule, July 23 2026).** Orange "OK" is not acceptable. Read `memory/yoast-green-checklist.md` BEFORE writing each post and apply all 10 checks at publish time. Core cause of orange: keyphrase too long and never written verbatim in title/slug/H2s/body. Keep keyphrases 2 to 4 words. Also need one outbound authoritative link plus the internal /contact/ link, and keyphrase in featured image alt text. Two technical gotchas: XML-RPC custom_fields ADDS duplicate meta rather than overwriting (pass existing meta id to update, pass {id} alone to delete), and `_yoast_wpseo_linkdex` (the score dot) only recalculates when the post is saved in the WP editor, so an API-only fix needs Chris to open and hit Update once.
