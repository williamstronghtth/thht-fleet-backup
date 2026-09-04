#!/usr/bin/env python3
"""
Cypress Head Absentee - Touch 1 Email
Follow up to Chris's cold calls
"""
import csv, smtplib, time, random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime
from pathlib import Path

CAMPAIGN_DIR = Path(__file__).parent
LEADS_FILE = CAMPAIGN_DIR / 'leads-raw.csv'
LOG_FILE = CAMPAIGN_DIR / 'touch1_email_run.log'
HEADSHOT_PATH = Path('/root/.openclaw/workspace-jack-sullivan/assets/jack-headshot.jpg')

SMTP_USER = 'jack@thehooverhometeam.com'
SMTP_PASS = 'rpwg sdna xtgp fujn'
CC_EMAIL = 'ch@thehooverhometeam.com'

SUBJECT = "Following up on Chris's call about your Cypress Head property"
TEMPLATE = """Hi {first_name},

My team lead Chris gave you a call today about your property in Cypress Head. He wanted to connect since you own there but live out of the area.

I'm following up to see if there's anything we can help with. Whether you're curious about what your home is worth in today's market or ever thinking about selling, we're happy to be a resource.

No pressure at all. Just reply to this email or give us a call anytime."""

SIGNATURE_HTML = """<br><table cellpadding='0' cellspacing='0' border='0' style='font-family: Arial, sans-serif;'><tr><td style='padding-right: 15px; vertical-align: top;'><img src='cid:jackphoto' alt='Jack Sullivan' width='90' height='90' style='border-radius: 50%; object-fit: cover;'></td><td style='vertical-align: top;'><p style='margin: 0; font-size: 16px; font-weight: bold; color: #1a3a5c;'>Jack Sullivan</p><p style='margin: 2px 0; font-size: 13px; color: #555;'>Lead Intelligence Specialist</p><p style='margin: 2px 0; font-size: 13px; color: #555;'>The Hoover Home Team powered by REAL LLC</p><p style='margin: 8px 0 0; font-size: 13px;'><span style='color: #1a3a5c;'>📱</span> <a href='tel:+13862733460' style='color: #1a3a5c; text-decoration: none;'>(386) 273-3460</a></p><p style='margin: 2px 0; font-size: 13px;'><span style='color: #1a3a5c;'>✉️</span> <a href='mailto:jack@thehooverhometeam.com' style='color: #1a3a5c; text-decoration: none;'>jack@thehooverhometeam.com</a></p></td></tr></table>"""

# Skip list
SKIP_EMAILS = {
    "cronje@earthlink.net",      # Petrus Cronje - already in Waters Edge
    "johnbateson2@gmail.com"     # John Bateson - warm lead
}

def log(msg):
    line = f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}"
    print(line)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')

def html_body(text):
    lines = text.strip().split('\n')
    html = ''.join([f"<p style='margin: 0 0 10px 0; font-family: Arial, sans-serif; font-size: 14px; color: #333;'>{line}</p>" if line.strip() else '<br>' for line in lines])
    return f"<html><body>{html}{SIGNATURE_HTML}</body></html>"

def send_email(to_email, first_name):
    msg = MIMEMultipart('related')
    msg['From'] = f'Jack Sullivan <{SMTP_USER}>'
    msg['To'] = to_email
    msg['Cc'] = CC_EMAIL
    msg['Subject'] = SUBJECT
    alt = MIMEMultipart('alternative')
    msg.attach(alt)
    alt.attach(MIMEText(html_body(TEMPLATE.replace('{first_name}', first_name)), 'html'))
    with open(HEADSHOT_PATH, 'rb') as f:
        img = MIMEImage(f.read())
        img.add_header('Content-ID', '<jackphoto>')
        img.add_header('Content-Disposition', 'inline', filename='jack.jpg')
        msg.attach(img)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

def main():
    with open(LEADS_FILE) as f:
        leads = list(csv.DictReader(f))
    
    # Deduplicate by email, skip empty emails and skip list
    seen = set()
    eligible = []
    for l in leads:
        email = l.get('Email', '').strip()
        if not email or email.lower() in SKIP_EMAILS or email.lower() in seen:
            continue
        seen.add(email.lower())
        eligible.append(l)
    
    log('='*50)
    log('Cypress Head Absentee - Touch 1')
    log('='*50)
    log(f'Total leads: {len(leads)}')
    log(f'Eligible (deduplicated, with email): {len(eligible)}')
    log(f'Skipped: Petrus Cronje (already in Waters Edge)')
    
    sent = errors = 0
    for i, lead in enumerate(eligible):
        email = lead['Email'].strip()
        first = (lead.get('First Name') or 'there').strip() or 'there'
        last = lead.get('Last Name', '')
        log(f'[{i+1}/{len(eligible)}] Sending to {first} {last} ({email})')
        try:
            send_email(email, first)
            sent += 1
            log('  -> ✅ Sent')
        except Exception as e:
            errors += 1
            log(f'  -> ❌ Error: {e}')
        if i < len(eligible)-1:
            wait = random.randint(60, 90)
            log(f'  Waiting {wait}s...')
            time.sleep(wait)
    log('-'*50)
    log(f'Done: {sent} sent, {errors} errors')

if __name__ == '__main__':
    main()
