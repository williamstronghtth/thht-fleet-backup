#!/usr/bin/env python3
"""Prepare lis pendens names for VCPA matching - proper format."""

import csv
import re

input_file = 'leads/lis-pendens/lis-pendens-owners-2026-02-24.csv'
output_file = 'leads/lis-pendens/lis-pendens-names-for-vcpa.csv'

def parse_name(full_name):
    """Parse 'LAST FIRST MIDDLE' into (last, first)."""
    parts = full_name.strip().upper().split()
    if len(parts) == 0:
        return None, None
    elif len(parts) == 1:
        return parts[0], ''
    else:
        # First part is last name, rest is first name(s)
        last = parts[0]
        first = ' '.join(parts[1:])
        # Remove suffixes from first name part
        first = re.sub(r'\s*(JR|SR|II|III|IV)$', '', first)
        return last, first.strip()

# Read the leads
with open(input_file) as f:
    reader = csv.DictReader(f)
    leads = list(reader)

# Write names for VCPA matching
seen = set()
with open(output_file, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['Last Name', 'First Name', 'source', 'instrument', 'date'])
    writer.writeheader()
    
    for lead in leads:
        for name_field in ['name_1', 'name_2']:
            if lead[name_field]:
                last, first = parse_name(lead[name_field])
                if last and first:
                    key = f"{last}|{first}"
                    if key not in seen:
                        seen.add(key)
                        writer.writerow({
                            'Last Name': last,
                            'First Name': first,
                            'source': 'lis_pendens',
                            'instrument': lead['instrument'],
                            'date': lead['date']
                        })

print(f"Prepared {len(seen)} unique names for VCPA matching")
print(f"Output: {output_file}")

# Show sample
print("\nSample names:")
with open(output_file) as f:
    for i, line in enumerate(f):
        if i < 6:
            print(f"  {line.strip()}")
