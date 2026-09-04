#!/usr/bin/env python3
"""
Send Email #2 (Following up) to all active cold calling leads
Skipping SMS touches as requested
"""

import json
import smtplib
import time
import random
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Config
CAMPAIGN_FILE = '/root/.openclaw/workspace-jack-sullivan/leads/cold-calling-campaign.json'
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = "jack@thehooverhometeam.com"
EMAIL_PASSWORD = "rpwg sdna xtgp fujn"
EMAIL_CC = "ch@thehooverhometeam.com"

# Email #2 Template
EMAIL_2 = {
    "subject": "Following up — {address}",
    "body": """Hi {first_name},

Just circling back on my note about your property in {city}.

I know managing a place from out of state can be a lot — whether it's a rental, vacation home, or something you're still figuring out. If you ever want to talk through your options, I'm happy to help.

What's your current situation with the property?

Best,
Chris"""
}


def load_campaign():
    with open(CAMPAIGN_FILE) as f:
        return json.load(f)


def save_campaign(data):
    with open(CAMPAIGN_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def extract_city(address):
    if not address:
        return "your area"
    parts = address.split(',')
    if len(parts) >= 2:
        return parts[-2].strip()
    return "your area"


def send_email(lead):
    if not lead.get('email'):
        return False, "No email"
    
    city = extract_city(lead.get('address', ''))
    address = lead.get('address', 'your property')
    
    subject = EMAIL_2['subject'].format(
        first_name=lead.get('first_name', 'there'),
        city=city,
        address=address
    )
    body = EMAIL_2['body'].format(
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


def main():
    campaign = load_campaign()
    
    print("=" * 60)
    print("SENDING EMAIL #2 (Following up)")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60 + "\n")
    
    sent = 0
    skipped = 0
    failed = 0
    
    for lead in campaign['leads']:
        # Skip if replied or unsubscribed
        if lead.get('replied') or lead.get('status') == 'unsubscribed':
            skipped += 1
            continue
        
        # Skip if no email
        if not lead.get('email'):
            skipped += 1
            continue
        
        # Skip if already got email #2 (current_touch >= 2)
        if lead.get('current_touch', 0) >= 2:
            skipped += 1
            continue
        
        # Must have received email #1
        if lead.get('current_touch', 0) < 1:
            skipped += 1
            continue
        
        name = f"{lead.get('first_name', '')} {lead.get('last_name', '')}".strip()
        
        success, msg = send_email(lead)
        
        if success:
            print(f"  ✓ {name} ({lead['email']})")
            lead['current_touch'] = 2
            lead['last_touch_date'] = datetime.now().isoformat()
            sent += 1
        else:
            print(f"  ✗ {name}: {msg}")
            failed += 1
        
        # Small delay between sends
        time.sleep(random.uniform(3, 6))
    
    # Save updated campaign
    save_campaign(campaign)
    
    print(f"\n{'=' * 60}")
    print(f"RESULTS: {sent} sent, {skipped} skipped, {failed} failed")
    print("=" * 60)
    
    return sent, skipped, failed


if __name__ == "__main__":
    main()
