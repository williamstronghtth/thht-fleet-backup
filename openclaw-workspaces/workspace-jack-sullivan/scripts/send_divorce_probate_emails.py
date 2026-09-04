#!/usr/bin/env python3
"""
Divorce/Probate Email Outreach - Week 1 Warmup (8 emails)
Sends personalized emails, CCs Chris, updates CRM, logs activity
"""

import smtplib
import ssl
import time
import json
import requests
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone

def log(msg):
    print(msg, flush=True)

# Config
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_FROM = "jack@thehooverhometeam.com"
EMAIL_PASSWORD = "rpwg sdna xtgp fujn"
CC_EMAIL = "ch@thehooverhometeam.com"
CRM_BASE = "https://clientlist.onrender.com/api/clients"

# Leads to email (first 8 uncontacted)
LEADS = [
    {"id": "mlvehs363depv", "firstName": "Judith Elizabeth", "lastName": "Augustine", "email": "freelance7@gmail.com", "type": "PROBATE", "address": "96 CUNNINGHAM DR, NEW SMYRNA BEACH, FL 32168"},
    {"id": "mlvehs59ppwlt", "firstName": "Cesar Antonio", "lastName": "Escobar", "email": "cesardeltona46@gmail.com", "type": "DIVORCE", "address": "950 DENALI DR, ORANGE CITY, FL 32763"},
    {"id": "mlvehs6se8icw", "firstName": "Maria T", "lastName": "Mercado", "email": "papimerc@hotmail.com", "type": "DIVORCE", "address": "943 FALLBROOKE AVE, DELTONA, FL 32725"},
    {"id": "mlvehs9mkt5h7", "firstName": "Carmen Milagros", "lastName": "Stryzak", "email": "cmstryzak1@gmail.com", "type": "DIVORCE", "address": "926 CLOVER ST, DELAND, FL 32720"},
    {"id": "mlvehsbix9q6e", "firstName": "Adam James", "lastName": "Stone", "email": "lugrox@aol.com", "type": "DIVORCE", "address": "923 GLAZEBROOK LOOP, ORANGE CITY, FL 32763"},
    {"id": "mlvehsepwhtwv", "firstName": "Ian Christopher", "lastName": "Anderson", "email": "conet5@aol.com", "type": "PROBATE", "address": "920 RIVERSIDE DR, HOLLY HILL, FL 32117"},
    {"id": "mlvehshmlbbzu", "firstName": "Joseph Gabriel", "lastName": "Peters", "email": "jgpeters50@yahoo.com", "type": "DIVORCE", "address": "915 CORAL REEF WAY, DAYTONA BEACH, FL 32114"},
    {"id": "mlvehsj39c18i", "firstName": "Amanda Michelle", "lastName": "Gillaspie", "email": "a__smith26@hotmail.com", "type": "DIVORCE", "address": "9 W HIGHBANKS RD, DEBARY, FL 32713"},
]

SIGNATURE = """
Jack Sullivan
Lead Intelligence Specialist
The Hoover Home Team powered by REAL LLC
"""

def get_email_content(lead):
    first_name = lead["firstName"].split()[0]  # Get just first name
    
    if lead["type"] == "DIVORCE":
        subject = f"{first_name}, a quick note about your property"
        body = f"""Hi {first_name},

I hope this message finds you well. I understand you may be navigating some life changes right now, and I wanted to reach out with a quick thought.

If you're considering your options for your property at {lead['address']}, I'd be happy to provide a no-pressure market analysis. Sometimes it helps to simply know where things stand — whether you're thinking of selling now, later, or just want to understand your equity position.

No rush, no obligation. Just here if you'd like to chat.

Wishing you all the best,
{SIGNATURE}
"""
    else:  # PROBATE
        subject = f"Thinking of you - {lead['address'].split(',')[0]}"
        body = f"""Hi {first_name},

I wanted to reach out with my condolences and let you know I'm here if you need any assistance with the property at {lead['address']}.

Handling an inherited property can feel overwhelming, especially during an already difficult time. If you'd like a straightforward conversation about your options — whether that's selling, renting, or simply understanding the property's current value — I'm happy to help however I can.

No pressure, just a resource whenever you're ready.

Take care,
{SIGNATURE}
"""
    return subject, body

def send_email(lead):
    subject, body = get_email_content(lead)
    
    msg = MIMEMultipart()
    msg['From'] = EMAIL_FROM
    msg['To'] = lead['email']
    msg['Cc'] = CC_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    context = ssl.create_default_context()
    
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls(context=context)
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.sendmail(EMAIL_FROM, [lead['email'], CC_EMAIL], msg.as_string())
    
    return True

def update_crm(lead):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    # Get current lead data
    resp = requests.get(f"{CRM_BASE}/{lead['id']}")
    current = resp.json()
    
    # Update notes
    new_notes = current.get('notes', '') + f"\n[{today}] Email Touch 1 sent"
    
    # Update the lead
    requests.put(f"{CRM_BASE}/{lead['id']}", json={
        "notes": new_notes.strip(),
        "lastActivity": today
    })
    
    # Log activity
    requests.post(f"{CRM_BASE}/{lead['id']}/activity", json={
        "action": "Email Sent",
        "details": f"Touch 1 - {lead['type']} outreach email sent. CC: {CC_EMAIL}"
    })

def main():
    log(f"Starting email campaign: {len(LEADS)} leads")
    log(f"CC on all emails: {CC_EMAIL}")
    log("-" * 50)
    
    sent_count = 0
    errors = []
    
    for i, lead in enumerate(LEADS):
        try:
            log(f"\n[{i+1}/{len(LEADS)}] Sending to {lead['firstName']} {lead['lastName']} ({lead['email']})...")
            log(f"  Type: {lead['type']}")
            
            send_email(lead)
            log(f"  ✓ Email sent successfully")
            
            update_crm(lead)
            log(f"  ✓ CRM updated")
            
            sent_count += 1
            
            # Wait 5-6 minutes before next email (except last one)
            if i < len(LEADS) - 1:
                wait_time = 330  # 5.5 minutes
                log(f"  Waiting {wait_time//60}m {wait_time%60}s before next email...")
                time.sleep(wait_time)
                
        except Exception as e:
            error_msg = f"{lead['firstName']} {lead['lastName']}: {str(e)}"
            errors.append(error_msg)
            log(f"  ✗ ERROR: {e}")
    
    log("\n" + "=" * 50)
    log(f"CAMPAIGN COMPLETE")
    log(f"  Emails sent: {sent_count}/{len(LEADS)}")
    log(f"  CC confirmed: {CC_EMAIL} on all emails")
    if errors:
        log(f"  Errors: {len(errors)}")
        for e in errors:
            log(f"    - {e}")
    else:
        log(f"  Errors: None")
    log("=" * 50)

if __name__ == "__main__":
    main()
