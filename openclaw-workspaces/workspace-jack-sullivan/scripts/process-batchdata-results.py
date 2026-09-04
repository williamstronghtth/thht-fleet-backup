#!/usr/bin/env python3
"""Process BatchData skip trace results and prep for CRM."""

import csv
import json

input_file = 'leads/lis-pendens/batchdata-results.csv'
output_file = 'leads/lis-pendens/lis-pendens-crm-ready.csv'

# Read results
with open(input_file, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    results = list(reader)

print(f"Total records: {len(results)}")

# Process each lead
leads = []
stats = {'matched': 0, 'with_phone': 0, 'with_email': 0, 'dnc': 0, 'deceased': 0, 'litigator': 0}

for r in results:
    # Check if matched
    if r.get('Skiptrace:meta.matched', '').lower() != 'true':
        continue
    stats['matched'] += 1
    
    # Check deceased
    if r.get('Skiptrace:death.deceased', '').lower() == 'true':
        stats['deceased'] += 1
        continue
    
    # Check litigator (might want to be careful)
    is_litigator = r.get('Skiptrace:litigator', '').lower() == 'true'
    if is_litigator:
        stats['litigator'] += 1
    
    # Get best phone (non-DNC, mobile preferred)
    best_phone = ''
    phone_type = ''
    for i in range(5):
        phone = r.get(f'Skiptrace:phoneNumbers.{i}.number', '')
        ptype = r.get(f'Skiptrace:phoneNumbers.{i}.type', '')
        dnc = r.get(f'Skiptrace:phoneNumbers.{i}.dnc', '').lower() == 'true'
        
        if phone and not dnc:
            if not best_phone or ptype == 'Mobile':
                best_phone = phone
                phone_type = ptype
                if ptype == 'Mobile':
                    break  # Mobile is best, stop looking
    
    if best_phone:
        stats['with_phone'] += 1
    
    # Get best email (tested preferred)
    best_email = ''
    for i in range(3):
        email = r.get(f'Skiptrace:emails.{i}.email', '')
        tested = r.get(f'Skiptrace:emails.{i}.tested', '').lower() == 'true'
        
        if email:
            if not best_email or tested:
                best_email = email
                if tested:
                    break
    
    if best_email:
        stats['with_email'] += 1
    
    # Build lead record
    lead = {
        'first_name': r.get('Skiptrace:name.first', r.get('First Name', '')),
        'last_name': r.get('Skiptrace:name.last', r.get('Last Name', '')),
        'address': r.get('Property Address', ''),
        'city': r.get('Property City', ''),
        'state': r.get('Property State', 'FL'),
        'zip': r.get('Property Zip', ''),
        'phone': best_phone,
        'phone_type': phone_type,
        'email': best_email,
        'mailing_address': r.get('Skiptrace:mailingAddress.street', ''),
        'mailing_city': r.get('Skiptrace:mailingAddress.city', ''),
        'mailing_state': r.get('Skiptrace:mailingAddress.state', ''),
        'mailing_zip': r.get('Skiptrace:mailingAddress.zip', ''),
        'lead_type': 'pre-foreclosure',
        'source': 'lis_pendens',
        'is_litigator': 'yes' if is_litigator else 'no',
        'dnc_tcpa': r.get('Skiptrace:dnc.tcpa', 'false'),
    }
    
    leads.append(lead)

# Write CRM-ready file
with open(output_file, 'w', newline='') as f:
    fieldnames = ['first_name', 'last_name', 'address', 'city', 'state', 'zip', 
                  'phone', 'phone_type', 'email', 'mailing_address', 'mailing_city',
                  'mailing_state', 'mailing_zip', 'lead_type', 'source', 'is_litigator', 'dnc_tcpa']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(leads)

print(f"\n{'='*50}")
print(f"🎯 SKIP TRACE RESULTS")
print(f"{'='*50}")
print(f"Matched:      {stats['matched']}")
print(f"Deceased:     {stats['deceased']} (removed)")
print(f"Litigators:   {stats['litigator']} (flagged)")
print(f"With phone:   {stats['with_phone']}")
print(f"With email:   {stats['with_email']}")
print(f"\n✅ CRM-ready leads: {len(leads)}")
print(f"📁 Output: {output_file}")

# Show sample
print(f"\n{'='*50}")
print("SAMPLE LEADS (first 10)")
print(f"{'='*50}")
for lead in leads[:10]:
    name = f"{lead['first_name']} {lead['last_name']}"
    phone = lead['phone'] or 'No phone'
    email = lead['email'][:25] + '...' if lead['email'] and len(lead['email']) > 25 else (lead['email'] or 'No email')
    print(f"{name[:20]:<20} | {phone:<12} | {email}")
