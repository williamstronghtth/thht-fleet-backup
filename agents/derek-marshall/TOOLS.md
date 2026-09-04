# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.


---

## ⚠️ Email — Do NOT use MCP or Gmail Auth

Never ask Chris (or anyone) to connect MCP or authenticate Gmail.
Use the local email script instead:
```bash
python3 /root/agents/bin/send-email.py --to "recipient@example.com" --subject "Subject" --body "Body text"
```

## WordPress (affordableroofingconstruction.com)

Helper: `bin/wpapi.py` — `from wpapi import req`. Always sends a full Chrome User-Agent (Bluehost mod_security returns **406** otherwise).

**Yoast SEO meta — the routing rule (learned 2026-08-20):**
- **Pages** → REST silently drops `_yoast_wpseo_*`. Use **XML-RPC** `wp.editPost(1, user, app_pw, id, {'custom_fields': [...]})`.
- **Posts** → REST `meta` works. XML-RPC **silently no-ops** here when the key already exists.
- REST also *hides* Yoast meta on pages when reading — so a "page has no SEO title" audit via REST is a **false negative**. Verify by scraping the live `<title>` / `<meta name="description">`.

**Redirection plugin** is active: `GET/POST https://affordableroofingconstruction.com/wp-json/redirection/v1/redirect` (Basic auth, app password). Use it for real 301s.

**Also active:** Yoast, Jetpack, WPForms, OptinMonster, MonsterInsights, WP Statistics, Insert Headers & Footers, Bluehost plugin.
