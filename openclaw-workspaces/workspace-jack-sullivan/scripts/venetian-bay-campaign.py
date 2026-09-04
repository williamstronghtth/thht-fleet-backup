#!/usr/bin/env python3
"""
Venetian Bay Absentee Owners - Email Campaign
A/B Testing 3 subject lines
"""

import json
import smtplib
import time
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER = "jack@thehooverhometeam.com"
PASSWORD = "rpwg sdna xtgp fujn"
CC = "ch@thehooverhometeam.com"

SIGNATURE = """
Jack Sullivan
Lead Intelligence Specialist
The Hoover Home Team powered by REAL LLC"""

SUBJECT_LINES = {
    'A': 'Quick question about your Venetian Bay property',
    'B': 'Venetian Bay market update — what owners are seeing',
    'C': 'Managing your NSB property from afar?'
}

def create_email(lead, group):
    subject = SUBJECT_LINES[group]
    
    # Personalize based on their state
    state = lead.get('mailing_state', 'out of state')
    
    body = f"""Hi {lead['first_name']},

I'm reaching out to Venetian Bay property owners who live out of state — I know managing a home in Florida from {state} comes with its own set of challenges.

Between rising insurance costs, coordinating maintenance from a distance, and keeping up with the market, a lot of owners I talk to are at least curious about what their options look like right now.

If you've ever wondered what your Venetian Bay property might be worth in today's market, I'd be happy to put together a quick, no-obligation market snapshot. No pressure — just good information to have.

Would that be helpful?

Best,{SIGNATURE}"""
    
    return subject, body


def send_email(lead, group):
    subject, body = create_email(lead, group)
    
    msg = MIMEMultipart()
    msg['From'] = SENDER
    msg['To'] = lead['email']
    msg['Cc'] = CC
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER, PASSWORD)
        server.send_message(msg)
        server.quit()
        return True, None
    except Exception as e:
        return False, str(e)


def run_campaign(dry_run=False):
    with open('/root/.openclaw/workspace-jack-sullivan/leads/venetian-bay-campaign.json') as f:
        campaign = json.load(f)
    
    print(f"{'='*60}")
    print(f"VENETIAN BAY ABSENTEE OWNERS CAMPAIGN")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print(f"Time: {datetime.now()}")
    print(f"{'='*60}\n")
    
    results = {'A': {'sent': 0, 'failed': 0}, 'B': {'sent': 0, 'failed': 0}, 'C': {'sent': 0, 'failed': 0}}
    
    for group in ['A', 'B', 'C']:
        leads = campaign['groups'][group]
        subject = SUBJECT_LINES[group]
        print(f"\n[GROUP {group}] Subject: \"{subject}\"")
        print(f"  Sending to {len(leads)} leads...")
        
        for i, lead in enumerate(leads):
            if dry_run:
                print(f"    [{i+1}/{len(leads)}] [DRY RUN] {lead['email']}")
                results[group]['sent'] += 1
            else:
                success, error = send_email(lead, group)
                if success:
                    print(f"    [{i+1}/{len(leads)}] ✓ {lead['email']}")
                    results[group]['sent'] += 1
                else:
                    print(f"    [{i+1}/{len(leads)}] ✗ {lead['email']} - {error}")
                    results[group]['failed'] += 1
                
                # Space emails 5-7 seconds apart
                if i < len(leads) - 1:
                    time.sleep(random.uniform(5, 7))
    
    print(f"\n{'='*60}")
    print("RESULTS:")
    total_sent = sum(r['sent'] for r in results.values())
    total_failed = sum(r['failed'] for r in results.values())
    for group in ['A', 'B', 'C']:
        print(f"  Group {group}: {results[group]['sent']} sent, {results[group]['failed']} failed")
    print(f"  TOTAL: {total_sent} sent, {total_failed} failed")
    print(f"{'='*60}")
    
    return results


if __name__ == "__main__":
    import sys
    dry_run = '--dry-run' in sys.argv
    run_campaign(dry_run=dry_run)
