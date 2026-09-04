#!/usr/bin/env python3
"""
Cold Calling Absentee Owners - 30-Day Qualification Sequence
Automated email + text outreach with reply detection
"""

import os
import sys
import json
import smtplib
import time
import random
from datetime import datetime, timedelta
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

# Load shared secrets from /root/agents/.env (no hardcoded credentials in source)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from secrets_loader import require

# Config
CAMPAIGN_FILE = '/root/.openclaw/workspace-jack-sullivan/leads/cold-calling-campaign.json'
LOCK_FILE = '/root/.openclaw/workspace-jack-sullivan/leads/cold-calling-sequence.lock'
LOCK_MAX_AGE_SECONDS = 1800  # 30 min — stale lock auto-removed
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = "jack@thehooverhometeam.com"
EMAIL_PASSWORD = require("JACK_EMAIL_APP_PASSWORD")
EMAIL_CC = "ch@thehooverhometeam.com"

HEADSHOT_PATH = Path('/root/.openclaw/workspace-jack-sullivan/assets/jack-headshot.jpg')

SIGNATURE_HTML = """
<br>
<table cellpadding="0" cellspacing="0" border="0" style="font-family: Arial, sans-serif;">
  <tr>
    <td style="padding-right: 15px; vertical-align: top;">
      <img src="cid:jackphoto" alt="Jack Sullivan" width="90" height="90" style="border-radius: 50%; object-fit: cover;">
    </td>
    <td style="vertical-align: top;">
      <p style="margin: 0; font-size: 16px; font-weight: bold; color: #1a3a5c;">Jack Sullivan</p>
      <p style="margin: 2px 0; font-size: 13px; color: #555;">Lead Intelligence Specialist</p>
      <p style="margin: 2px 0; font-size: 13px; color: #555;">The Hoover Home Team powered by REAL LLC</p>
      <p style="margin: 8px 0 0; font-size: 13px;">
        <span style="color: #1a3a5c;">📱</span> <a href="tel:+13862733460" style="color: #1a3a5c; text-decoration: none;">(386) 273-3460</a>
      </p>
      <p style="margin: 2px 0; font-size: 13px;">
        <span style="color: #1a3a5c;">✉️</span> <a href="mailto:jack@thehooverhometeam.com" style="color: #1a3a5c; text-decoration: none;">jack@thehooverhometeam.com</a>
      </p>
    </td>
  </tr>
</table>
"""


def text_to_html(body_text):
    """Convert plain text body to HTML paragraphs with signature."""
    lines = body_text.strip().split('\n')
    html_lines = []
    for line in lines:
        if line.strip():
            html_lines.append(f"<p style='margin: 0 0 10px 0; font-family: Arial, sans-serif; font-size: 14px; color: #333;'>{line}</p>")
        else:
            html_lines.append("<br>")
    body_html = "\n".join(html_lines)
    return f"<html><body>\n{body_html}\n{SIGNATURE_HTML}\n</body></html>"


# Schedule: (day, touch_number, type) — email only, no SMS
SCHEDULE = [
    (1,  1,  "email"),
    (3,  2,  "skip"),   # Former text touch — removed
    (6,  3,  "email"),
    (9,  4,  "skip"),   # Former text touch — removed
    (12, 5,  "email"),
    (15, 6,  "skip"),   # Former text touch — removed
    (18, 7,  "email"),
    (22, 8,  "skip"),   # Former text touch — removed
    (26, 9,  "email"),
    (30, 10, "skip"),   # Former text touch — removed
]

# Email Templates
EMAIL_TEMPLATES = {
    1: {
        "subject": "Quick question about your {city} property",
        "body": """Hi {first_name},

I tried reaching you by phone earlier — no worries if you missed it.

I'm Jack from The Hoover Home Team. I work with a lot of out-of-area property owners in {city}, and I wanted to check in to see what your plans are for the property.

No agenda here — just curious if it's something you're holding onto, renting out, or if you've thought about selling at some point.

Happy to chat if you'd like, or feel free to reply here."""
    },
    3: {
        "subject": "Following up — {address}",
        "body": """Hi {first_name},

Just circling back on my note about your property in {city}.

I know managing a place from out of state can be a lot — whether it's a rental, vacation home, or something you're still figuring out. If you ever want to talk through your options, I'm happy to help.

What's your current situation with the property?"""
    },
    5: {
        "subject": "Quick question — is the property occupied?",
        "body": """Hi {first_name},

I wanted to follow up one more time about your {city} property.

I'm curious — is it currently occupied, rented, or sitting vacant? That helps me understand if there's anything I can help with, whether it's selling, finding a tenant, or just keeping an eye on things locally.

Either way, no pressure. Just here if you need a hand."""
    },
    7: {
        "subject": "Market update for {city} owners",
        "body": """Hi {first_name},

I've been keeping tabs on the {city} market, and things have been moving. Thought you might want to know where your property stands.

If you're curious what it might be worth — or just want to talk through whether now's the right time to make a move — let me know.

No obligation. Just information."""
    },
    9: {
        "subject": "Last note from me — {address}",
        "body": """Hi {first_name},

I've reached out a few times and haven't heard back, so I'll keep this short.

If you ever decide to sell, rent, or just want a local contact in {city}, I'm here. My info is below.

Wishing you all the best with the property."""
    }
}


def acquire_lock():
    """Return True if lock acquired, False if another instance is running."""
    lock = Path(LOCK_FILE)
    if lock.exists():
        age = time.time() - lock.stat().st_mtime
        if age < LOCK_MAX_AGE_SECONDS:
            return False
        # Stale lock — remove and continue
        lock.unlink()
    lock.write_text(str(os.getpid()))
    return True


def release_lock():
    lock = Path(LOCK_FILE)
    if lock.exists():
        lock.unlink()


def load_campaign():
    with open(CAMPAIGN_FILE) as f:
        return json.load(f)


def save_campaign(data):
    with open(CAMPAIGN_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def get_campaign_day(campaign):
    """Calculate days since campaign start"""
    start = datetime.strptime(campaign['created'], '%Y-%m-%d')
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    return (today - start).days + 1


def extract_city(address):
    """Extract city from address string"""
    if not address:
        return "your area"
    parts = address.split(',')
    if len(parts) >= 2:
        return parts[-2].strip()
    return "your area"


def build_email_message(lead, touch_num):
    """Build email MIMEMultipart for given lead and touch number"""
    template = EMAIL_TEMPLATES.get(touch_num)
    if not template:
        return None, f"No template for touch {touch_num}"

    city = extract_city(lead.get('address', ''))
    address = lead.get('address', 'your property')

    subject = template['subject'].format(
        first_name=lead.get('first_name', 'there'),
        city=city,
        address=address
    )
    body = template['body'].format(
        first_name=lead.get('first_name', 'there'),
        city=city,
        address=address
    )

    msg = MIMEMultipart("related")
    msg['From'] = f"Jack Sullivan <{EMAIL_SENDER}>"
    msg['To'] = lead['email']
    msg['Cc'] = EMAIL_CC
    msg['Subject'] = subject

    msg_alt = MIMEMultipart("alternative")
    msg.attach(msg_alt)
    msg_alt.attach(MIMEText(text_to_html(body), 'html'))

    with open(HEADSHOT_PATH, "rb") as f:
        img = MIMEImage(f.read())
        img.add_header("Content-ID", "<jackphoto>")
        img.add_header("Content-Disposition", "inline", filename="jack.jpg")
        msg.attach(img)

    return msg, None


def make_tls_context():
    """Build TLS context compatible with OpenSSL 3.0+ on this host"""
    import ssl
    # The prior comment here claimed the hostname check "trips on this server's
    # OpenSSL 3.0" and disabled verification. That claim is falsified: cadence-engine.py
    # has used create_default_context() against the same smtp.gmail.com from this host
    # since 2026-08-24 with zero auth failures. CERT_NONE defeats TLS against a MITM.
    return ssl.create_default_context()


def open_smtp_connection():
    """Open and return a persistent SMTP connection"""
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30)
    server.ehlo()
    server.starttls(context=make_tls_context())
    server.ehlo()
    server.login(EMAIL_SENDER, EMAIL_PASSWORD)
    return server


def send_email(lead, touch_num, server=None):
    """Send email for given touch number using optional persistent SMTP server"""
    if not lead.get('email'):
        return False, "No email"

    msg, err = build_email_message(lead, touch_num)
    if err:
        return False, err

    try:
        # Use provided server or open a one-off connection
        if server:
            server.send_message(msg)
        else:
            conn = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30)
            conn.ehlo()
            conn.starttls(context=make_tls_context())
            conn.ehlo()
            conn.login(EMAIL_SENDER, EMAIL_PASSWORD)
            conn.send_message(msg)
            conn.quit()
        return True, "Sent"
    except Exception as e:
        return False, str(e)



def run_daily_sequence():
    """Run today's scheduled touches"""
    if not acquire_lock():
        print("Another instance is already running. Exiting.")
        return {'sent': 0, 'skipped': 0, 'failed': 0, 'replied': 0}

    try:
        return _run_daily_sequence()
    finally:
        release_lock()


def _run_daily_sequence():
    """Internal: run today's scheduled touches (called under lock)"""
    campaign = load_campaign()
    day = get_campaign_day(campaign)
    
    print(f"{'='*60}")
    print(f"COLD CALLING SEQUENCE - Day {day}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}\n")
    
    # Find today's touch
    todays_touch = None
    for sched_day, touch_num, touch_type in SCHEDULE:
        if sched_day == day:
            todays_touch = (touch_num, touch_type)
            break
    
    if not todays_touch:
        print(f"No touch scheduled for day {day}. Rest day.")
        return {'sent': 0, 'skipped': 0, 'failed': 0, 'replied': 0}
    
    touch_num, touch_type = todays_touch
    print(f"Today's Touch: #{touch_num} ({touch_type.upper()})\n")

    results = {'sent': 0, 'skipped': 0, 'failed': 0, 'replied': 0}

    # Skipped touches (former SMS) — no sends, just log and move on
    if touch_type == "skip":
        print(f"Touch #{touch_num} is a skipped touch (former SMS). Nothing to send.")
        return results

    # Open one persistent SMTP connection for all email touches
    # (avoids hammering Gmail with 159 separate login/logout cycles)
    smtp_server = None
    try:
        smtp_server = open_smtp_connection()
        print("SMTP connection established ✓\n")
    except Exception as e:
        print(f"SMTP connection failed: {e}")
        return results

    try:
        for lead in campaign['leads']:
            # Skip if already replied
            if lead.get('replied'):
                results['replied'] += 1
                continue

            # Skip if not active
            if lead.get('status') != 'active':
                results['skipped'] += 1
                continue

            # Skip if already did this touch
            if lead.get('current_touch', 0) >= touch_num:
                results['skipped'] += 1
                continue

            name = f"{lead.get('first_name', '')} {lead.get('last_name', '')}".strip()
            success, msg = send_email(lead, touch_num, server=smtp_server)

            if success:
                print(f"  ✓ {name}: email sent")
                lead['current_touch'] = touch_num
                lead['last_touch_date'] = datetime.now().isoformat()
                results['sent'] += 1
            else:
                print(f"  ✗ {name}: {msg}")
                results['failed'] += 1

            # Spacing between sends to avoid spam filters
            time.sleep(random.uniform(2, 5))
    finally:
        if smtp_server:
            try:
                smtp_server.quit()
            except Exception:
                pass

    # Save updated campaign
    save_campaign(campaign)
    
    print(f"\n{'='*60}")
    print(f"RESULTS: {results['sent']} sent, {results['skipped']} skipped, {results['failed']} failed, {results['replied']} replied")
    print(f"{'='*60}")
    
    return results


def mark_replied(email_or_phone):
    """Mark a lead as replied (stops their sequence)"""
    campaign = load_campaign()
    
    for lead in campaign['leads']:
        if lead.get('email') == email_or_phone or lead.get('phone') == email_or_phone:
            lead['replied'] = True
            lead['status'] = 'replied'
            save_campaign(campaign)
            return True, lead
    
    return False, None


def get_stats():
    """Get campaign statistics"""
    campaign = load_campaign()
    
    total = len(campaign['leads'])
    active = sum(1 for l in campaign['leads'] if l.get('status') == 'active' and not l.get('replied'))
    replied = sum(1 for l in campaign['leads'] if l.get('replied'))
    completed = sum(1 for l in campaign['leads'] if l.get('current_touch', 0) >= 10)
    
    # Touch breakdown
    touches = {}
    for l in campaign['leads']:
        t = l.get('current_touch', 0)
        touches[t] = touches.get(t, 0) + 1
    
    return {
        'total': total,
        'active': active,
        'replied': replied,
        'completed': completed,
        'day': get_campaign_day(campaign),
        'touches': touches
    }


def weekly_report():
    """Generate weekly status report"""
    stats = get_stats()
    
    report = f"""
📊 **COLD CALLING SEQUENCE - WEEKLY REPORT**

**Campaign Day:** {stats['day']} of 30
**Total Leads:** {stats['total']}
**Active in Sequence:** {stats['active']}
**Replied (paused):** {stats['replied']}
**Completed Sequence:** {stats['completed']}

**Touch Progress:**
"""
    for touch in range(11):
        count = stats['touches'].get(touch, 0)
        if count > 0:
            report += f"  Touch {touch}: {count} leads\n"
    
    return report


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "--stats":
            stats = get_stats()
            print(json.dumps(stats, indent=2))
        elif cmd == "--report":
            print(weekly_report())
        elif cmd == "--mark-replied" and len(sys.argv) > 2:
            success, lead = mark_replied(sys.argv[2])
            if success:
                print(f"Marked as replied: {lead['first_name']} {lead['last_name']}")
            else:
                print("Lead not found")
        else:
            print("Usage: cold-calling-sequence.py [--stats|--report|--mark-replied <email/phone>]")
    else:
        run_daily_sequence()
