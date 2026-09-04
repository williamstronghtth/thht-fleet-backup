#!/usr/bin/env python3
"""
Fly In Absentee 15-Touch Cadence Runner v3
- HTML emails with Jack's signature and headshot
- Max 30 SMS/day to avoid carrier filtering
- Content variation to avoid spam detection
"""

import json
import csv
import os
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime, timedelta
from pathlib import Path
import time
import random
import sys

# Add scripts directory to path for signature import
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

# Configuration
CAMPAIGN_DIR = Path(__file__).parent
LEADS_FILE = CAMPAIGN_DIR / "leads.csv"
CADENCE_FILE = CAMPAIGN_DIR / "cadence.json"
TEMPLATES_DIR = CAMPAIGN_DIR / "templates"
LOG_FILE = CAMPAIGN_DIR / "run.log"
QUEUE_FILE = CAMPAIGN_DIR / "sms_queue.json"
DAILY_STATS_FILE = CAMPAIGN_DIR / "daily_stats.json"
HEADSHOT_PATH = Path(__file__).parent.parent.parent / "assets" / "jack-headshot.jpg"

# Limits
MAX_SMS_PER_DAY = 30
MAX_EMAILS_PER_DAY = 50
SMS_SPACING_SECONDS = 900  # 15 minutes between SMS

# Email config
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
EMAIL_ADDRESS = "jack@thehooverhometeam.com"
EMAIL_PASSWORD = "<REDACTED:CREDENTIAL>"
CC_EMAIL = "ch@thehooverhometeam.com"

# Quo/OpenPhone SMS config
QUO_API_URL = "https://api.openphone.com/v1/messages"
QUO_API_KEY = "<REDACTED:CREDENTIAL>"
QUO_PHONE = "+13862733460"

# Signature HTML
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

# Content variations to avoid spam filters
GREETING_VARS = ["Hi", "Hey", "Hello"]
OPENER_VARS = [
    "this is Jack from The Hoover Home Team.",
    "Jack here from The Hoover Home Team.",
    "it's Jack with The Hoover Home Team.",
]
CLOSER_VARS = [
    "Let me know if you have any questions!",
    "Happy to chat whenever works for you.",
    "Feel free to reach out anytime.",
    "Just let me know if I can help!",
]

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


def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def load_cadence():
    with open(CADENCE_FILE) as f:
        return json.load(f)

def load_leads():
    leads = []
    if not LEADS_FILE.exists():
        return leads
    with open(LEADS_FILE, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['current_touch'] = int(row['current_touch'])
            leads.append(row)
    return leads

def save_leads(leads):
    if not leads:
        return
    fieldnames = list(leads[0].keys())
    with open(LEADS_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(leads)

def load_daily_stats():
    today = datetime.now().strftime("%Y-%m-%d")
    if DAILY_STATS_FILE.exists():
        with open(DAILY_STATS_FILE) as f:
            stats = json.load(f)
            if stats.get('date') == today:
                return stats
    return {'date': today, 'sms_sent': 0, 'emails_sent': 0}

def save_daily_stats(stats):
    with open(DAILY_STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=2)

def load_template(template_name):
    template_path = TEMPLATES_DIR / template_name
    with open(template_path) as f:
        return f.read()

def personalize(template, lead, vary_content=False):
    """Replace placeholders with lead data, optionally vary content"""
    result = template
    
    first_name = lead.get("first_name", "there")
    if not first_name or first_name.strip() == "":
        first_name = "there"
    
    address = normalize_address(lead.get("property_address", "your property"))

    result = result.replace("{first_name}", first_name)
    result = result.replace("{last_name}", lead.get("last_name", ""))
    result = result.replace("{property_address}", address)
    result = result.replace("{address}", address)
    result = result.replace("{email}", lead.get("email", ""))
    
    if vary_content or "{greeting}" in result or "{opener}" in result:
        greeting = random.choice(GREETING_VARS)
        opener = random.choice(OPENER_VARS)
        closer = random.choice(CLOSER_VARS)
        
        result = result.replace("{greeting}", greeting)
        result = result.replace("{opener}", opener)
        result = result.replace("{closer}", closer)
    
    return result

def text_to_html(text):
    """Convert plain text email body to HTML with signature"""
    # Escape HTML and convert line breaks
    lines = text.strip().split('\n')
    html_lines = []
    for line in lines:
        if line.strip():
            html_lines.append(f"<p style='margin: 0 0 10px 0; font-family: Arial, sans-serif; font-size: 14px; color: #333;'>{line}</p>")
        else:
            html_lines.append("<br>")
    
    body_html = "\n".join(html_lines)
    
    return f"""<html>
<body>
{body_html}
{SIGNATURE_HTML}
</body>
</html>"""

def send_email(to_email, subject, body):
    """Send HTML email with embedded signature"""
    try:
        msg = MIMEMultipart("related")
        msg['From'] = f"Jack Sullivan <{EMAIL_ADDRESS}>"
        msg['To'] = to_email
        msg['Cc'] = CC_EMAIL
        msg['Subject'] = subject
        
        # Create HTML body with signature
        html_body = text_to_html(body)
        
        msg_alt = MIMEMultipart("alternative")
        msg.attach(msg_alt)
        msg_alt.attach(MIMEText(html_body, 'html'))
        
        # Attach headshot
        with open(HEADSHOT_PATH, "rb") as f:
            img = MIMEImage(f.read())
            img.add_header("Content-ID", "<jackphoto>")
            img.add_header("Content-Disposition", "inline", filename="jack.jpg")
            msg.attach(img)
        
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            recipients = [to_email, CC_EMAIL]
            server.send_message(msg)
        
        return True, None
    except Exception as e:
        log(f"EMAIL ERROR: {e}")
        return False, str(e)

def send_sms(to_phone, message):
    """Send SMS via Quo/OpenPhone API"""
    try:
        phone = ''.join(filter(str.isdigit, to_phone))
        if len(phone) == 10:
            phone = "1" + phone
        phone = "+" + phone
        
        headers = {
            "Authorization": QUO_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "from": QUO_PHONE,
            "to": [phone],
            "content": message
        }
        
        response = requests.post(QUO_API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code in [200, 201, 202]:
            data = response.json()
            msg_id = data.get('data', {}).get('id')
            status = data.get('data', {}).get('status', 'unknown')
            return True, {'id': msg_id, 'status': status}
        else:
            log(f"SMS API ERROR: {response.status_code} - {response.text}")
            return False, response.text
    except Exception as e:
        log(f"SMS ERROR: {e}")
        return False, str(e)

def get_touch_config(cadence, touch_num):
    """Get configuration for a specific touch"""
    for touch in cadence['touches']:
        if touch['touch'] == touch_num:
            return touch
    return None

def run_cadence():
    log("=" * 50)
    log("Starting Fly In Cadence Runner v3 (with signature)")
    log("=" * 50)
    
    cadence = load_cadence()
    leads = load_leads()
    stats = load_daily_stats()
    
    log(f"Loaded {len(leads)} leads")
    log(f"Today's stats: {stats['sms_sent']} SMS, {stats['emails_sent']} emails")
    
    today = datetime.now().date()
    emails_sent = 0
    sms_sent = 0
    
    for lead in leads:
        if lead.get('status') != 'active':
            continue
            
        current_touch = lead['current_touch']
        next_touch = current_touch + 1
        
        # Check if we have a next touch
        touch_config = get_touch_config(cadence, next_touch)
        if not touch_config:
            continue
        
        # Skip SMS touches — email-only cadence (Quo credits unavailable)
        if touch_config['type'] == 'sms':
            continue

        # Check if enough days have passed
        last_touch_date_str = lead.get('last_touch_date', '')
        if not last_touch_date_str:
            log(f"Skipping {lead['first_name']} {lead['last_name']} — missing last_touch_date")
            continue
        # Handle both "YYYY-MM-DD" and ISO datetime strings
        last_touch_date = datetime.strptime(last_touch_date_str[:10], "%Y-%m-%d").date()
        days_since = (today - last_touch_date).days

        if days_since < touch_config.get('day_offset', touch_config.get('day', 0)):
            continue

        # Check daily limits
        if touch_config['type'] == 'email' and stats['emails_sent'] >= MAX_EMAILS_PER_DAY:
            log(f"Email limit reached, skipping {lead['first_name']} {lead['last_name']}")
            continue
        
        # Load and personalize template
        template = load_template(touch_config['template'])
        content = personalize(template, lead, vary_content=(touch_config['type'] == 'sms'))
        
        # Send
        if touch_config['type'] == 'email':
            if not lead.get('email'):
                continue
            subject = touch_config.get('subject', 'Following up')
            subject = personalize(subject, lead)
            
            log(f"Sending email touch {next_touch} to {lead['first_name']} {lead['last_name']}")
            success, error = send_email(lead['email'], subject, content)
            
            if success:
                emails_sent += 1
                stats['emails_sent'] += 1
                lead['current_touch'] = next_touch
                lead['last_touch_date'] = today.strftime("%Y-%m-%d")
                log(f"  -> ✅ Email sent")
            else:
                log(f"  -> ❌ Failed: {error}")
                
        elif touch_config['type'] == 'sms':
            if not lead.get('phone'):
                continue
                
            log(f"Sending SMS touch {next_touch} to {lead['first_name']} {lead['last_name']}")
            success, result = send_sms(lead['phone'], content)
            
            if success:
                sms_sent += 1
                stats['sms_sent'] += 1
                lead['current_touch'] = next_touch
                lead['last_touch_date'] = today.strftime("%Y-%m-%d")
                log(f"  -> ✅ SMS sent")
                time.sleep(SMS_SPACING_SECONDS // 60)  # Brief pause
            else:
                log(f"  -> ❌ Failed: {result}")
    
    save_leads(leads)
    save_daily_stats(stats)
    
    log("-" * 50)
    log(f"Done: {emails_sent} emails, {sms_sent} SMS sent today")

if __name__ == "__main__":
    run_cadence()
