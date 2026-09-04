#!/usr/bin/env python3
"""
Fly In Absentee 15-Touch Cadence Runner v2
- Max 30 SMS/day to avoid carrier filtering
- Queues messages for spaced delivery
- Content variation to avoid spam detection
- Delivery status checking
"""

import json
import csv
import os
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from pathlib import Path
import time
import random

# Configuration
CAMPAIGN_DIR = Path(__file__).parent
LEADS_FILE = CAMPAIGN_DIR / "leads.csv"
CADENCE_FILE = CAMPAIGN_DIR / "cadence.json"
TEMPLATES_DIR = CAMPAIGN_DIR / "templates"
LOG_FILE = CAMPAIGN_DIR / "run.log"
QUEUE_FILE = CAMPAIGN_DIR / "sms_queue.json"
DAILY_STATS_FILE = CAMPAIGN_DIR / "daily_stats.json"

# Limits
MAX_SMS_PER_DAY = 30
MAX_EMAILS_PER_DAY = 50
SMS_SPACING_SECONDS = 900  # 15 minutes between SMS

# Email config
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "jack@thehooverhometeam.com"
EMAIL_PASSWORD = "rpwg sdna xtgp fujn"
CC_EMAIL = "ch@thehooverhometeam.com"

# Quo/OpenPhone SMS config
QUO_API_URL = "https://api.openphone.com/v1/messages"
QUO_API_KEY = "<REDACTED:CREDENTIAL>"
QUO_PHONE = "+13862733460"

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
    
    # Always replace basic placeholders
    result = result.replace("{first_name}", first_name)
    result = result.replace("{last_name}", lead.get("last_name", ""))
    result = result.replace("{property_address}", lead.get("property_address", "your property"))
    result = result.replace("{email}", lead.get("email", ""))
    
    # For SMS, add random variations to avoid spam detection
    if vary_content or "{greeting}" in result or "{opener}" in result:
        greeting = random.choice(GREETING_VARS)
        opener = random.choice(OPENER_VARS)
        closer = random.choice(CLOSER_VARS)
        
        result = result.replace("{greeting}", greeting)
        result = result.replace("{opener}", opener)
        result = result.replace("{closer}", closer)
    
    return result

def send_email(to_email, subject, body):
    """Send email via Gmail SMTP"""
    try:
        msg = MIMEMultipart()
        msg['From'] = f"Jack Sullivan <{EMAIL_ADDRESS}>"
        msg['To'] = to_email
        msg['Cc'] = CC_EMAIL
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            recipients = [to_email, CC_EMAIL]
            server.sendmail(EMAIL_ADDRESS, recipients, msg.as_string())
        
        return True, None
    except Exception as e:
        log(f"EMAIL ERROR: {e}")
        return False, str(e)

def send_sms(to_phone, message):
    """Send SMS via Quo/OpenPhone API and verify delivery"""
    try:
        # Format phone number
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

def check_sms_delivery(msg_id):
    """Check delivery status of a sent SMS"""
    try:
        headers = {"Authorization": QUO_API_KEY}
        response = requests.get(f"{QUO_API_URL}/{msg_id}", headers=headers, timeout=30)
        if response.status_code == 200:
            data = response.json()
            return data.get('data', {}).get('status', 'unknown')
        return 'unknown'
    except:
        return 'unknown'

def get_due_touch(lead, cadence):
    """Determine if lead is due for a touch today"""
    current_touch = lead['current_touch']
    start_date_str = lead.get('start_date', lead.get('created', ''))
    
    if not start_date_str:
        return None
    
    try:
        start_date = datetime.strptime(start_date_str[:10], "%Y-%m-%d")
    except:
        return None
    
    today = datetime.now().date()
    touches = cadence['touches']
    next_touch_num = current_touch + 1
    
    if next_touch_num > len(touches):
        return None
    
    next_touch = touches[next_touch_num - 1]
    touch_day = next_touch['day']
    due_date = (start_date + timedelta(days=touch_day)).date()
    
    if due_date <= today:
        return next_touch
    
    return None

def run_cadence():
    log("=" * 60)
    log("Fly In Absentee 15-Touch Cadence Runner v2")
    log("=" * 60)
    
    cadence = load_cadence()
    leads = load_leads()
    stats = load_daily_stats()
    
    log(f"Total leads: {len(leads)}")
    log(f"Daily stats: {stats['sms_sent']} SMS, {stats['emails_sent']} emails sent today")
    
    emails_sent = 0
    sms_sent = 0
    sms_queued = 0
    errors = 0
    
    for lead in leads:
        # Check daily limits
        if stats['sms_sent'] >= MAX_SMS_PER_DAY and stats['emails_sent'] >= MAX_EMAILS_PER_DAY:
            log("Daily limits reached. Stopping.")
            break
        
        has_email = bool(lead.get('email', '').strip())
        has_phone = bool(lead.get('phone', '').strip())
        
        if not has_email and not has_phone:
            continue
        
        if lead.get('status') == 'replied':
            continue
        
        due_touch = get_due_touch(lead, cadence)
        if not due_touch:
            continue
        
        touch_type = due_touch['type']
        template_name = due_touch['template']
        touch_num = due_touch['touch']
        
        template = load_template(template_name)
        
        success = False
        
        if touch_type == 'email' and has_email:
            if stats['emails_sent'] >= MAX_EMAILS_PER_DAY:
                continue
                
            content = personalize(template, lead, vary_content=False)
            lines = content.split('\n')
            subject = lines[0].replace('SUBJECT:', '').strip()
            body = '\n'.join(lines[2:]).strip()
            
            log(f"Sending email #{touch_num} to {lead['first_name']} {lead['last_name']} ({lead['email']})")
            success, error = send_email(lead['email'], subject, body)
            
            if success:
                emails_sent += 1
                stats['emails_sent'] += 1
            else:
                errors += 1
            
            time.sleep(random.uniform(5, 10))
            
        elif touch_type == 'sms' and has_phone:
            if stats['sms_sent'] >= MAX_SMS_PER_DAY:
                sms_queued += 1
                continue
            
            content = personalize(template, lead, vary_content=True)
            
            log(f"Sending SMS #{touch_num} to {lead['first_name']} {lead['last_name']} ({lead['phone']})")
            success, result = send_sms(lead['phone'], content)
            
            if success:
                sms_sent += 1
                stats['sms_sent'] += 1
                
                # Wait and check delivery
                time.sleep(5)
                if result and result.get('id'):
                    delivery_status = check_sms_delivery(result['id'])
                    log(f"  -> Delivery status: {delivery_status}")
                    if delivery_status == 'undelivered':
                        log(f"  -> WARNING: Message undelivered!")
                        errors += 1
                        success = False
            else:
                errors += 1
            
            # Long delay between SMS
            time.sleep(SMS_SPACING_SECONDS)
        
        if success:
            lead['current_touch'] = touch_num
            lead['last_touch_date'] = datetime.now().isoformat()
    
    save_leads(leads)
    save_daily_stats(stats)
    
    log("-" * 60)
    log(f"Emails sent: {emails_sent}")
    log(f"SMS sent: {sms_sent}")
    log(f"SMS queued (over limit): {sms_queued}")
    log(f"Errors: {errors}")
    log("=" * 60)
    
    return {
        "emails_sent": emails_sent,
        "sms_sent": sms_sent,
        "sms_queued": sms_queued,
        "errors": errors
    }

if __name__ == "__main__":
    run_cadence()
