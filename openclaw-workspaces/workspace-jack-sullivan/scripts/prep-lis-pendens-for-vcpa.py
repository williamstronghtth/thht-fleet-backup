#!/usr/bin/env python3
"""Prepare lis pendens names for VCPA matching."""

import csv

input_file = 'leads/lis-pendens/lis-pendens-owners-2026-02-24.csv'
output_file = 'leads/lis-pendens/lis-pendens-names-for-vcpa.csv'

# Read the leads
with open(input_file) as f:
    reader = csv.DictReader(f)
    leads = list(reader)

# Write names for VCPA matching (one per row, include instrument for tracking)
with open(output_file, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['Name', 'source', 'instrument', 'date'])
    writer.writeheader()
    
    for lead in leads:
        if lead['name_1']:
            writer.writerow({
                'Name': lead['name_1'],
                'source': 'lis_pendens',
                'instrument': lead['instrument'],
                'date': lead['date']
            })
        if lead['name_2']:
            writer.writerow({
                'Name': lead['name_2'],
                'source': 'lis_pendens',
                'instrument': lead['instrument'],
                'date': lead['date']
            })

# Count
with open(output_file) as f:
    count = sum(1 for _ in f) - 1  # minus header

print(f"Prepared {count} names for VCPA matching from {len(leads)} LP filings")
print(f"Output: {output_file}")
