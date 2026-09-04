#!/usr/bin/env python3
"""Upload Port Orange absentee owners to CRM with tier tagging."""

import csv
import sys
import requests
import time
from pathlib import Path

# Load shared secrets from /root/agents/.env (no hardcoded credentials in source)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from secrets_loader import require

CRM_API = 'https://clientlist.onrender.com/api/clients'
CRM_HEADERS = {'X-API-Key': require("CRM_API_KEY")}

INPUT_FILE = '/root/agents/jack-sullivan/workspace/inbox/Port Orange Absentee - Sheet1 (1).csv'

# Keywords that indicate a corporate/LLC/trust entity
CORPORATE_KEYWORDS = ['llc', 'inc', 'lp', ' lp', 'corp', 'trust', ' tr', 'properties',
                      'assets', 'borrower', 'church', 'bishop', 'group']


def is_corporate(first_name, last_name):
    combined = (first_name + ' ' + last_name).lower()
    return any(kw in combined for kw in CORPORATE_KEYWORDS)


def get_tier(first_name, last_name, remarks):
    if is_corporate(first_name, last_name):
        return 2, 'CORPORATE_ENTITY'
    state = (remarks or '').strip().upper()
    if state and state != 'FL':
        return 1, 'OUT_OF_STATE'
    return 3, 'FL_ABSENTEE'


def build_notes(tier_num, tier_tag, remarks):
    state = (remarks or '').strip().upper() or 'FL'
    return (
        f"Port Orange absentee owner | Tier {tier_num} ({tier_tag}) | "
        f"Mailing state: {state} | Source: port-orange-absentee-2026-04-29"
    )


with open(INPUT_FILE, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    leads = list(reader)

print(f"Uploading {len(leads)} Port Orange absentee leads to CRM...")

success = 0
errors = []
tier_counts = {1: 0, 2: 0, 3: 0}

for i, lead in enumerate(leads):
    first = lead.get('First Name', '').strip()
    last = lead.get('Last Name', '').strip()
    email = lead.get('Email', '').strip() or None
    phone = lead.get('Phone Number', '').strip() or None
    address = lead.get('Address Street', '').strip()
    remarks = lead.get('Remarks', '').strip()

    tier_num, tier_tag = get_tier(first, last, remarks)
    tier_counts[tier_num] += 1

    tags = ['ABSENTEE_OWNER', f'TIER_{tier_num}', tier_tag, 'port-orange-32127']

    client = {
        'firstName': first,
        'lastName': last,
        'email': email,
        'phone': phone,
        'address': address,
        'city': 'Port Orange',
        'state': 'FL',
        'zip': '32127',
        'leadType': 'absentee-owner',
        'source': 'port_orange_absentee_list',
        'status': 'new',
        'notes': build_notes(tier_num, tier_tag, remarks),
        'tags': tags,
    }

    try:
        resp = requests.post(CRM_API, json=client, headers=CRM_HEADERS, timeout=10)
        if resp.status_code in [200, 201]:
            success += 1
        else:
            errors.append(f"{first} {last}: HTTP {resp.status_code} — {resp.text[:80]}")
    except Exception as e:
        errors.append(f"{first} {last}: {str(e)}")

    if (i + 1) % 25 == 0:
        print(f"  [{i+1}/{len(leads)}] uploaded...")

    time.sleep(0.1)

print(f"\n{'='*55}")
print(f"CRM UPLOAD COMPLETE — Port Orange Absentees")
print(f"{'='*55}")
print(f"Total uploaded: {success}/{len(leads)}")
print(f"  Tier 1 (OUT_OF_STATE):    {tier_counts[1]}")
print(f"  Tier 2 (CORPORATE):       {tier_counts[2]}")
print(f"  Tier 3 (FL_ABSENTEE):     {tier_counts[3]}")
if errors:
    print(f"\nErrors ({len(errors)}):")
    for e in errors[:10]:
        print(f"  - {e}")
