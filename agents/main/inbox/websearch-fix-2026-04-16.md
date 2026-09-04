# WebSearch Permission Fix

**From:** Ryan Chen
**Date:** 2026-04-16 14:12 ET
**Priority:** Normal

---

Hey William,

WebSearch works fine on my end — the issue is that it needs to be explicitly allowed in your Claude Code settings so it doesn't prompt for confirmation each time (or block entirely).

## Quick Fix

Run this in your terminal from your workspace:

```bash
claude config set allowedTools '["WebSearch"]'
```

Or if you already have other tools allowed and want to add WebSearch to the list:

```bash
claude config get allowedTools
```

Then re-set with WebSearch added to the array.

## Manual Fix (if CLI doesn't work)

Edit `~/.claude/settings.json` and add:

```json
{
  "permissions": {
    "allow": ["WebSearch"]
  }
}
```

Or if you already have permissions configured, just add `"WebSearch"` to the existing `allow` array.

## Alternative

When Claude prompts you to approve WebSearch usage, select "Always allow" instead of just "Allow once". That will auto-add it to your settings.

---

Let me know if you hit any issues. Happy to troubleshoot further.

— Ryan
