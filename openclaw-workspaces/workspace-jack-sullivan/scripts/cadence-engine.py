#!/usr/bin/env python3
"""
25-Touch Cadence Engine for Lis Pendens Leads
Handles Email + SMS touches. Calls are queued for manual execution.
"""

import os
import sys
import json
import time
import random
import requests
from datetime import datetime, timedelta

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


# === CONFIG ===
CRM_API = "https://clientlist.onrender.com/api/clients"
QUO_API = "https://api.openphone.com/v1/messages"
QUO_TOKEN = "<REDACTED:CREDENTIAL>"
QUO_FROM = "+13862733460"
GMAIL_USER = "jack@thehooverhometeam.com"
CC_EMAIL = "ch@thehooverhometeam.com"

# Campaign start date
CAMPAIGN_START = datetime(2026, 2, 24)

# 25-touch schedule: (day, touch_type)
CADENCE = [
    (1, "email"),
    (2, "text"),
    (3, "call"),
    (4, "email"),
    (5, "text"),
    (7, "call"),
    (8, "email"),
    (9, "text"),
    (10, "call"),
    (12, "email"),
    (13, "text"),
    (14, "call"),
    (15, "mail"),  # Direct mail - handled by Chris
    (17, "email"),
    (18, "text"),
    (19, "call"),
    (21, "email"),
    (22, "text"),
    (24, "call"),
    (25, "email"),
    (26, "text"),
    (27, "call"),
    (28, "email"),
    (29, "text"),
    (30, "call"),
]

# Email templates by touch number
EMAIL_TEMPLATES = {
    1: {
        "subject": "Quick question about your {city} property",
        "body": """Hi {first_name},

I came across your property on {street} and wanted to reach out. I work with homeowners in {city} who are exploring their options, and I thought I'd check in to see if selling might be something you're considering.

No pressure at all - just here if you'd like to have a conversation about what your home might be worth in today's market.

Would you be open to a quick chat?

Best,
Jack Sullivan
Lead Intelligence Specialist
The Hoover Home Team powered by REAL LLC"""
    },
    2: {
        "subject": "Following up - {street}",
        "body": """Hi {first_name},

Just following up on my note from a few days ago about your property on {street}.

I know timing is everything, and I'm not here to pressure you. If you're even slightly curious about what options might be available, I'm happy to share some information - no strings attached.

Let me know if you'd like to chat.

Best,
Jack Sullivan
Lead Intelligence Specialist
The Hoover Home Team powered by REAL LLC"""
    },
    3: {
        "subject": "Still thinking about {street}?",
        "body": """Hi {first_name},

I wanted to check in one more time about your property on {street}. 

The market in {city} has been moving, and I thought you might appreciate knowing where things stand - whether you're thinking about selling now or sometime down the road.

Happy to put together a quick market snapshot if that would be helpful.

Best,
Jack Sullivan
Lead Intelligence Specialist
The Hoover Home Team powered by REAL LLC"""
    },
    4: {
        "subject": "Options for {street}",
        "body": """Hi {first_name},

I've reached out a few times about your {city} property, and I understand if the timing isn't right.

That said, I work with homeowners in all kinds of situations - some want top dollar on the open market, others prefer a quick, private sale. There's no one-size-fits-all approach.

If you'd ever like to explore what makes sense for your situation, I'm here.

Best,
Jack Sullivan
Lead Intelligence Specialist
The Hoover Home Team powered by REAL LLC"""
    },
    5: {
        "subject": "Checking in - {city} property",
        "body": """Hi {first_name},

Just a quick note to see if anything has changed with your plans for {street}.

I'm still happy to help if you're exploring your options. No pressure, just keeping the door open.

Best,
Jack Sullivan
Lead Intelligence Specialist
The Hoover Home Team powered by REAL LLC"""
    },
    6: {
        "subject": "One more thought on {street}",
        "body": """Hi {first_name},

I know I've reached out several times, and I appreciate your patience.

If selling isn't on your radar right now, that's completely fine. But if circumstances change, my offer to help stands.

Wishing you all the best,
Jack Sullivan
Lead Intelligence Specialist
The Hoover Home Team powered by REAL LLC"""
    },
    7: {
        "subject": "Market update for {city}",
        "body": """Hi {first_name},

I wanted to share a quick update on the {city} market - homes similar to yours on {street} have been getting solid interest lately.

If you've been on the fence about exploring your options, now might be a good time to at least see where you stand.

Happy to chat whenever works for you.

Best,
Jack Sullivan
Lead Intelligence Specialist
The Hoover Home Team powered by REAL LLC"""
    },
    8: {
        "subject": "Last note from me - {street}",
        "body": """Hi {first_name},

This will be my last email about your {city} property. I don't want to be a bother.

If you ever decide to explore selling, my info is below. I'd be honored to help when the time is right.

Take care,
Jack Sullivan
Lead Intelligence Specialist
The Hoover Home Team powered by REAL LLC"""
    },
}

# SMS templates by touch number
SMS_TEMPLATES = {
    1: "Hi {first_name}, this is Jack from The Hoover Home Team. I recently came across your property on {street} and wanted to see if you might be open to discussing your options. No pressure - just here to help if needed. Feel free to text or call back anytime.",
    2: "Hi {first_name}, just following up on my message about your {city} property. If you have any questions about what it might be worth or what your options are, I'm happy to help. - Jack",
    3: "Hi {first_name}, checking in one more time about {street}. I work with homeowners exploring all kinds of options - whether that's selling now or just understanding the market. Let me know if I can help. - Jack",
    4: "Hi {first_name}, just a quick note to see if anything has changed with your {city} property. I'm still here if you'd like to chat. No pressure at all. - Jack",
    5: "Hi {first_name}, I know timing is everything. If you're ever curious about your options for {street}, feel free to reach out. Wishing you well. - Jack",
    6: "Hi {first_name}, last text from me about your property. If selling ever crosses your mind, I'd be glad to help. Take care. - Jack, The Hoover Home Team",
    7: "Hi {first_name}, just wanted to let you know I'm still available if you have questions about your {city} property. Here when you need me. - Jack",
    8: "Hi {first_name}, final check-in on {street}. If the time is ever right to explore your options, don't hesitate to reach out. All the best. - Jack",
}


def get_campaign_day():
    """Calculate current campaign day (1-30)"""
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    delta = (today - CAMPAIGN_START).days + 1
    return delta


def get_todays_touch():
    """Get today's touch type and number"""
    day = get_campaign_day()
    for d, touch_type in CADENCE:
        if d == day:
            # Count which email/text number this is
            touch_num = sum(1 for dd, tt in CADENCE if dd <= d and tt == touch_type)
            return day, touch_type, touch_num
    return day, None, None


def get_lis_pendens_leads():
    """Fetch lis pendens leads from CRM"""
    try:
        resp = requests.get(CRM_API, timeout=30)
        resp.raise_for_status()
        clients = resp.json()
        
        # Filter for lis pendens leads (source = "lis_pendens" or "pre-foreclosure")
        leads = [c for c in clients if c.get("source") in ["lis_pendens", "pre-foreclosure", "lis-pendens"]]
        return leads
    except Exception as e:
        print(f"Error fetching leads: {e}")
        return []


def send_email(lead, template_num):
    """Send email via Gmail API (placeholder - uses existing email script)"""
    first_name = lead.get("firstName", "there")
    email = lead.get("email")
    street = normalize_address(lead.get("address", "your property"))
    city = normalize_address(lead.get("city", "your area"))

    if not email:
        return False, "No email"

    template = EMAIL_TEMPLATES.get(template_num, EMAIL_TEMPLATES[1])
    subject = template["subject"].format(first_name=first_name, street=street, city=city)
    body = template["body"].format(first_name=first_name, street=street, city=city)
    
    # Call the email outreach script
    # For now, print what would be sent
    print(f"  EMAIL to {email}: {subject}")
    
    # TODO: Integrate with Gmail API
    return True, "Queued"


def send_sms(lead, template_num):
    """Send SMS via Quo/OpenPhone API"""
    first_name = lead.get("firstName", "there")
    phone = lead.get("phone")
    street = normalize_address(lead.get("address", "your property"))
    city = normalize_address(lead.get("city", "your area"))

    if not phone:
        return False, "No phone"
    
    # Format phone number
    phone_clean = ''.join(filter(str.isdigit, phone))
    if len(phone_clean) == 10:
        phone_clean = "1" + phone_clean
    if not phone_clean.startswith("+"):
        phone_clean = "+" + phone_clean
    
    template = SMS_TEMPLATES.get(template_num, SMS_TEMPLATES[1])
    message = template.format(first_name=first_name, street=street, city=city)
    
    try:
        resp = requests.post(
            QUO_API,
            headers={
                "Authorization": f"Bearer {QUO_TOKEN}",
                "Content-Type": "application/json"
            },
            json={
                "from": QUO_FROM,
                "to": phone_clean,
                "content": message
            },
            timeout=30
        )
        
        if resp.status_code in [200, 201, 202]:
            print(f"  SMS to {phone}: Sent")
            return True, "Sent"
        else:
            print(f"  SMS to {phone}: Failed ({resp.status_code})")
            return False, f"HTTP {resp.status_code}"
    except Exception as e:
        print(f"  SMS to {phone}: Error - {e}")
        return False, str(e)


def generate_call_list(leads, day):
    """Generate a call list for manual calling"""
    print(f"\n📞 CALL LIST FOR DAY {day}")
    print("=" * 60)
    
    for i, lead in enumerate(leads, 1):
        name = f"{lead.get('firstName', '')} {lead.get('lastName', '')}".strip()
        phone = lead.get('phone', 'No phone')
        address = lead.get('address', 'Unknown')
        city = lead.get('city', '')
        
        print(f"{i}. {name}")
        print(f"   Phone: {phone}")
        print(f"   Property: {address}, {city}")
        print()
    
    print(f"Total calls: {len(leads)}")
    return leads


def run_todays_touch(dry_run=False):
    """Execute today's touch for all lis pendens leads"""
    day, touch_type, touch_num = get_todays_touch()
    
    print(f"\n{'='*60}")
    print(f"CADENCE ENGINE - Day {day} of 30")
    print(f"Touch Type: {touch_type or 'REST DAY'} (#{touch_num})")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print(f"{'='*60}\n")
    
    if day > 30:
        print("Campaign complete! All 30 days finished.")
        return
    
    if touch_type is None:
        print("Rest day - no touches scheduled.")
        return
    
    leads = get_lis_pendens_leads()
    print(f"Found {len(leads)} lis pendens leads\n")
    
    if not leads:
        print("No leads found!")
        return
    
    if touch_type == "email":
        print(f"Sending Email #{touch_num} to {len(leads)} leads...")
        success = 0
        for lead in leads:
            if dry_run:
                print(f"  [DRY RUN] Would email {lead.get('email', 'no email')}")
                success += 1
            else:
                ok, msg = send_email(lead, touch_num)
                if ok:
                    success += 1
                time.sleep(random.uniform(300, 360))  # 5-6 min spacing
        print(f"\nEmails: {success}/{len(leads)} sent")
        
    elif touch_type == "text":
        print(f"Sending SMS #{touch_num} to {len(leads)} leads...")
        success = 0
        for lead in leads:
            if dry_run:
                print(f"  [DRY RUN] Would text {lead.get('phone', 'no phone')}")
                success += 1
            else:
                ok, msg = send_sms(lead, touch_num)
                if ok:
                    success += 1
                time.sleep(random.uniform(5, 15))  # Short delay between texts
        print(f"\nSMS: {success}/{len(leads)} sent")
        
    elif touch_type == "call":
        generate_call_list(leads, day)
        
    elif touch_type == "mail":
        print("DIRECT MAIL DAY")
        print("Chris should have the mail ready to send!")
        print(f"Leads to mail: {len(leads)}")


def show_schedule():
    """Display the full 25-touch schedule"""
    print("\n25-TOUCH CADENCE SCHEDULE")
    print("=" * 40)
    
    email_count = text_count = call_count = 0
    
    for day, touch_type in CADENCE:
        date = CAMPAIGN_START + timedelta(days=day-1)
        date_str = date.strftime("%b %d")
        
        if touch_type == "email":
            email_count += 1
            icon = "📧"
            label = f"Email #{email_count}"
        elif touch_type == "text":
            text_count += 1
            icon = "💬"
            label = f"Text #{text_count}"
        elif touch_type == "call":
            call_count += 1
            icon = "📞"
            label = f"Call #{call_count}"
        elif touch_type == "mail":
            icon = "📬"
            label = "Direct Mail"
        
        print(f"Day {day:2d} ({date_str}): {icon} {label}")
    
    print(f"\nTotals: {email_count} emails, {text_count} texts, {call_count} calls, 1 mail = 25 touches")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--schedule":
            show_schedule()
        elif sys.argv[1] == "--dry-run":
            run_todays_touch(dry_run=True)
        elif sys.argv[1] == "--calls":
            day = get_campaign_day()
            leads = get_lis_pendens_leads()
            generate_call_list(leads, day)
        else:
            print("Usage: cadence-engine.py [--schedule|--dry-run|--calls]")
    else:
        run_todays_touch(dry_run=False)
