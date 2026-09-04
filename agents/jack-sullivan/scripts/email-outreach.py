#!/usr/bin/env python3
"""
Email Outreach System for The Hoover Home Team
- 4-touch sequence (Day 0, 3, 7, 14)
- Spaced sends (5-6 min apart)
- Domain warmup (30-50/day initially)
- CRM integration
"""

import os
import sys
import json
import time
import random
import smtplib
import requests
from datetime import datetime, timedelta
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

# Load shared secrets from /root/agents/.env (no hardcoded credentials in source)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from secrets_loader import require

# Config
CRM_BASE = "https://clientlist.onrender.com/api"
CRM_API_KEY = require("CRM_API_KEY")
CRM_HEADERS = {'X-API-Key': CRM_API_KEY}
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL = "jack@thehooverhometeam.com"
PASSWORD = require("JACK_EMAIL_APP_PASSWORD")
CC = "ch@thehooverhometeam.com"

# Daily limits (warmup phase)
DAILY_LIMIT = 40  # Week 1: 30-50
BATCH_SIZE = 10   # Per 2-hour window during warmup
SEND_SPACING_MIN = 300  # 5 minutes in seconds
SEND_SPACING_MAX = 420  # 7 minutes in seconds

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

# Email templates
TEMPLATES = {
    "DIVORCE": {
        1: {
            "subject": "Quick question about your {city} property",
            "body": """Hi {first_name},

I help homeowners in {city} who are navigating life changes and considering their options. I know this can be a busy time, so I'll keep this brief.

If selling your property is something you're thinking about — even just exploring — I'd be happy to share what the market looks like right now for your area. No pressure, no commitment.

Would you be open to a quick conversation?"""
        },
        2: {
            "subject": "Market update for {city}",
            "body": """Hi {first_name},

I wanted to follow up and share something that might be useful.

Properties in {city} have been moving lately, and I've been helping several homeowners in similar situations get clarity on their options.

If timing is something you're thinking about, I'm happy to run some numbers for your property — no strings attached.

Worth a quick call?"""
        },
        3: {
            "subject": "Thought of you",
            "body": """Hi {first_name},

I was working with another homeowner in {city} this week who was in a similar situation — not sure whether to sell, rent, or hold.

We mapped out their options together, and it helped them make a decision they felt good about.

If you'd find that kind of conversation helpful, I'm here. Just reply and we can set up a time."""
        },
        4: {
            "subject": "Last note from me",
            "body": """Hi {first_name},

I've reached out a few times, so I'll keep this short — I don't want to be a bother.

If your situation has changed or you're ready to explore your options, my door is always open. Just reply to this email.

Wishing you all the best either way."""
        }
    },
    "PROBATE": {
        1: {
            "subject": "Inherited property in {city}?",
            "body": """Hi {first_name},

I'm Jack with The Hoover Home Team. We specialize in helping families with inherited properties here in Volusia County.

I know this can be an overwhelming time, and dealing with property decisions on top of everything else isn't easy.

If you're exploring your options — whether that's selling, renting, or just understanding what the property is worth — I'm happy to help.

No pressure at all. Would a quick conversation be helpful?"""
        },
        2: {
            "subject": "A few options for inherited properties",
            "body": """Hi {first_name},

Following up on my note from a few days ago.

When families inherit property, there are usually a few paths: sell quickly, hold and rent, or do some updates first. Each has pros and cons depending on your situation.

If you'd like, I can walk you through what makes sense for your specific property. No obligation.

Worth a quick call?"""
        },
        3: {
            "subject": "Helped a family in {city} last week",
            "body": """Hi {first_name},

I was working with a family last week who inherited a property and wasn't sure what to do with it. They were out of state and didn't want to deal with managing it remotely.

We worked through their options together and found a solution that worked for them.

If you're in a similar spot, I'm happy to help you think through it."""
        },
        4: {
            "subject": "Just checking in one last time",
            "body": """Hi {first_name},

I've reached out a few times, so this will be my last note for now.

If things change or you'd like to talk through your options for the property in {city}, I'm here. Just reply anytime.

Wishing you and your family all the best."""
        }
    }
}


def get_clients():
    """Fetch all clients from CRM"""
    resp = requests.get(f"{CRM_BASE}/clients", headers=CRM_HEADERS)
    data = resp.json()
    return data.get("clients", [])


def get_lead_type(client):
    """Determine if DIVORCE or PROBATE"""
    notes = (client.get("notes", "") or "").upper()
    if "DIVORCE" in notes:
        return "DIVORCE"
    elif "PROBATE" in notes:
        return "PROBATE"
    return None


def get_touch_number(client):
    """Determine which touch this client is on based on activity log"""
    activities = client.get("activityLog", [])
    email_count = 0
    last_email_date = None
    
    for a in activities:
        details = (a.get("details", "") or "").lower()
        action = (a.get("action", "") or "").lower()
        if "email" in details or "email" in action:
            email_count += 1
            ts = a.get("timestamp", "")
            if ts:
                last_email_date = ts[:10]  # YYYY-MM-DD
    
    return email_count, last_email_date


def days_since(date_str):
    """Calculate days since a date string"""
    if not date_str:
        return 999
    try:
        d = datetime.strptime(date_str[:10], "%Y-%m-%d")
        return (datetime.now() - d).days
    except:
        return 999


def get_city_from_address(address):
    """Extract city from address string"""
    if not address:
        return "your area"
    parts = address.split(",")
    if len(parts) >= 2:
        # Usually: "123 Main St, City, FL 12345"
        city_part = parts[-2].strip() if len(parts) >= 2 else parts[-1]
        # Remove state/zip if present
        city = city_part.split()[0] if city_part else "your area"
        return city_part.strip()
    return "your area"


def send_email(to_email, subject, body):
    """Send HTML email via Gmail SMTP with embedded headshot signature"""
    msg = MIMEMultipart("related")
    msg["From"] = f"Jack Sullivan <{EMAIL}>"
    msg["To"] = to_email
    msg["Cc"] = CC
    msg["Subject"] = subject

    msg_alt = MIMEMultipart("alternative")
    msg.attach(msg_alt)
    msg_alt.attach(MIMEText(text_to_html(body), 'html'))

    with open(HEADSHOT_PATH, "rb") as f:
        img = MIMEImage(f.read())
        img.add_header("Content-ID", "<jackphoto>")
        img.add_header("Content-Disposition", "inline", filename="jack.jpg")
        msg.attach(img)

    import ssl
    ctx = ssl.create_default_context()
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
        server.ehlo()
        server.starttls(context=ctx)
        server.ehlo()
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)


def update_crm(client_id, touch_num):
    """Update CRM with email activity"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Add activity log entry
    activity = {
        "action": "Email Sent",
        "details": f"Touch {touch_num} email sent"
    }
    requests.post(f"{CRM_BASE}/clients/{client_id}/activity", json=activity, headers=CRM_HEADERS)

    # Update notes
    client = requests.get(f"{CRM_BASE}/clients/{client_id}", headers=CRM_HEADERS).json()
    current_notes = client.get("notes", "") or ""
    new_notes = f"{current_notes}\n[{today}] Email Touch {touch_num} sent".strip()
    requests.put(f"{CRM_BASE}/clients/{client_id}", json={"notes": new_notes}, headers=CRM_HEADERS)


def get_ready_leads(clients):
    """Get leads ready for email based on sequence timing"""
    ready = []
    
    for c in clients:
        # Must have email
        if not c.get("email"):
            continue
        
        # Must be DIVORCE or PROBATE
        lead_type = get_lead_type(c)
        if not lead_type:
            continue
        
        email_count, last_email = get_touch_number(c)
        days = days_since(last_email)
        
        # Determine if ready for next touch
        if email_count == 0:
            # Never emailed - ready for Touch 1
            ready.append((c, lead_type, 1))
        elif email_count == 1 and days >= 3:
            # Touch 1 sent 3+ days ago - ready for Touch 2
            ready.append((c, lead_type, 2))
        elif email_count == 2 and days >= 4:
            # Touch 2 sent 4+ days ago - ready for Touch 3 (day 7)
            ready.append((c, lead_type, 3))
        elif email_count == 3 and days >= 7:
            # Touch 3 sent 7+ days ago - ready for Touch 4 (day 14)
            ready.append((c, lead_type, 4))
        # After Touch 4, they go to cold/SMS
    
    return ready


def run_batch(max_sends=None):
    """Run email batch with spacing"""
    if max_sends is None:
        max_sends = BATCH_SIZE
    
    print(f"📧 Email Outreach Batch — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)
    
    clients = get_clients()
    ready = get_ready_leads(clients)
    
    print(f"Total clients: {len(clients)}")
    print(f"Ready for email: {len(ready)}")
    print(f"Batch size: {max_sends}")
    print("-" * 50)
    
    # Prioritize: Touch 1 first (new leads), then follow-ups
    ready.sort(key=lambda x: x[2])  # Sort by touch number
    
    sent = 0
    for client, lead_type, touch_num in ready[:max_sends]:
        first_name = client.get("firstName", "there")
        email = client.get("email")
        address = client.get("address", "")
        city = get_city_from_address(address)
        client_id = client.get("id")
        
        # Get template
        template = TEMPLATES[lead_type][touch_num]
        subject = template["subject"].format(city=city, first_name=first_name)
        body = template["body"].format(
            first_name=first_name,
            city=city
        )
        
        try:
            send_email(email, subject, body)
            update_crm(client_id, touch_num)
            sent += 1
            print(f"✅ {sent}. {first_name} {client.get('lastName', '')} | Touch {touch_num} | {lead_type}")
            
            # Space out sends
            if sent < max_sends and sent < len(ready):
                wait = random.randint(SEND_SPACING_MIN, SEND_SPACING_MAX)
                print(f"   ⏳ Waiting {wait//60}m {wait%60}s...")
                time.sleep(wait)
                
        except Exception as e:
            print(f"❌ Failed: {first_name} — {e}")
    
    print("=" * 50)
    print(f"✅ BATCH COMPLETE: {sent} emails sent")
    return sent


if __name__ == "__main__":
    batch_size = int(sys.argv[1]) if len(sys.argv) > 1 else BATCH_SIZE
    run_batch(batch_size)
