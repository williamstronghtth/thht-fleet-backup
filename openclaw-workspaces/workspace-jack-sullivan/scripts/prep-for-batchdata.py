#!/usr/bin/env python3
"""Prep lis pendens leads for BatchData skip tracing."""

import csv

input_file = 'leads/lis-pendens/lis-pendens-final-leads.csv'
output_file = 'leads/lis-pendens/batchdata-lis-pendens-64.csv'

# Volusia County zip codes by city (common ones)
ZIP_LOOKUP = {
    'PORT ORANGE': '32127',
    'DAYTONA BEACH': '32114',
    'NEW SMYRNA BEACH': '32168',
    'ORMOND BEACH': '32174',
    'DELAND': '32720',
    'DELTONA': '32725',
    'DEBARY': '32713',
    'EDGEWATER': '32132',
    'HOLLY HILL': '32117',
    'SOUTH DAYTONA': '32119',
    'ORANGE CITY': '32763',
    'PIERSON': '32180',
    'ENTERPRISE': '32725',
    'LAKE HELEN': '32744',
}

# Read leads
with open(input_file) as f:
    reader = csv.DictReader(f)
    leads = list(reader)

# Write BatchData format
with open(output_file, 'w', newline='') as f:
    writer = csv.writer(f)
    # Header per Chris's format
    writer.writerow(['Last Name', 'First Name', 'Property Address', 'Property City', 'Property State', 'Property Zip'])
    
    for lead in leads:
        city = lead['city'].upper()
        zip_code = ZIP_LOOKUP.get(city, '')
        
        writer.writerow([
            lead['last_name'],
            lead['first_name'],
            lead['address'],
            lead['city'],
            'FL',
            zip_code
        ])

print(f"✅ BatchData file ready: {output_file}")
print(f"   {len(leads)} leads")

# Show first few rows
print("\nPreview:")
with open(output_file) as f:
    for i, line in enumerate(f):
        if i < 8:
            print(f"  {line.strip()}")
