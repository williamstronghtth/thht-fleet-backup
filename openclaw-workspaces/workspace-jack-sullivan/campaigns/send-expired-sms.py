#!/usr/bin/env python3
"""
Expired Leads SMS - Follow up to cold calls
"""

import csv
import requests
import time
import random
from datetime import datetime

API_KEY = "<REDACTED:CREDENTIAL>"
MY_NUMBER = "+13862733460"

LEADS_FILE = "expired-march-2026.csv"
LOG_FILE = "expired_sms_run.log"

MESSAGES = [
    "Hi {first_name}, this is Chris Hoover following up on our call. I know your listing expired and I'd love to help you get it sold. What questions can I answer for you? Reply STOP to opt out.",
    "Hey {first_name}, Chris Hoover here. Just called about your property. I specialize in selling homes that didn't move the first time. Would love to chat about a fresh approach. Reply STOP to opt out.",
    "Hi {first_name}, Chris from The Hoover Home Team. Following up on my call about your expired listing. I have some ideas on how we can get it sold. Let me know if you'd like to talk. Reply STOP to opt out."
]

SPACING = 60  # 1 min between sends

def log(msg):
    line = f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def send_sms(to_number, message):
    return requests.post("https://api.openphone.com/v1/messages",
        json={"from": MY_NUMBER, "to": [to_number], "content": message},
        headers={"Authorization": API_KEY, "Content-Type": "application/json"}).json()

def check_delivery(msg_id):
    time.sleep(8)
    return requests.get(f"https://api.openphone.com/v1/messages/{msg_id}",
        headers={"Authorization": API_KEY}).json().get("data", {}).get("status", "unknown")

def main():
    log("=" * 50)
    log("Expired Leads SMS Blast")
    log("=" * 50)
    
    with open(LEADS_FILE, "r") as f:
        reader = csv.DictReader(f)
        leads = list(reader)
    
    # Filter leads with phone numbers
    eligible = [l for l in leads if l.get("Phone Number", "").strip()]
    log(f"Leads with phone: {len(eligible)}")
    
    sent = delivered = undelivered = errors = 0
    
    for lead in eligible:
        phone = lead["Phone Number"].replace("(", "").replace(")", "").replace("-", "").replace(" ", "")
        if not phone.startswith("+"):
            phone = "+1" + phone
        
        first_name = lead.get("First Name", "").strip() or "there"
        message = random.choice(MESSAGES).format(first_name=first_name)
        
        log(f"Sending to {first_name} {lead.get('Last Name', '')} ({phone})")
        
        try:
            result = send_sms(phone, message)
            if "data" in result:
                status = check_delivery(result["data"]["id"])
                if status == "delivered":
                    log("  -> ✅ Delivered")
                    delivered += 1
                else:
                    log(f"  -> ❌ {status}")
                    undelivered += 1
                sent += 1
            else:
                log(f"  -> ❌ {result}")
                errors += 1
        except Exception as e:
            log(f"  -> ❌ {e}")
            errors += 1
        
        log(f"  Waiting {SPACING}s...")
        time.sleep(SPACING)
    
    log("-" * 50)
    log(f"Done: {sent} sent, {delivered} delivered, {undelivered} undelivered, {errors} errors")

if __name__ == "__main__":
    main()
