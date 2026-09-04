#!/usr/bin/env python3
"""Process VCPA matches and create final lis pendens lead list."""

import csv
from collections import defaultdict

input_file = 'leads/lis-pendens/lis-pendens-vcpa-matches.csv'
names_file = 'leads/lis-pendens/lis-pendens-names-for-vcpa.csv'
output_file = 'leads/lis-pendens/lis-pendens-final-leads.csv'

# Load original names with instrument/date info
name_to_info = {}
with open(names_file) as f:
    reader = csv.DictReader(f)
    for row in reader:
        key = f"{row['Last Name']}, {row['First Name']}"
        name_to_info[key] = {
            'instrument': row.get('instrument', ''),
            'date': row.get('date', ''),
            'source': row.get('source', 'lis_pendens')
        }

# Read matches
with open(input_file) as f:
    reader = csv.DictReader(f)
    matches = list(reader)

print(f"Total match records: {len(matches)}")

# Filter for HIGH confidence
high_conf = [m for m in matches if m.get('Confidence', '').upper() == 'HIGH']
print(f"HIGH confidence: {len(high_conf)}")

# Deduplicate by original name + address
seen = set()
leads = []

for m in high_conf:
    orig_name = m.get('Original Name', '')
    address = m.get('Property Address', '')
    city = m.get('City', '')
    
    key = f"{orig_name}|{address}"
    if key in seen:
        continue
    seen.add(key)
    
    # Get instrument/date from original lookup
    info = name_to_info.get(orig_name, {})
    
    # Parse name
    parts = orig_name.replace('"', '').split(',')
    last_name = parts[0].strip() if parts else ''
    first_name = parts[1].strip() if len(parts) > 1 else ''
    
    leads.append({
        'first_name': first_name,
        'last_name': last_name,
        'address': address,
        'city': city,
        'state': 'FL',
        'zip': '',  # Will need skip trace for this
        'date_filed': info.get('date', ''),
        'instrument': info.get('instrument', ''),
        'parcel_id': m.get('Parcel ID', '')
    })

# Sort by date filed descending
leads.sort(key=lambda x: x['date_filed'], reverse=True)

# Write output
with open(output_file, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['first_name', 'last_name', 'address', 'city', 'state', 'zip', 'date_filed', 'instrument', 'parcel_id'])
    writer.writeheader()
    writer.writerows(leads)

print(f"\n=== FINAL RESULTS ===")
print(f"Lis Pendens Leads (HIGH confidence): {len(leads)}")
print(f"Output: {output_file}")

# Date range
dates = [l['date_filed'] for l in leads if l['date_filed']]
if dates:
    print(f"Date range: {min(dates)} to {max(dates)}")

# City breakdown
cities = defaultdict(int)
for l in leads:
    cities[l['city']] += 1
print(f"\nTop cities:")
for city, count in sorted(cities.items(), key=lambda x: -x[1])[:10]:
    print(f"  {city}: {count}")

# Show sample
print("\n=== NEWEST 15 LEADS ===")
for lead in leads[:15]:
    name = f"{lead['first_name']} {lead['last_name']}"
    addr = f"{lead['address']}, {lead['city']}"[:40]
    print(f"{lead['date_filed']} | {name[:22]:<22} | {addr}")
