#!/usr/bin/env python3
"""
Fly In Absentee Owners Campaign
Send follow-up emails after Chris's calls and load to CRM
NO DASHES in emails
"""

import csv
import json
import smtplib
import requests
import time
import random
import re
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Config
CSV_FILE = '/root/.openclaw/media/inbound/file_15---ecc47a2c-cd8c-45cf-9c2f-6dfa9328d796.csv'
CAMPAIGN_FILE = '/root/.openclaw/workspace-jack-sullivan/leads/flyin-campaign.json'
CRM_API = 'https://clientlist.onrender.com/api/clients'

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = "jack@thehooverhometeam.com"
EMAIL_PASSWORD = "rpwg sdna xtgp fujn"
EMAIL_CC = "ch@thehooverhometeam.com"

# Email template - follow up after phone call - NO DASHES
EMAIL_TEMPLATE = {
    "subject": "Following up on my call about your Fly In property",
    "body": """Hi {first_name},

Chris Hoover just tried giving you a call and left a voicemail about your property at {address}.

I wanted to follow up here in case email works better for you.

Chris works with a lot of homeowners in the Fly In community and was curious if you've ever considered selling your home there. No pressure at all, just reaching out to see if it's something worth a conversation.

Feel free to reply here or give Chris a call directly at (386) 273-3460.

Best,
Jack Sullivan
Lead Intelligence Specialist
The Hoover Home Team powered by REAL LLC"""
}


def clean_phone(phone):
    """Clean phone number to digits only"""
    if not phone:
        return ""
    return re.sub(r'[^\d]', '', phone)


def load_csv():
    """Load and parse CSV file"""
    leads = []
    with open(CSV_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Skip empty rows
            first_name = row.get('First Name', '').strip()
            last_name = row.get('Last Name', '').strip()
            if not first_name and not last_name:
                continue
            
            lead = {
                'property_address': row.get('Address', '').strip(),
                'first_name': first_name,
                'last_name': last_name,
                'email': row.get('Email', '').strip(),
                'phone': clean_phone(row.get('Phone 1', '')),
                'phone2': clean_phone(row.get('Phone 2', '')),
                'mailing_state': row.get('Mailing Addess', '').strip(),
                'source': 'flyin-absentee',
                'status': 'active',
                'current_touch': 0,
                'created': datetime.now().strftime('%Y-%m-%d')
            }
            leads.append(lead)
    return leads


def add_to_crm(lead):
    """Add lead to CRM"""
    try:
        payload = {
            'name': f"{lead['first_name']} {lead['last_name']}".strip(),
            'email': lead.get('email', ''),
            'phone': lead.get('phone', ''),
            'address': lead.get('property_address', ''),
            'source': 'Fly In Absentee',
            'status': 'New Lead',
            'notes': f"Mailing State: {lead.get('mailing_state', '')}"
        }
        
        resp = requests.post(CRM_API, json=payload, timeout=30)
        if resp.status_code in [200, 201]:
            return True, resp.json().get('id', 'unknown')
        return False, f"HTTP {resp.status_code}"
    except Exception as e:
        return False, str(e)


def send_email(lead):
    """Send follow-up email"""
    if not lead.get('email'):
        return False, "No email"
    
    address = lead.get('property_address', 'your Fly In property')
    
    subject = EMAIL_TEMPLATE['subject']
    body = EMAIL_TEMPLATE['body'].format(
        first_name=lead.get('first_name', 'there'),
        address=address
    )
    
    msg = MIMEMultipart()
    msg['From'] = "Jack Sullivan <jack@thehooverhometeam.com>"
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
    print("=" * 60)
    print("FLY IN ABSENTEE CAMPAIGN")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60 + "\n")
    
    # Load leads
    leads = load_csv()
    print(f"Loaded {len(leads)} leads from CSV\n")
    
    # Stats
    crm_added = 0
    crm_failed = 0
    emails_sent = 0
    emails_skipped = 0
    emails_failed = 0
    
    # Process each lead
    for lead in leads:
        name = f"{lead['first_name']} {lead['last_name']}".strip()
        
        # Add to CRM
        success, result = add_to_crm(lead)
        if success:
            lead['crm_id'] = result
            crm_added += 1
            print(f"  + CRM: {name}")
        else:
            crm_failed += 1
            print(f"  x CRM: {name} ({result})")
        
        # Send email if has address
        if lead.get('email'):
            success, msg = send_email(lead)
            if success:
                lead['current_touch'] = 1
                lead['last_touch_date'] = datetime.now().isoformat()
                emails_sent += 1
                print(f"  + Email: {name}")
            else:
                emails_failed += 1
                print(f"  x Email: {name} ({msg})")
            
            # Delay between emails
            time.sleep(random.uniform(3, 5))
        else:
            emails_skipped += 1
    
    # Save campaign file
    campaign = {
        'name': 'flyin-absentee',
        'created': datetime.now().strftime('%Y-%m-%d'),
        'leads': leads
    }
    with open(CAMPAIGN_FILE, 'w') as f:
        json.dump(campaign, f, indent=2)
    
    print(f"\n{'=' * 60}")
    print("RESULTS")
    print(f"  CRM: {crm_added} added, {crm_failed} failed")
    print(f"  Email: {emails_sent} sent, {emails_skipped} no email, {emails_failed} failed")
    print(f"  Campaign saved: {CAMPAIGN_FILE}")
    print("=" * 60)
    
    return {
        'crm_added': crm_added,
        'emails_sent': emails_sent,
        'emails_skipped': emails_skipped
    }


if __name__ == "__main__":
    main()
