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

### WordPress (thehooverhometeam.com) — WAF gotcha
- Host has Mod_Security WAF. It **406s the default `python-requests` User-Agent**.
- Fix: set `User-Agent: curl/8.5.0` (or any curl UA). curl-based scripts work as-is.
- Also send `Cookie: humans_21909=1` to skip the JS challenge (see `fiona-murphy/scripts/wp_config.py`).
- REST base: `https://thehooverhometeam.com/wp-json/wp/v2`; auth = WP_USER + WP_APP_PASSWORD (basic).
- Creds live in `fiona-murphy/workspace/.env` (gitignored). Never hardcode.
- Blog publish-verification gate: `fiona-murphy/scripts/publish-gate.py`, cron `0 18 * * *`.
