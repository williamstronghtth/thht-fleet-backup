#!/usr/bin/env python3
"""
Send Email #2 (Following up) to all active cold calling leads
Skipping SMS touches as requested
"""

import os
import json
import smtplib
import time
import random
from datetime import datetime
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

# Config
CAMPAIGN_FILE = '/root/.openclaw/workspace-jack-sullivan/leads/cold-calling-campaign.json'
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = "jack@thehooverhometeam.com"
EMAIL_PASSWORD = os.environ["JACK_EMAIL_APP_PASSWORD"]
EMAIL_CC = "ch@thehooverhometeam.com"

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


# Email #2 Template
EMAIL_2 = {
    "subject": "Following up — {address}",
    "body": """Hi {first_name},

Just circling back on my note about your property in {city}.

I know managing a place from out of state can be a lot — whether it's a rental, vacation home, or something you're still figuring out. If you ever want to talk through your options, I'm happy to help.

What's your current situation with the property?"""
}


def load_campaign():
    with open(CAMPAIGN_FILE) as f:
        return json.load(f)


def save_campaign(data):
    with open(CAMPAIGN_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def extract_city(address):
    if not address:
        return "your area"
    parts = address.split(',')
    if len(parts) >= 2:
        return parts[-2].strip()
    return "your area"


def send_email(lead):
    if not lead.get('email'):
        return False, "No email"
    
    city = extract_city(lead.get('address', ''))
    address = lead.get('address', 'your property')
    
    subject = EMAIL_2['subject'].format(
        first_name=lead.get('first_name', 'there'),
        city=city,
        address=address
    )
    body = EMAIL_2['body'].format(
        first_name=lead.get('first_name', 'there'),
        city=city,
        address=address
    )
    
    msg = MIMEMultipart("related")
    msg['From'] = f"Jack Sullivan <{EMAIL_SENDER}>"
    msg['To'] = lead['email']
    msg['Cc'] = EMAIL_CC
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
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True, "Sent"
    except Exception as e:
        return False, str(e)


def main():
    campaign = load_campaign()
    
    print("=" * 60)
    print("SENDING EMAIL #2 (Following up)")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60 + "\n")
    
    sent = 0
    skipped = 0
    failed = 0
    
    for lead in campaign['leads']:
        # Skip if replied or unsubscribed
        if lead.get('replied') or lead.get('status') == 'unsubscribed':
            skipped += 1
            continue
        
        # Skip if no email
        if not lead.get('email'):
            skipped += 1
            continue
        
        # Skip if already got email #2 (current_touch >= 2)
        if lead.get('current_touch', 0) >= 2:
            skipped += 1
            continue
        
        # Must have received email #1
        if lead.get('current_touch', 0) < 1:
            skipped += 1
            continue
        
        name = f"{lead.get('first_name', '')} {lead.get('last_name', '')}".strip()
        
        success, msg = send_email(lead)
        
        if success:
            print(f"  ✓ {name} ({lead['email']})")
            lead['current_touch'] = 2
            lead['last_touch_date'] = datetime.now().isoformat()
            sent += 1
        else:
            print(f"  ✗ {name}: {msg}")
            failed += 1
        
        # Small delay between sends
        time.sleep(random.uniform(3, 6))
    
    # Save updated campaign
    save_campaign(campaign)
    
    print(f"\n{'=' * 60}")
    print(f"RESULTS: {sent} sent, {skipped} skipped, {failed} failed")
    print("=" * 60)
    
    return sent, skipped, failed


if __name__ == "__main__":
    main()
