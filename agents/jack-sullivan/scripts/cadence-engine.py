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
import smtplib
import ssl
import requests
from datetime import datetime, timedelta
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

# Load shared secrets from /root/agents/.env (no hardcoded credentials in source)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from secrets_loader import require

# === CONFIG ===
CRM_API = "https://clientlist.onrender.com/api/clients"
CRM_API_KEY = require("CRM_API_KEY")
CRM_HEADERS = {'X-API-Key': CRM_API_KEY}
QUO_API = "https://api.openphone.com/v1/messages"
QUO_TOKEN = require("QUO_TOKEN")
QUO_FROM = "+13862733460"
GMAIL_USER = "jack@thehooverhometeam.com"
CC_EMAIL = "ch@thehooverhometeam.com"
EMAIL_SENDER = "jack@thehooverhometeam.com"
EMAIL_PASSWORD = require("JACK_EMAIL_APP_PASSWORD")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

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

Would you be open to a quick chat?"""
    },
    2: {
        "subject": "Following up - {street}",
        "body": """Hi {first_name},

Just following up on my note from a few days ago about your property on {street}.

I know timing is everything, and I'm not here to pressure you. If you're even slightly curious about what options might be available, I'm happy to share some information - no strings attached.

Let me know if you'd like to chat."""
    },
    3: {
        "subject": "Still thinking about {street}?",
        "body": """Hi {first_name},

I wanted to check in one more time about your property on {street}. 

The market in {city} has been moving, and I thought you might appreciate knowing where things stand - whether you're thinking about selling now or sometime down the road.

Happy to put together a quick market snapshot if that would be helpful."""
    },
    4: {
        "subject": "Options for {street}",
        "body": """Hi {first_name},

I've reached out a few times about your {city} property, and I understand if the timing isn't right.

That said, I work with homeowners in all kinds of situations - some want top dollar on the open market, others prefer a quick, private sale. There's no one-size-fits-all approach.

If you'd ever like to explore what makes sense for your situation, I'm here."""
    },
    5: {
        "subject": "Checking in - {city} property",
        "body": """Hi {first_name},

Just a quick note to see if anything has changed with your plans for {street}.

I'm still happy to help if you're exploring your options. No pressure, just keeping the door open."""
    },
    6: {
        "subject": "One more thought on {street}",
        "body": """Hi {first_name},

I know I've reached out several times, and I appreciate your patience.

If selling isn't on your radar right now, that's completely fine. But if circumstances change, my offer to help stands.

Wishing you all the best,"""
    },
    7: {
        "subject": "Market update for {city}",
        "body": """Hi {first_name},

I wanted to share a quick update on the {city} market - homes similar to yours on {street} have been getting solid interest lately.

If you've been on the fence about exploring your options, now might be a good time to at least see where you stand.

Happy to chat whenever works for you."""
    },
    8: {
        "subject": "Last note from me - {street}",
        "body": """Hi {first_name},

This will be my last email about your {city} property. I don't want to be a bother.

If you ever decide to explore selling, my info is below. I'd be honored to help when the time is right.

Take care,"""
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
        resp = requests.get(CRM_API, headers=CRM_HEADERS, timeout=30)
        resp.raise_for_status()
        clients = resp.json()
        
        # Filter for lis pendens leads (source = "lis_pendens" or "pre-foreclosure")
        leads = [c for c in clients if c.get("source") in ["lis_pendens", "pre-foreclosure", "lis-pendens"]]
        return leads
    except Exception as e:
        print(f"Error fetching leads: {e}")
        return []


def send_email(lead, template_num):
    """Send HTML email via Gmail SMTP with embedded headshot signature"""
    first_name = lead.get("firstName", "there")
    email = lead.get("email")
    street = lead.get("address", "your property")
    city = lead.get("city", "your area")

    if not email:
        return False, "No email"

    template = EMAIL_TEMPLATES.get(template_num, EMAIL_TEMPLATES[1])
    subject = template["subject"].format(first_name=first_name, street=street, city=city)
    body = template["body"].format(first_name=first_name, street=street, city=city)

    msg = MIMEMultipart("related")
    msg['From'] = f"Jack Sullivan <{EMAIL_SENDER}>"
    msg['To'] = email
    msg['Cc'] = CC_EMAIL
    msg['Subject'] = subject

    msg_alt = MIMEMultipart("alternative")
    msg.attach(msg_alt)
    msg_alt.attach(MIMEText(text_to_html(body), 'html'))

    with open(HEADSHOT_PATH, "rb") as f:
        img = MIMEImage(f.read())
        img.add_header("Content-ID", "<jackphoto>")
        img.add_header("Content-Disposition", "inline", filename="jack.jpg")
        msg.attach(img)

    try:
        ctx = ssl.create_default_context()
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30)
        server.ehlo()
        server.starttls(context=ctx)
        server.ehlo()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"  EMAIL to {email}: {subject}")
        return True, "Sent"
    except Exception as e:
        return False, str(e)


def send_sms(lead, template_num):
    """Send SMS via Quo/OpenPhone API"""
    first_name = lead.get("firstName", "there")
    phone = lead.get("phone")
    street = lead.get("address", "your property")
    city = lead.get("city", "your area")
    
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
