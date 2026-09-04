#!/usr/bin/env python3
"""
Expired Leads Email - Follow up to cold calls
With Jack's HTML signature and headshot
"""

import csv
import smtplib
import time
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime
from pathlib import Path

CAMPAIGN_DIR = Path(__file__).parent
LEADS_FILE = CAMPAIGN_DIR / "expired-march-2026.csv"
LOG_FILE = CAMPAIGN_DIR / "expired_email_run.log"
HEADSHOT_PATH = CAMPAIGN_DIR.parent / "assets" / "jack-headshot.jpg"

SMTP_USER = "jack@thehooverhometeam.com"
SMTP_PASS = "rpwg sdna xtgp fujn"
CC_EMAIL = "ch@thehooverhometeam.com"

# Skip list - positive responses
SKIP_EMAILS = ["alondralorrianne@gmail.com", "rhwarfel@yahoo.com", "davidkosmas@me.com"]  # + David Kosmas removed

SUBJECT = "Following up on our call"

TEMPLATE = """Hi {first_name},

I wanted to follow up on our conversation about your property at {address}.

I know the listing expired and that can be frustrating. Sometimes the market timing wasn't right, or the previous approach didn't connect with the right buyers.

I'd love to share some fresh ideas on how we can get your home sold. A new strategy, updated pricing analysis, and targeted marketing can make all the difference.

No pressure at all. If you'd like to chat, just reply to this email or give me a call."""

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

SPACING_MIN = 60
SPACING_MAX = 90

def log(msg):
    line = f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def text_to_html(text):
    lines = text.strip().split('\n')
    html_lines = []
    for line in lines:
        if line.strip():
            html_lines.append(f"<p style='margin: 0 0 10px 0; font-family: Arial, sans-serif; font-size: 14px; color: #333;'>{line}</p>")
        else:
            html_lines.append("<br>")
    
    return f"""<html><body>
{"".join(html_lines)}
{SIGNATURE_HTML}
</body></html>"""

def send_email(to_email, first_name, address):
    msg = MIMEMultipart("related")
    msg['From'] = f"Jack Sullivan <{SMTP_USER}>"
    msg['To'] = to_email
    msg['Cc'] = CC_EMAIL
    msg['Subject'] = SUBJECT
    
    body = TEMPLATE.format(first_name=first_name, address=address)
    html_body = text_to_html(body)
    
    msg_alt = MIMEMultipart("alternative")
    msg.attach(msg_alt)
    msg_alt.attach(MIMEText(html_body, 'html'))
    
    with open(HEADSHOT_PATH, "rb") as f:
        img = MIMEImage(f.read())
        img.add_header("Content-ID", "<jackphoto>")
        img.add_header("Content-Disposition", "inline", filename="jack.jpg")
        msg.attach(img)
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

def main():
    log("=" * 50)
    log("Expired Leads Email Campaign (with signature)")
    log("=" * 50)
    
    with open(LEADS_FILE, "r") as f:
        reader = csv.DictReader(f)
        leads = list(reader)
    
    eligible = [
        l for l in leads 
        if l.get("Email", "").strip() 
        and l.get("Email", "").lower() not in [e.lower() for e in SKIP_EMAILS]
        and l.get("First Name", "").strip()
    ]
    
    log(f"Eligible leads: {len(eligible)}")
    log(f"Skipped: {', '.join(SKIP_EMAILS)}")
    
    sent = errors = 0
    
    for lead in eligible:
        email = lead["Email"].strip()
        first_name = lead.get("First Name", "").strip() or "there"
        address = f"{lead.get('Street Name', '')} {lead.get('City', '')} {lead.get('State', '')} {lead.get('Zip', '')}".strip()
        
        log(f"Sending to {first_name} {lead.get('Last Name', '')} ({email})")
        
        try:
            send_email(email, first_name, address)
            log("  -> ✅ Sent")
            sent += 1
        except Exception as e:
            log(f"  -> ❌ Error: {e}")
            errors += 1
        
        wait = random.randint(SPACING_MIN, SPACING_MAX)
        log(f"  Waiting {wait}s...")
        time.sleep(wait)
    
    log("-" * 50)
    log(f"Done: {sent} sent, {errors} errors")

if __name__ == "__main__":
    main()
