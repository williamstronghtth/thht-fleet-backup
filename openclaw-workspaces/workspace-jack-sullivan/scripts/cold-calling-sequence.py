#!/usr/bin/env python3
"""
Cold Calling Absentee Owners - 30-Day Qualification Sequence
Automated email + text outreach with reply detection
"""

import os
import sys
import json
import smtplib
import requests
import time
import random
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Config
CAMPAIGN_FILE = '/root/.openclaw/workspace-jack-sullivan/leads/cold-calling-campaign.json'
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = "jack@thehooverhometeam.com"
EMAIL_PASSWORD = "rpwg sdna xtgp fujn"
EMAIL_CC = "ch@thehooverhometeam.com"

QUO_API = "https://api.openphone.com/v1/messages"
QUO_TOKEN = "<REDACTED:CREDENTIAL>"
QUO_FROM = "+13862733460"

STATE_ABBREVS = {
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
    'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
    'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
    'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
    'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
}

def normalize_address(address):
    """Convert ALL CAPS address to Title Case. Preserves state abbreviations and zip codes."""
    if not address:
        return address
    parts = address.split(',')
    result = []
    for part in parts:
        words = part.strip().split()
        normalized = []
        for word in words:
            if word.upper() in STATE_ABBREVS:
                normalized.append(word.upper())
            elif word.isdigit():
                normalized.append(word)
            else:
                normalized.append(word.capitalize())
        result.append(' '.join(normalized))
    return ', '.join(result)

# Schedule: (day, touch_number, type)
# NOTE: Texts disabled until Quo/OpenPhone A2P approved
SCHEDULE = [
    (1, 1, "email"),
    (3, 2, "skip"),    # Was text - Quo pending
    (6, 3, "email"),
    (9, 4, "skip"),    # Was text - Quo pending
    (12, 5, "email"),
    (15, 6, "skip"),   # Was text - Quo pending
    (18, 7, "email"),
    (22, 8, "skip"),   # Was text - Quo pending
    (26, 9, "email"),
    (30, 10, "skip"),  # Was text - Quo pending
]

# Email Templates
EMAIL_TEMPLATES = {
    1: {
        "subject": "Quick question about your {city} property",
        "body": """Hi {first_name},

I tried reaching you by phone earlier — no worries if you missed it.

I'm Chris with The Hoover Home Team. I work with a lot of out-of-area property owners in {city}, and I wanted to check in to see what your plans are for the property.

No agenda here — just curious if it's something you're holding onto, renting out, or if you've thought about selling at some point.

Happy to chat if you'd like, or feel free to reply here.

Best,
Chris Hoover
The Hoover Home Team"""
    },
    3: {
        "subject": "Following up — {address}",
        "body": """Hi {first_name},

Just circling back on my note about your property in {city}.

I know managing a place from out of state can be a lot — whether it's a rental, vacation home, or something you're still figuring out. If you ever want to talk through your options, I'm happy to help.

What's your current situation with the property?

Best,
Chris"""
    },
    5: {
        "subject": "Quick question — is the property occupied?",
        "body": """Hi {first_name},

I wanted to follow up one more time about your {city} property.

I'm curious — is it currently occupied, rented, or sitting vacant? That helps me understand if there's anything I can help with, whether it's selling, finding a tenant, or just keeping an eye on things locally.

Either way, no pressure. Just here if you need a hand.

Chris"""
    },
    7: {
        "subject": "Market update for {city} owners",
        "body": """Hi {first_name},

I've been keeping tabs on the {city} market, and things have been moving. Thought you might want to know where your property stands.

If you're curious what it might be worth — or just want to talk through whether now's the right time to make a move — let me know.

No obligation. Just information.

Chris"""
    },
    9: {
        "subject": "Last note from me — {address}",
        "body": """Hi {first_name},

I've reached out a few times and haven't heard back, so I'll keep this short.

If you ever decide to sell, rent, or just want a local contact in {city}, I'm here. My info is below.

Wishing you all the best with the property.

Chris Hoover
The Hoover Home Team
(386) 273-3460"""
    }
}

# Text Templates
TEXT_TEMPLATES = {
    2: "Hi {first_name}, this is Chris Hoover — I left you a voicemail about your property in {city}. Just wanted to see if you had any questions or if there's anything I can help with. No pressure, just checking in.",
    4: "Hey {first_name}, following up on your {city} property. Are you currently renting it out or is it sitting vacant? Curious what your plans are. — Chris",
    6: "Hi {first_name}, quick question — have you thought about selling your {city} property, or are you planning to hold onto it for now? Either way, happy to chat if helpful. — Chris",
    8: "Hey {first_name}, just checking in one more time. If you ever want to know what your property might be worth or talk through options, I'm around. — Chris",
    10: "Hi {first_name}, last text from me. If you ever need help with your {city} property — selling, renting, or anything else — feel free to reach out anytime. Best of luck! — Chris, The Hoover Home Team"
}


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


def send_email(lead, touch_num):
    """Send email for given touch number"""
    if not lead.get('email'):
        return False, "No email"
    
    template = EMAIL_TEMPLATES.get(touch_num)
    if not template:
        return False, f"No template for touch {touch_num}"
    
    city = extract_city(normalize_address(lead.get('address', '')))
    address = normalize_address(lead.get('address', 'your property'))
    
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
    
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = lead['email']
    msg['Cc'] = EMAIL_CC
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True, "Sent"
    except Exception as e:
        return False, str(e)


def send_text(lead, touch_num):
    """Send SMS for given touch number"""
    if not lead.get('phone'):
        return False, "No phone"
    
    template = TEXT_TEMPLATES.get(touch_num)
    if not template:
        return False, f"No template for touch {touch_num}"
    
    city = extract_city(lead.get('address', ''))
    
    message = template.format(
        first_name=lead.get('first_name', 'there'),
        city=city
    )
    
    # Format phone
    phone = ''.join(filter(str.isdigit, str(lead['phone'])))
    if len(phone) == 10:
        phone = "1" + phone
    if not phone.startswith("+"):
        phone = "+" + phone
    
    try:
        resp = requests.post(
            QUO_API,
            headers={
                "Authorization": f"Bearer {QUO_TOKEN}",
                "Content-Type": "application/json"
            },
            json={
                "from": QUO_FROM,
                "to": phone,
                "content": message
            },
            timeout=30
        )
        
        if resp.status_code in [200, 201, 202]:
            return True, "Sent"
        else:
            return False, f"HTTP {resp.status_code}"
    except Exception as e:
        return False, str(e)


def run_daily_sequence():
    """Run today's scheduled touches"""
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
    
    for i, lead in enumerate(campaign['leads']):
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
        
        if touch_type == "skip":
            # SMS touch pending A2P approval — skip silently
            print(f"  - {name}: skipped (SMS pending)")
            results['skipped'] += 1
            continue
        elif touch_type == "email":
            success, msg = send_email(lead, touch_num)
        else:
            success, msg = send_text(lead, touch_num)

        if success:
            print(f"  ✓ {name}: {touch_type} sent")
            lead['current_touch'] = touch_num
            lead['last_touch_date'] = datetime.now().isoformat()
            results['sent'] += 1
        else:
            print(f"  ✗ {name}: {msg}")
            results['failed'] += 1
        
        # Small delay between sends
        time.sleep(random.uniform(2, 5))
    
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
