#!/usr/bin/env python3
"""
GA4 Weekly Report — thehooverhometeam.com
Pulls this week vs last week stats and sends to Chris via Telegram.
"""

import json
import subprocess
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timedelta

WORKSPACE = "/root/agents/fiona-murphy/workspace"
TOKEN_FILE = f"{WORKSPACE}/credentials/ga4-oauth-token.json"
CLIENT_SECRET_FILE = f"{WORKSPACE}/credentials/client_secret.json"
PROPERTY_ID = "364061355"
TELEGRAM_BOT_TOKEN = "<REDACTED:TELEGRAM_BOT_TOKEN>"
TELEGRAM_CHAT_ID = "8560812913"


def load_tokens():
    with open(TOKEN_FILE) as f:
        return json.load(f)


def refresh_access_token(tokens):
    with open(CLIENT_SECRET_FILE) as f:
        client_data = json.load(f)

    installed = client_data.get("installed", client_data)
    client_id = installed["client_id"]
    client_secret = installed["client_secret"]
    refresh_token = tokens.get("refresh_token") or tokens.get("_refresh_token")

    payload = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": <REDACTED:CREDENTIAL>,
        "refresh_token": <REDACTED:CREDENTIAL>,
        "grant_type": "refresh_token",
    }).encode()

    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        data=payload,
        method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())

    tokens["token"] = result["access_token"]
    with open(TOKEN_FILE, "w") as f:
        json.dump(tokens, f, indent=2)

    return result["access_token"]


def get_access_token():
    # Always refresh to avoid stale token issues on scheduled runs
    tokens = load_tokens()
    return refresh_access_token(tokens)


def run_report(access_token, start_date, end_date):
    url = f"https://analyticsdata.googleapis.com/v1beta/properties/{PROPERTY_ID}:runReport"
    body = json.dumps({
        "dateRanges": [{"startDate": start_date, "endDate": end_date}],
        "metrics": [
            {"name": "activeUsers"},
            {"name": "sessions"},
            {"name": "screenPageViews"},
            {"name": "averageSessionDuration"},
        ]
    }).encode()

    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Authorization", f"Bearer {access_token}")
    req.add_header("Content-Type", "application/json")

    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())

    row = data["rows"][0]["metricValues"]
    return {
        "active_users": int(float(row[0]["value"])),
        "sessions": int(float(row[1]["value"])),
        "page_views": int(float(row[2]["value"])),
        "avg_session_sec": float(row[3]["value"]),
    }


def format_duration(seconds):
    m = int(seconds) // 60
    s = int(seconds) % 60
    return f"{m}m {s:02d}s"


def delta_str(current, previous):
    if previous == 0:
        return "(no prior data)"
    change = current - previous
    pct = (change / previous) * 100
    arrow = "+" if change >= 0 else ""
    return f"{arrow}{change} ({arrow}{pct:.1f}%)"


def send_telegram(message):
    payload = urllib.parse.urlencode({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
        data=payload,
        method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def main():
    today = datetime.now().date()
    # This week: last 7 days (yesterday back 6 more days)
    this_end = today - timedelta(days=1)
    this_start = today - timedelta(days=7)
    # Last week: 8-14 days ago
    last_end = today - timedelta(days=8)
    last_start = today - timedelta(days=14)

    access_token = <REDACTED:CREDENTIAL>()

    this_week = run_report(access_token, this_start.isoformat(), this_end.isoformat())
    last_week = run_report(access_token, last_start.isoformat(), last_end.isoformat())

    this_dur = format_duration(this_week["avg_session_sec"])
    last_dur = format_duration(last_week["avg_session_sec"])

    report = f"""📊 *Weekly Traffic Report — thehooverhometeam.com*
_{this_start.strftime('%b %d')} – {this_end.strftime('%b %d, %Y')} vs prior week_

*Active Users:* {this_week['active_users']} _{delta_str(this_week['active_users'], last_week['active_users'])}_
*Sessions:* {this_week['sessions']} _{delta_str(this_week['sessions'], last_week['sessions'])}_
*Page Views:* {this_week['page_views']} _{delta_str(this_week['page_views'], last_week['page_views'])}_
*Avg Session:* {this_dur} _(was {last_dur})_

_Prior week: {last_start.strftime('%b %d')} – {last_end.strftime('%b %d')}_
— Fiona 🏡"""

    send_telegram(report)
    print("Report sent successfully.")
    print(report)


if __name__ == "__main__":
    main()
