#!/usr/bin/env python3
"""Load lis pendens leads into CRM."""

import csv
import requests
import time

CRM_API = 'https://clientlist.onrender.com/api/clients'
input_file = 'leads/lis-pendens/lis-pendens-crm-ready.csv'

# Read leads
with open(input_file) as f:
    reader = csv.DictReader(f)
    leads = list(reader)

print(f"Loading {len(leads)} pre-foreclosure leads to CRM...")

success = 0
errors = []

for i, lead in enumerate(leads):
    # Format for CRM
    client = {
        'firstName': lead['first_name'],
        'lastName': lead['last_name'],
        'email': lead['email'] if lead['email'] else None,
        'phone': lead['phone'] if lead['phone'] else None,
        'address': lead['address'],
        'city': lead['city'],
        'state': lead['state'],
        'zip': lead['zip'],
        'leadType': 'pre-foreclosure',
        'source': 'lis_pendens',
        'status': 'new',
        'notes': f"Mailing: {lead['mailing_address']}, {lead['mailing_city']}, {lead['mailing_state']} {lead['mailing_zip']}" if lead['mailing_address'] else '',
        'tags': ['lis-pendens', 'pre-foreclosure']
    }
    
    # Add litigator warning
    if lead.get('is_litigator') == 'yes':
        client['tags'].append('litigator-caution')
        client['notes'] = (client['notes'] + ' | ⚠️ LITIGATOR FLAG').strip(' | ')
    
    try:
        resp = requests.post(CRM_API, json=client, timeout=10)
        if resp.status_code in [200, 201]:
            success += 1
        else:
            errors.append(f"{lead['first_name']} {lead['last_name']}: {resp.status_code}")
    except Exception as e:
        errors.append(f"{lead['first_name']} {lead['last_name']}: {str(e)}")
    
    # Progress
    if (i + 1) % 10 == 0:
        print(f"  [{i+1}/{len(leads)}] loaded...")
    
    time.sleep(0.1)  # Rate limit

print(f"\n{'='*50}")
print(f"✅ CRM LOAD COMPLETE")
print(f"{'='*50}")
print(f"Success: {success}/{len(leads)}")
if errors:
    print(f"Errors: {len(errors)}")
    for e in errors[:5]:
        print(f"  - {e}")
