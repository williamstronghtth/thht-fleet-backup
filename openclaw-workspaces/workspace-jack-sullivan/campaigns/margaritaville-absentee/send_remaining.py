#!/usr/bin/env python3
import csv, smtplib, time, random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime
from pathlib import Path

CAMPAIGN_DIR = Path("/root/.openclaw/workspace-jack-sullivan/campaigns/margaritaville-absentee")
LEADS_FILE = CAMPAIGN_DIR / "leads-raw.csv"
LOG_FILE = CAMPAIGN_DIR / "touch1_email_run.log"
HEADSHOT_PATH = Path("/root/.openclaw/workspace-jack-sullivan/assets/jack-headshot.jpg")

SMTP_USER = "jack@thehooverhometeam.com"
SMTP_PASS = "rpwg sdna xtgp fujn"
CC_EMAIL = "ch@thehooverhometeam.com"

SUBJECT = "Following up on Chris's call about your Margaritaville property"
TEMPLATE = """Hi {first_name},

My team lead Chris gave you a call yesterday about your property in Margaritaville. He wanted to connect since you own there but live out of the area.

I'm following up to see if there's anything we can help with. Whether you're curious about what your home is worth in today's market or ever thinking about selling, we're happy to be a resource.

No pressure at all. Just reply to this email or give us a call anytime."""

SIGNATURE_HTML = """<br><table cellpadding="0" cellspacing="0" border="0" style="font-family: Arial, sans-serif;"><tr><td style="padding-right: 15px; vertical-align: top;"><img src="cid:jackphoto" alt="Jack Sullivan" width="90" height="90" style="border-radius: 50%; object-fit: cover;"></td><td style="vertical-align: top;"><p style="margin: 0; font-size: 16px; font-weight: bold; color: #1a3a5c;">Jack Sullivan</p><p style="margin: 2px 0; font-size: 13px; color: #555;">Lead Intelligence Specialist</p><p style="margin: 2px 0; font-size: 13px; color: #555;">The Hoover Home Team powered by REAL LLC</p><p style="margin: 8px 0 0; font-size: 13px;"><span style="color: #1a3a5c;">📱</span> <a href="tel:+13862733460" style="color: #1a3a5c; text-decoration: none;">(386) 273-3460</a></p><p style="margin: 2px 0; font-size: 13px;"><span style="color: #1a3a5c;">✉️</span> <a href="mailto:jack@thehooverhometeam.com" style="color: #1a3a5c; text-decoration: none;">jack@thehooverhometeam.com</a></p></td></tr></table>"""

# Skip list - 12 total
SKIP_EMAILS = {
    "leeman488@hotmail.com",   # Christie Orton
    "adapice@comcast.net",     # Andrew Dapice
    "angeekaz@yahoo.com",      # Darren Hall
    "keanej@aol.com",          # James Keane
    "toconner3209@aol.com",    # Timothy O'Connor
    "heat7591@aol.com",        # Gustive Pece
    "vmeans2016@gmail.com",    # Valerie Balzanti
    "rmcmenamin@address.com",  # Rita Mcmenamin
    "efarris1950@optonline.net", # Elaine Farris
    "tfiricano@gmail.com",     # Anthony Firicano
    "dannyalexander@comcast.net", # Danny Alexander
    "pbasmith@yahoo.com",       # Paul Smith
    "kendallaroth@gmail.com",   # Kendall Roth
    "chris@lokerhome.com",     # Christopher Loker
    "dksobx@aol.com",          # David Striebich
    "cmcquaide@gmail.com",     # Cynthia Mcquaide
    "sdm0489@aol.com",         # Scott Mcpherson
    "alexmk327@aol.com",       # Deborah/Debbie Kivett
    "tuckerrl@bellsouth.net",  # Ronald Tucker
    "jeneumann@msn.com",       # James Neumann
    "laurenb92@yahoo.com",     # Ronald Reagan
    "nmartin@simione.com",     # Nancy Portolese
    "lpreston10@msn.com",      # Warren Preston
    "kimmy237@hotmail.com",    # Adrienne Menken
    "wawags72@hotmail.com",    # Wallace Wagner
    "hbs41598@optonline.net",  # Raymond Sussek
    "susan.manion@flash.net"   # Edward Manion
}

def get_already_sent():
    sent = set()
    try:
        with open(LOG_FILE, 'r') as f:
            for line in f:
                if "Sending to" in line and "(" in line:
                    start = line.find("(") + 1
                    end = line.find(")")
                    if start > 0 and end > start:
                        email = line[start:end].strip().lower()
                        sent.add(email)
    except:
        pass
    return sent

def log(msg):
    line = f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def text_to_html(text):
    lines = text.strip().split('\n')
    html_lines = [f"<p style='margin: 0 0 10px 0; font-family: Arial, sans-serif; font-size: 14px; color: #333;'>{line}</p>" if line.strip() else "<br>" for line in lines]
    return f"<html><body>{''.join(html_lines)}{SIGNATURE_HTML}</body></html>"

def send_email(to_email, first_name):
    msg = MIMEMultipart("related")
    msg['From'] = f"Jack Sullivan <{SMTP_USER}>"
    msg['To'] = to_email
    msg['Cc'] = CC_EMAIL
    msg['Subject'] = SUBJECT
    msg_alt = MIMEMultipart("alternative")
    msg.attach(msg_alt)
    msg_alt.attach(MIMEText(text_to_html(TEMPLATE.replace("{first_name}", first_name)), 'html'))
    with open(HEADSHOT_PATH, "rb") as f:
        img = MIMEImage(f.read())
        img.add_header("Content-ID", "<jackphoto>")
        img.add_header("Content-Disposition", "inline", filename="jack.jpg")
        msg.attach(img)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

def main():
    ALREADY_SENT = get_already_sent()
    
    log("=" * 50)
    log("Margaritaville Touch 1 - v8 (+Valerie Balzanti removed)")
    log("=" * 50)
    
    with open(LEADS_FILE, "r") as f:
        leads = list(csv.DictReader(f))[:150]
    
    eligible = [l for l in leads if l.get("Email", "").strip() and l.get("Email", "").strip().lower() not in ALREADY_SENT and l.get("Email", "").strip().lower() not in {e.lower() for e in SKIP_EMAILS}]
    
    log(f"Already sent: {len(ALREADY_SENT)}, Skipped: 7, Remaining: {len(eligible)}")
    
    sent = errors = 0
    for i, lead in enumerate(eligible):
        email = lead["Email"].strip()
        first_name = lead.get("First Name", "").strip() or "there"
        log(f"[{i+1}/{len(eligible)}] Sending to {first_name} {lead.get('Last Name', '')} ({email})")
        try:
            send_email(email, first_name)
            log("  -> ✅ Sent")
            sent += 1
        except Exception as e:
            log(f"  -> ❌ Error: {e}")
            errors += 1
        if i < len(eligible) - 1:
            wait = random.randint(60, 90)
            log(f"  Waiting {wait}s...")
            time.sleep(wait)
    log(f"Done: {sent} sent (+ {len(ALREADY_SENT)} earlier), {errors} errors")

if __name__ == "__main__":
    main()
