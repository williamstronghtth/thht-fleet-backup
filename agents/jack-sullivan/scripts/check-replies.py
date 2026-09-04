#!/usr/bin/env python3
"""
Check for email replies and notify Chris via Telegram.
Run periodically to catch incoming responses.
"""

import imaplib
import email
from email.header import decode_header
from datetime import datetime, timedelta
import json
import os
import sys
from pathlib import Path

# Load shared secrets from /root/agents/.env (no hardcoded credentials in source)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from secrets_loader import require

# Config
IMAP_HOST = "imap.gmail.com"
EMAIL = "jack@thehooverhometeam.com"
PASSWORD = require("JACK_EMAIL_APP_PASSWORD")
CHRIS_CHAT_ID = "8560812913"

# Track notified replies to avoid duplicates
NOTIFIED_FILE = "/root/.openclaw/workspace-jack-sullivan/data/notified-replies.json"

def load_notified():
    """Load set of already-notified message IDs"""
    try:
        with open(NOTIFIED_FILE, 'r') as f:
            return set(json.load(f))
    except:
        return set()

def save_notified(notified):
    """Save notified message IDs"""
    os.makedirs(os.path.dirname(NOTIFIED_FILE), exist_ok=True)
    with open(NOTIFIED_FILE, 'w') as f:
        json.dump(list(notified), f)

def check_inbox():
    """Check for new replies to our outreach emails"""
    notified = load_notified()
    new_replies = []
    
    try:
        mail = imaplib.IMAP4_SSL(IMAP_HOST)
        mail.login(EMAIL, PASSWORD)
        mail.select("INBOX")
        
        # Search for recent emails (last 24 hours)
        date = (datetime.now() - timedelta(days=1)).strftime("%d-%b-%Y")
        _, messages = mail.search(None, f'(SINCE {date})')
        
        for msg_id in messages[0].split():
            msg_id_str = msg_id.decode()
            if msg_id_str in notified:
                continue
            
            _, msg_data = mail.fetch(msg_id, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])
            
            # Get sender
            from_addr = msg.get("From", "")
            subject = msg.get("Subject", "")
            
            # Decode subject if needed
            if subject:
                decoded = decode_header(subject)
                subject = decoded[0][0]
                if isinstance(subject, bytes):
                    subject = subject.decode()
            
            # Skip if it's from ourselves or Chris
            if "jack@thehooverhometeam.com" in from_addr.lower():
                continue
            if "ch@thehooverhometeam.com" in from_addr.lower():
                continue
            
            # Check if this looks like a reply to our outreach
            keywords = ["re:", "quick question", "market update", "inherited", "property"]
            is_reply = any(kw in subject.lower() for kw in keywords)
            
            if is_reply:
                # Get body preview
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode()[:200]
                            break
                else:
                    body = msg.get_payload(decode=True).decode()[:200]
                
                new_replies.append({
                    "from": from_addr,
                    "subject": subject,
                    "preview": body.strip()
                })
                notified.add(msg_id_str)
        
        mail.close()
        mail.logout()
        
    except Exception as e:
        print(f"Error checking inbox: {e}")
        return []
    
    save_notified(notified)
    return new_replies

def format_notification(replies):
    """Format replies for Telegram notification"""
    if not replies:
        return None
    
    msg = "🔔 **NEW LEAD REPLIES:**\n\n"
    for r in replies:
        msg += f"**From:** {r['from']}\n"
        msg += f"**Subject:** {r['subject']}\n"
        msg += f"**Preview:** {r['preview'][:100]}...\n\n"
    
    msg += "Check your inbox to respond! 🎯"
    return msg

if __name__ == "__main__":
    print(f"Checking for replies... {datetime.now()}")
    replies = check_inbox()
    
    if replies:
        print(f"Found {len(replies)} new replies!")
        notification = format_notification(replies)
        print(notification)
        # Note: Actual Telegram send would go through OpenClaw message tool
    else:
        print("No new replies.")
