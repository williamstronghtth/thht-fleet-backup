#!/usr/bin/env python3
"""Guarantee today's CLEARED-FIGURES block exists before the gates run.

WHY THIS EXISTS (2026-09-02)
----------------------------
The cleared-figures block is the one input to brief-gate.py that nothing
generates and nothing checks. When it is missing, the gate does not fail --
it silently checks today's copy against YESTERDAY's block and reports CLEAN.
That is the worst possible failure mode: a green light from a stale source.

It has now been late four times: Aug 28, Aug 29-30, Sept 1, Sept 2.

On Sept 1 an amendment was written stating "a 06:00 cron now writes a
carry-forward stub." No such cron existed. The prose describing the control
shipped; the control did not. That is its own lesson and it is recorded in
the Sept 2 block: A CONTROL IS NOT SHIPPED UNTIL ITS SCHEDULER LINE EXISTS.
Verify with `crontab -l`, never by remembering having written it.

WHAT THIS DOES
--------------
06:00 ET, daily. If today's block is missing, copy the newest one forward,
stamp it UNREVIEWED, and alert. The stub is deliberately marked so that a
carry-forward nobody has looked at cannot pass as a reviewed clearance --
the same distinction the Sept 1 block drew between clearing FIGURES and
clearing WORDING.

It does NOT clear anything. A human still reviews. It exists so that the
failure is LOUD instead of silent.
"""
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
WORKSPACE = Path("/root/agents/william-strong/workspace")
PATTERN = "CLEARED-FIGURES-*.md"
RELATIVE_TIME = re.compile(r"\b(today|this week|yesterday|tomorrow)\b", re.I)


def alert(message):
    """Telegram Chris. Never raises -- an alert failure must not mask the alert."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat = os.environ.get("TELEGRAM_CHAT_ID")
    print(message)
    if not token or not chat:
        print("[stub] no telegram creds in env; printed only", file=sys.stderr)
        return
    try:
        data = urllib.parse.urlencode({"chat_id": chat, "text": message}).encode()
        urllib.request.urlopen(
            f"https://api.telegram.org/bot{token}/sendMessage", data, timeout=15
        )
    except Exception as exc:  # noqa: BLE001 - alerting must never crash the job
        print(f"[stub] telegram failed: {exc}", file=sys.stderr)


def main():
    today = datetime.now(ET).strftime("%Y-%m-%d")
    target = WORKSPACE / f"CLEARED-FIGURES-{today}.md"
    if target.exists():
        print(f"[stub] {target.name} already exists — nothing to do.")
        return 0

    blocks = sorted(WORKSPACE.glob(PATTERN))
    if not blocks:
        alert("🚨 CLEARED-FIGURES: no block exists at all. Every figure gate is "
              "running blind. Nothing may publish until one is written.")
        return 2

    newest = blocks[-1]
    body = newest.read_text()

    # A stub is a carry-forward, and the Sept 1 rule says a carry-forward may
    # not contain relative time words -- they silently re-date themselves.
    stale_words = sorted({m.group(0).lower() for m in RELATIVE_TIME.finditer(body)})
    warning = ""
    if stale_words:
        warning = ("\n> ⚠️ **Carried text contains relative-time wording "
                   f"({', '.join(stale_words)}).** Per the Sept 1 amendment a "
                   "carry-forward may not contain these. Replace with absolute "
                   "dates during review.\n")

    header = (
        f"# CLEARED FIGURES — {today} — ⛔ UNREVIEWED AUTO-STUB\n\n"
        f"**Generated 06:00 ET by `cleared-figures-stub.py` because no block "
        f"existed for {today}.** Copied forward from `{newest.name}`.\n\n"
        f"**THIS IS NOT A CLEARANCE.** No human has confirmed these figures are "
        f"still current for {today}. It exists so that the figure gates check "
        f"against a file that knows it is stale, instead of silently checking "
        f"against yesterday's block and reporting CLEAN.\n\n"
        f"**Before anything publishes today, William must review this file, "
        f"confirm the carry-forward basis, and delete this header.**\n"
        f"{warning}\n---\n\n"
    )
    target.write_text(header + body)
    alert(
        f"⛔ CLEARED-FIGURES-{today}.md was MISSING at 06:00 ET.\n\n"
        f"Auto-stub written, carried forward from {newest.name} and marked "
        f"UNREVIEWED. Figure gates will run against it.\n\n"
        f"William must review and clear it before any copy ships today."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
