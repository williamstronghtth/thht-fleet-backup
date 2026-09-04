#!/usr/bin/env python3
"""
Send Touch 2 SMS for Fly In absentee campaign
50/day max, 5 min spacing, content variation, delivery checking
"""

import csv
import requests
import random
import time
import sys
from datetime import datetime
from pathlib import Path

CAMPAIGN_DIR = Path(__file__).parent
LEADS_FILE = CAMPAIGN_DIR / "leads.csv"
TEMPLATES_DIR = CAMPAIGN_DIR / "templates"
LOG_FILE = CAMPAIGN_DIR / "touch2_sms_run.log"

MAX_SMS = int(sys.argv[1]) if len(sys.argv) > 1 else 50
SMS_SPACING = 300  # 5 minutes

QUO_API_URL = "https://api.openphone.com/v1/messages"
QUO_API_KEY = "<REDACTED:CREDENTIAL>"
QUO_PHONE = "+13862733460"

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

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def load_leads():
    leads = []
    with open(LEADS_FILE, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['current_touch'] = int(row['current_touch'])
            leads.append(row)
    return leads

def save_leads(leads):
    fieldnames = list(leads[0].keys())
    with open(LEADS_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(leads)

def personalize_sms(lead):
    with open(TEMPLATES_DIR / "sms_01.txt") as f:
        template = f.read()
    
    first_name = lead.get("first_name", "there").strip()
    if not first_name:
        first_name = "there"
    
    result = template
    result = result.replace("{first_name}", first_name)
    result = result.replace("{property_address}", lead.get("property_address", "your property"))
    result = result.replace("{greeting}", random.choice(GREETING_VARS))
    result = result.replace("{opener}", random.choice(OPENER_VARS))
    result = result.replace("{closer}", random.choice(CLOSER_VARS))
    
    return result

def send_sms(to_phone, message):
    phone = ''.join(filter(str.isdigit, to_phone))
    if len(phone) == 10:
        phone = "1" + phone
    phone = "+" + phone
    
    headers = {"Authorization": QUO_API_KEY, "Content-Type": "application/json"}
    payload = {"from": QUO_PHONE, "to": [phone], "content": message}
    
    try:
        response = requests.post(QUO_API_URL, headers=headers, json=payload, timeout=30)
        if response.status_code in [200, 201, 202]:
            data = response.json()
            msg_id = data.get('data', {}).get('id')
            
            # Check delivery after 10s
            time.sleep(10)
            check = requests.get(f"{QUO_API_URL}/{msg_id}", 
                               headers={"Authorization": QUO_API_KEY}, timeout=30)
            status = check.json().get('data', {}).get('status', 'unknown')
            return True, status, msg_id
        else:
            return False, f"API error: {response.status_code}", None
    except Exception as e:
        return False, str(e), None

def main():
    log("=" * 60)
    log("Touch 2 SMS Batch — Fly In Absentee")
    log(f"Max SMS: {MAX_SMS}, Spacing: {SMS_SPACING}s")
    log("=" * 60)
    
    leads = load_leads()
    
    # Find leads that need Touch 2 SMS (at touch 1 with phone, not bounced)
    eligible = [l for l in leads if l['current_touch'] == 1 
                and l.get('phone', '').strip()
                and l.get('status', 'active') != 'bounced']
    
    log(f"Eligible leads (touch 1 with phone): {len(eligible)}")
    
    sent = 0
    delivered = 0
    undelivered = 0
    errors = 0
    
    for lead in eligible:
        if sent >= MAX_SMS:
            log(f"Reached daily limit ({MAX_SMS}). Stopping.")
            break
        
        message = personalize_sms(lead)
        log(f"Sending to {lead['first_name']} {lead['last_name']} ({lead['phone']})")
        
        success, status, msg_id = send_sms(lead['phone'], message)
        
        if success:
            sent += 1
            if status == 'delivered':
                delivered += 1
                lead['current_touch'] = 2
                lead['last_touch_date'] = datetime.now().isoformat()
                log(f"  -> ✅ Delivered")
            elif status == 'undelivered':
                undelivered += 1
                log(f"  -> ❌ Undelivered")
            else:
                # Sent but status pending — count as success
                delivered += 1
                lead['current_touch'] = 2
                lead['last_touch_date'] = datetime.now().isoformat()
                log(f"  -> Status: {status}")
        else:
            errors += 1
            log(f"  -> ERROR: {status}")
        
        if sent < MAX_SMS and sent < len(eligible):
            log(f"  Waiting {SMS_SPACING}s...")
            time.sleep(SMS_SPACING)
    
    save_leads(leads)
    
    log("-" * 60)
    log(f"SMS sent: {sent}")
    log(f"Delivered: {delivered}")
    log(f"Undelivered: {undelivered}")
    log(f"Errors: {errors}")
    log(f"Remaining: {len(eligible) - sent}")
    log("=" * 60)

if __name__ == "__main__":
    main()
