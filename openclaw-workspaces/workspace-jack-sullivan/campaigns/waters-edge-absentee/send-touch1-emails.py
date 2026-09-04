#!/usr/bin/env python3
"""
Waters Edge Absentee - Touch 1 Email Sender
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
LEADS_FILE = CAMPAIGN_DIR / "leads.csv"
TEMPLATES_DIR = CAMPAIGN_DIR / "templates"
LOG_FILE = CAMPAIGN_DIR / "touch1_email_run.log"
HEADSHOT_PATH = CAMPAIGN_DIR.parent.parent / "assets" / "jack-headshot.jpg"

SMTP_USER = "jack@thehooverhometeam.com"
SMTP_PASS = "rpwg sdna xtgp fujn"
CC_EMAIL = "ch@thehooverhometeam.com"

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

def send_email(to_email, subject, body):
    msg = MIMEMultipart("related")
    msg['From'] = f"Jack Sullivan <{SMTP_USER}>"
    msg['To'] = to_email
    msg['Cc'] = CC_EMAIL
    msg['Subject'] = subject
    
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
    log("Waters Edge Touch 1 Emails (with signature)")
    log("=" * 50)
    
    # Load template
    with open(TEMPLATES_DIR / "email_touch1.txt") as f:
        template = f.read()
    
    # Load leads
    with open(LEADS_FILE, "r") as f:
        reader = csv.DictReader(f)
        leads = list(reader)
    
    # Filter: has email, active status, touch 0
    eligible = [
        l for l in leads 
        if l.get("email", "").strip() 
        and l.get("status") == "active"
        and l.get("current_touch", "0") == "0"
    ]
    
    log(f"Eligible leads: {len(eligible)}")
    
    sent = errors = 0
    
    for lead in eligible:
        email = lead["email"].strip()
        first_name = lead.get("first_name", "").strip() or "there"
        
        body = template.replace("{first_name}", first_name)
        subject = "Your neighbors in Waters Edge"
        
        log(f"Sending to {first_name} {lead.get('last_name', '')} ({email})")
        
        try:
            send_email(email, subject, body)
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
