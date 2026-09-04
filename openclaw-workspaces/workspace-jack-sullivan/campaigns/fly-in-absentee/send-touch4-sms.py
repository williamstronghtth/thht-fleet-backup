#!/usr/bin/env python3
import csv, requests, time, random
from datetime import datetime

API_KEY = "<REDACTED:CREDENTIAL>"
MY_NUMBER = "+13862733460"
LEADS_FILE = "leads.csv"
LOG_FILE = "touch4_sms_run.log"

GREETINGS = ["Hi", "Hey", "Hello"]
OPENERS = ["Just checking in —", "Quick follow-up —", ""]
CLOSERS = [
    "Let me know if you'd like more info. Reply STOP to opt out.",
    "Happy to answer any questions. Reply STOP to opt out."
]

MAX_SMS, SPACING = 50, 300

def log(msg):
    line = f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f: f.write(line + "\n")

def build_message(first_name):
    return f"{random.choice(GREETINGS)} {first_name}, {random.choice(OPENERS)} Did you get a chance to see my email about your property in Fly In? {random.choice(CLOSERS)}".replace("  ", " ")

def send_sms(to_number, message):
    return requests.post("https://api.openphone.com/v1/messages",
        json={"from": MY_NUMBER, "to": [to_number], "content": message},
        headers={"Authorization": API_KEY, "Content-Type": "application/json"}).json()

def check_delivery(msg_id):
    time.sleep(10)
    return requests.get(f"https://api.openphone.com/v1/messages/{msg_id}",
        headers={"Authorization": API_KEY}).json().get("data", {}).get("status", "unknown")

def main():
    log("=" * 50)
    log("Touch 4 SMS — Fly In Absentee")
    
    with open(LEADS_FILE, "r") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        leads = list(reader)
    
    eligible = [l for l in leads if l.get("current_touch") == "3" and l.get("status") == "active" and l.get("phone")]
    log(f"Eligible: {len(eligible)}")
    
    sent = delivered = undelivered = errors = 0
    
    for lead in eligible[:MAX_SMS]:
        phone = lead["phone"]
        if not phone.startswith("+"): phone = "+1" + phone.replace("-", "").replace(" ", "")
        
        log(f"Sending to {lead['first_name']} {lead['last_name']} ({phone})")
        
        try:
            result = send_sms(phone, build_message(lead["first_name"]))
            if "data" in result:
                status = check_delivery(result["data"]["id"])
                if status == "delivered":
                    log("  -> ✅ Delivered"); delivered += 1
                    lead["current_touch"] = "4"
                    lead["last_touch_date"] = datetime.now().isoformat()
                else:
                    log(f"  -> ❌ {status}"); undelivered += 1
                sent += 1
            else:
                log(f"  -> ❌ {result}"); errors += 1
        except Exception as e:
            log(f"  -> ❌ {e}"); errors += 1
        
        log(f"  Waiting {SPACING}s...")
        time.sleep(SPACING)
    
    with open(LEADS_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(leads)
    
    log(f"Done: {sent} sent, {delivered} delivered, {undelivered} undelivered, {errors} errors")
    log(f"Remaining: {len(eligible) - sent}")

if __name__ == "__main__": main()
