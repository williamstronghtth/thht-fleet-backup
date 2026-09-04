#!/usr/bin/env python3
"""Final lis pendens lead processing with deduplication and validation."""

import csv
from collections import defaultdict

input_file = 'leads/lis-pendens/lis-pendens-vcpa-matches.csv'
names_file = 'leads/lis-pendens/lis-pendens-names-for-vcpa.csv'
output_file = 'leads/lis-pendens/lis-pendens-final-leads.csv'

# Invalid address patterns
INVALID_PATTERNS = ['NOT AVAIL', 'NO STREET', 'UNKNOWN', 'N/A']

def is_valid_address(addr):
    if not addr or len(addr) < 5:
        return False
    addr_upper = addr.upper()
    for pattern in INVALID_PATTERNS:
        if pattern in addr_upper:
            return False
    # Must have at least one number (street number)
    if not any(c.isdigit() for c in addr):
        return False
    return True

# Load original names with instrument/date info
name_to_info = {}
with open(names_file) as f:
    reader = csv.DictReader(f)
    for row in reader:
        key = f"{row['Last Name']}, {row['First Name']}"
        name_to_info[key] = {
            'instrument': row.get('instrument', ''),
            'date': row.get('date', ''),
        }

# Read matches
with open(input_file) as f:
    reader = csv.DictReader(f)
    matches = list(reader)

# Filter for HIGH confidence with valid addresses
high_conf = [m for m in matches 
             if m.get('Confidence', '').upper() == 'HIGH' 
             and is_valid_address(m.get('Property Address', ''))]

print(f"Total records: {len(matches)}")
print(f"HIGH confidence with valid address: {len(high_conf)}")

# Group by person (to pick best address per person)
by_person = defaultdict(list)
for m in high_conf:
    key = m.get('Original Name', '')
    by_person[key].append(m)

print(f"Unique individuals: {len(by_person)}")

# Create final lead list - one best address per person
leads = []
for name, records in by_person.items():
    # Pick address in priority order: Port Orange, Daytona Beach, New Smyrna, etc (coverage area)
    PRIORITY_CITIES = ['PORT ORANGE', 'DAYTONA BEACH', 'NEW SMYRNA BEACH', 'ORMOND BEACH', 'DELAND', 'DELTONA']
    
    # Sort by city priority
    def city_priority(r):
        city = r.get('City', '').upper()
        for i, c in enumerate(PRIORITY_CITIES):
            if c in city:
                return i
        return 99
    
    records.sort(key=city_priority)
    best = records[0]
    
    # Get instrument/date from original lookup
    info = name_to_info.get(name, {})
    
    # Parse name
    parts = name.replace('"', '').split(',')
    last_name = parts[0].strip() if parts else ''
    first_name = parts[1].strip() if len(parts) > 1 else ''
    
    leads.append({
        'first_name': first_name,
        'last_name': last_name,
        'full_name': f"{first_name} {last_name}",
        'address': best.get('Property Address', ''),
        'city': best.get('City', ''),
        'state': 'FL',
        'date_filed': info.get('date', ''),
        'instrument': info.get('instrument', ''),
        'parcel_id': best.get('Parcel ID', ''),
        'lead_type': 'pre-foreclosure'
    })

# Sort by date filed descending
leads.sort(key=lambda x: x['date_filed'], reverse=True)

# Write output
with open(output_file, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=[
        'first_name', 'last_name', 'full_name', 'address', 'city', 'state', 
        'date_filed', 'instrument', 'parcel_id', 'lead_type'
    ])
    writer.writeheader()
    writer.writerows(leads)

print(f"\n{'='*50}")
print(f"🎯 FINAL LIS PENDENS LEADS: {len(leads)}")
print(f"{'='*50}")
print(f"Date range: {min(l['date_filed'] for l in leads if l['date_filed'])} to {max(l['date_filed'] for l in leads if l['date_filed'])}")

# City breakdown
cities = defaultdict(int)
for l in leads:
    cities[l['city']] += 1
print(f"\nBy city:")
for city, count in sorted(cities.items(), key=lambda x: -x[1])[:8]:
    print(f"  {city}: {count}")

# Save summary
print(f"\n📁 Saved to: {output_file}")

# Show sample
print(f"\n{'='*50}")
print("NEWEST 20 LEADS")
print(f"{'='*50}")
for lead in leads[:20]:
    print(f"{lead['date_filed']} | {lead['full_name'][:22]:<22} | {lead['address']}, {lead['city']}")
