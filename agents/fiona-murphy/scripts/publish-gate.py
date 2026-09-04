#!/usr/bin/env python3
"""Blog publish-verification gate for Fiona's daily run.

Requested by William (2026-08-10): the WordPress publish step silently dropped
on Aug 4/5/8 — drafts were written but no post went live and no alert fired.
This gate runs at the END of Fiona's daily session:

  1. Query the WP REST API for a post PUBLISHED today (ET).
  2. If one exists -> log OK, exit 0.
  3. If none exists -> loudly alert Chris on Telegram, exit 1.

Idempotent and safe to re-run. No hardcoded secrets: WP creds come from the
gitignored workspace `.env` (WP_SITE/WP_USER/WP_APP_PASSWORD); the Telegram bot
token comes from /root/agents/telegram-bots.json.

Usage:  python3 publish-gate.py            # check today, alert on miss
        python3 publish-gate.py --dry-run  # check only, never send Telegram
"""
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import quote
from zoneinfo import ZoneInfo

import requests

from wp_config import get_credentials, WAF_COOKIE

ET = ZoneInfo("America/New_York")
# The host WAF (Mod_Security) 406s the default python-requests UA; a curl UA
# passes (matches the curl-based publish scripts that already work).
WP_USER_AGENT = "curl/8.5.0"
CHRIS_CHAT_ID = "8560812913"
BOTS_FILE = Path("/root/agents/telegram-bots.json")
FIONA_AGENT_ID = "fiona-murphy"
REQUEST_TIMEOUT = 20
AUDIT_LOG = Path("/root/agents/logs/publish-gate-audit.log")


def get_todays_posts(status):
    """Return posts of the given status (publish|draft) dated today (ET).

    Raises requests.RequestException on network/API failure so a broken check
    is never mistaken for a clean pass.
    """
    site, user, password = <REDACTED:CREDENTIAL>()
    now = datetime.now(ET)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    # WP expects site-local ISO time (no offset) for the after/before filters.
    url = (
        f"{site}/wp-json/wp/v2/posts"
        f"?status={status}"
        f"&after={quote(start.strftime('%Y-%m-%dT%H:%M:%S'))}"
        f"&before={quote(end.strftime('%Y-%m-%dT%H:%M:%S'))}"
        f"&per_page=20&_fields=id,link,date,title"
    )
    resp = requests.get(
        url,
        auth=(user, password),
        headers={"Cookie": WAF_COOKIE, "User-Agent": WP_USER_AGENT},
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()


def get_fiona_bot_token():
    """Read Fiona's Telegram bot token from the shared bots config."""
    bots = json.loads(BOTS_FILE.read_text()).get("bots", [])
    for bot in bots:
        if bot.get("agent_id") == FIONA_AGENT_ID:
            return bot.get("bot_token")
    raise RuntimeError(f"No bot_token for '{FIONA_AGENT_ID}' in {BOTS_FILE}")


def alert_chris(message):
    """Send a loud Telegram alert to Chris. Returns True on success."""
    token = <REDACTED:CREDENTIAL>()
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    resp = requests.post(
        url,
        data={"chat_id": CHRIS_CHAT_ID, "text": message, "parse_mode": "Markdown"},
        timeout=REQUEST_TIMEOUT,
    )
    if resp.status_code != 200:
        print(f"ERROR: Telegram alert failed: {resp.status_code} {resp.text}")
        return False
    return True


def log_outcome(message):
    """Print, and append one timestamped line to a dedicated audit log.

    stdout alone goes to the shared logs/cron.log, which every agent appends to
    and which churns — so on 2026-08-30 the gate's own firing history was
    unverifiable past the current day. A monitor whose fires can't be counted
    is indistinguishable from a monitor that stopped. Never let the only record
    of a gate live in a shared, rotating log.
    """
    print(message)
    stamp = datetime.now(ET).strftime("%Y-%m-%dT%H:%M:%S%z")
    first_line = message.splitlines()[0] if message else ""
    try:
        AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
        with AUDIT_LOG.open("a", encoding="utf-8") as handle:
            handle.write(f"{stamp} {first_line}\n")
    except OSError as exc:
        # Audit logging must never take down the gate itself.
        print(f"WARN: could not write audit log {AUDIT_LOG}: {exc}")


def main():
    dry_run = "--dry-run" in sys.argv
    today = datetime.now(ET).strftime("%Y-%m-%d")
    try:
        published = get_todays_posts("publish")
        drafts = get_todays_posts("draft")
    except requests.RequestException as exc:
        # A failed check is itself worth surfacing — don't exit clean on error.
        msg = f"⚠️ *Blog gate check failed* ({today}): could not reach WP API — {exc}"
        log_outcome(msg)
        if not dry_run:
            alert_chris(msg)
        return 2

    if published:
        titles = ", ".join(p.get("title", {}).get("rendered", "?") for p in published)
        log_outcome(f"✅ OK: {len(published)} post(s) published today ({today}): {titles}")
        return 0

    if not drafts:
        # Nothing drafted or published today (e.g. a social-only day) — not a
        # publish failure, so stay quiet rather than false-alarm.
        log_outcome(f"✅ OK: no blog drafted or published today ({today}) — nothing to gate.")
        return 0

    # The exact bug William reported: a draft was written but the publish
    # step silently dropped. Loudly flag it for a same-day manual push.
    draft_titles = ", ".join(d.get("title", {}).get("rendered", "?") for d in drafts)
    msg = (
        f"🚨 *BLOG DID NOT PUBLISH TODAY* ({today})\n\n"
        f"A draft exists but no post went live on thehooverhometeam.com: "
        f"_{draft_titles}_\n\n"
        "The publish step dropped — it needs a manual push. Flagging same-day "
        "so it doesn't slip to the weekly review."
    )
    log_outcome(msg)
    if dry_run:
        print("(--dry-run: Telegram alert suppressed)")
        return 1
    alert_chris(msg)
    return 1


if __name__ == "__main__":
    sys.exit(main())
