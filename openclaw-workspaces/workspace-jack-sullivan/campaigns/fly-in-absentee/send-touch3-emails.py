#!/usr/bin/env python3
"""
Send Touch 3 emails (skipping Touch 2 SMS due to delivery issues)
Paced: 50 emails max, 5 min spacing
"""

import csv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path
import time
import random
import sys

CAMPAIGN_DIR = Path(__file__).parent
LEADS_FILE = CAMPAIGN_DIR / "leads.csv"
TEMPLATES_DIR = CAMPAIGN_DIR / "templates"
LOG_FILE = CAMPAIGN_DIR / "touch3_run.log"

# Limits
MAX_EMAILS = int(sys.argv[1]) if len(sys.argv) > 1 else 50
EMAIL_SPACING = 300  # 5 minutes

# Email config
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "jack@thehooverhometeam.com"
EMAIL_PASSWORD = "rpwg sdna xtgp fujn"
CC_EMAIL = "ch@thehooverhometeam.com"

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

def load_template():
    with open(TEMPLATES_DIR / "email_02.txt") as f:
        return f.read()

def personalize(template, lead):
    result = template
    first_name = lead.get("first_name", "there")
    if not first_name or first_name.strip() == "":
        first_name = "there"
    result = result.replace("{first_name}", first_name)
    result = result.replace("{last_name}", lead.get("last_name", ""))
    result = result.replace("{property_address}", lead.get("property_address", "your property"))
    return result

def send_email(to_email, subject, body):
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
            server.sendmail(EMAIL_ADDRESS, [to_email, CC_EMAIL], msg.as_string())
        return True
    except Exception as e:
        log(f"EMAIL ERROR: {e}")
        return False

def main():
    log("=" * 60)
    log("Touch 3 Email Batch (Skipping Touch 2 SMS)")
    log(f"Max emails: {MAX_EMAILS}, Spacing: {EMAIL_SPACING}s")
    log("=" * 60)
    
    leads = load_leads()
    template = load_template()
    
    # Find leads at touch 1 with email
    eligible = [l for l in leads if l['current_touch'] == 1 and l.get('email', '').strip()]
    log(f"Eligible leads (touch 1 with email): {len(eligible)}")
    
    sent = 0
    errors = 0
    
    for lead in eligible:
        if sent >= MAX_EMAILS:
            log(f"Reached daily limit ({MAX_EMAILS}). Stopping.")
            break
        
        content = personalize(template, lead)
        lines = content.split('\n')
        subject = lines[0].replace('SUBJECT:', '').strip()
        body = '\n'.join(lines[2:]).strip()
        
        log(f"Sending to {lead['first_name']} {lead['last_name']} ({lead['email']})")
        
        if send_email(lead['email'], subject, body):
            sent += 1
            # Update lead: skip touch 2, mark as touch 3
            lead['current_touch'] = 3
            lead['last_touch_date'] = datetime.now().isoformat()
        else:
            errors += 1
        
        if sent < MAX_EMAILS and sent < len(eligible):
            log(f"  Waiting {EMAIL_SPACING}s before next...")
            time.sleep(EMAIL_SPACING)
    
    save_leads(leads)
    
    log("-" * 60)
    log(f"Emails sent: {sent}")
    log(f"Errors: {errors}")
    log(f"Remaining: {len(eligible) - sent}")
    log("=" * 60)

if __name__ == "__main__":
    main()
