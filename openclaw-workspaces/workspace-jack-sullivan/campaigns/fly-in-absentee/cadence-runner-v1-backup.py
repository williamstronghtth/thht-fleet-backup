#!/usr/bin/env python3
"""
Fly In Absentee 15-Touch Cadence Runner
Runs daily at 9am ET to execute due touches
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
    fieldnames = leads[0].keys()
    with open(LEADS_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(leads)

def load_template(template_name):
    template_path = TEMPLATES_DIR / template_name
    with open(template_path) as f:
        return f.read()

def personalize(template, lead):
    """Replace placeholders with lead data"""
    result = template
    result = result.replace("{first_name}", lead.get("first_name", "there"))
    result = result.replace("{last_name}", lead.get("last_name", ""))
    result = result.replace("{property_address}", lead.get("property_address", "your property"))
    result = result.replace("{email}", lead.get("email", ""))
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
        
        return True
    except Exception as e:
        log(f"EMAIL ERROR: {e}")
        return False

def send_sms(to_phone, message):
    """Send SMS via Quo/OpenPhone API"""
    try:
        # Format phone number
        phone = to_phone.strip()
        if not phone.startswith("+"):
            if not phone.startswith("1"):
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
            return True
        else:
            log(f"SMS ERROR: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        log(f"SMS ERROR: {e}")
        return False

def get_due_touch(lead, cadence):
    """Determine if lead is due for a touch today"""
    current_touch = lead['current_touch']
    start_date_str = lead.get('start_date', lead.get('created', ''))
    last_touch_str = lead.get('last_touch_date', '')
    
    if not start_date_str:
        return None
    
    # Parse start date
    try:
        start_date = datetime.strptime(start_date_str[:10], "%Y-%m-%d")
    except:
        return None
    
    today = datetime.now().date()
    
    # Find next touch
    touches = cadence['touches']
    next_touch_num = current_touch + 1
    
    if next_touch_num > len(touches):
        return None  # Cadence complete
    
    next_touch = touches[next_touch_num - 1]
    touch_day = next_touch['day']
    due_date = (start_date + timedelta(days=touch_day)).date()
    
    if due_date <= today:
        return next_touch
    
    return None

def run_cadence():
    log("=" * 60)
    log("Fly In Absentee 15-Touch Cadence Runner")
    log("=" * 60)
    
    cadence = load_cadence()
    leads = load_leads()
    
    log(f"Total leads: {len(leads)}")
    
    emails_sent = 0
    sms_sent = 0
    errors = 0
    
    for lead in leads:
        # Skip if no email and no phone
        has_email = bool(lead.get('email', '').strip())
        has_phone = bool(lead.get('phone', '').strip())
        
        if not has_email and not has_phone:
            continue
        
        # Check if paused (replied)
        if lead.get('status') == 'replied':
            continue
        
        due_touch = get_due_touch(lead, cadence)
        if not due_touch:
            continue
        
        touch_type = due_touch['type']
        template_name = due_touch['template']
        touch_num = due_touch['touch']
        
        template = load_template(template_name)
        content = personalize(template, lead)
        
        success = False
        
        if touch_type == 'email' and has_email:
            # Extract subject from template
            lines = content.split('\n')
            subject = lines[0].replace('SUBJECT:', '').strip()
            body = '\n'.join(lines[2:]).strip()
            
            log(f"Sending email #{touch_num} to {lead['first_name']} {lead['last_name']} ({lead['email']})")
            success = send_email(lead['email'], subject, body)
            
            if success:
                emails_sent += 1
            else:
                errors += 1
                
            # Delay between emails
            time.sleep(random.uniform(5, 10))
            
        elif touch_type == 'sms' and has_phone:
            log(f"Sending SMS #{touch_num} to {lead['first_name']} {lead['last_name']} ({lead['phone']})")
            success = send_sms(lead['phone'], content)
            
            if success:
                sms_sent += 1
            else:
                errors += 1
                
            # Delay between SMS
            time.sleep(random.uniform(2, 5))
        
        if success:
            lead['current_touch'] = touch_num
            lead['last_touch_date'] = datetime.now().isoformat()
    
    # Save updated leads
    save_leads(leads)
    
    log("-" * 60)
    log(f"Emails sent: {emails_sent}")
    log(f"SMS sent: {sms_sent}")
    log(f"Errors: {errors}")
    log("=" * 60)
    
    return {
        "emails_sent": emails_sent,
        "sms_sent": sms_sent,
        "errors": errors
    }

if __name__ == "__main__":
    run_cadence()
