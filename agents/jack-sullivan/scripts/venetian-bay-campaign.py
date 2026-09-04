#!/usr/bin/env python3
"""
Venetian Bay Absentee Owners - Email Campaign
A/B Testing 3 subject lines
"""

import os
import json
import smtplib
import time
import random
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER = "jack@thehooverhometeam.com"
PASSWORD = os.environ["JACK_EMAIL_APP_PASSWORD"]
CC = "ch@thehooverhometeam.com"

HEADSHOT_PATH = Path('/root/.openclaw/workspace-jack-sullivan/assets/jack-headshot.jpg')

SIGNATURE_HTML = """
<br>
<table cellpadding="0" cellspacing="0" border="0" style="font-family: Arial, sans-serif;">
  <tr>
    <td style="padding-right: 15px; vertical-align: top;">
      <img src="cid:jackphoto" alt="Jack Sullivan" width="90" height="90" style="border-radius: 50%; object-fit: cover;">
    </td>
    <td style="vertical-align: top;">
      <p style="margin: 0; font-size: 16px; font-weight: bold; color: #1a3a5c;">Jack Sullivan</p>
      <p style="margin: 2px 0; font-size: 13px; color: #555;">Lead Intelligence Specialist</p>
      <p style="margin: 2px 0; font-size: 13px; color: #555;">The Hoover Home Team powered by REAL LLC</p>
      <p style="margin: 8px 0 0; font-size: 13px;">
        <span style="color: #1a3a5c;">📱</span> <a href="tel:+13862733460" style="color: #1a3a5c; text-decoration: none;">(386) 273-3460</a>
      </p>
      <p style="margin: 2px 0; font-size: 13px;">
        <span style="color: #1a3a5c;">✉️</span> <a href="mailto:jack@thehooverhometeam.com" style="color: #1a3a5c; text-decoration: none;">jack@thehooverhometeam.com</a>
      </p>
    </td>
  </tr>
</table>
"""


def text_to_html(body_text):
    """Convert plain text body to HTML paragraphs with signature."""
    lines = body_text.strip().split('\n')
    html_lines = []
    for line in lines:
        if line.strip():
            html_lines.append(f"<p style='margin: 0 0 10px 0; font-family: Arial, sans-serif; font-size: 14px; color: #333;'>{line}</p>")
        else:
            html_lines.append("<br>")
    body_html = "\n".join(html_lines)
    return f"<html><body>\n{body_html}\n{SIGNATURE_HTML}\n</body></html>"

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

Would that be helpful?"""
    
    return subject, body


def send_email(lead, group):
    subject, body = create_email(lead, group)

    msg = MIMEMultipart("related")
    msg['From'] = f"Jack Sullivan <{SENDER}>"
    msg['To'] = lead['email']
    msg['Cc'] = CC
    msg['Subject'] = subject

    msg_alt = MIMEMultipart("alternative")
    msg.attach(msg_alt)
    msg_alt.attach(MIMEText(text_to_html(body), 'html'))

    with open(HEADSHOT_PATH, "rb") as f:
        img = MIMEImage(f.read())
        img.add_header("Content-ID", "<jackphoto>")
        img.add_header("Content-Disposition", "inline", filename="jack.jpg")
        msg.attach(img)

    try:
        # Use default context with certificate verification (secure)
        ctx = ssl.create_default_context()
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30)
        server.ehlo()
        server.starttls(context=ctx)
        server.ehlo()
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
