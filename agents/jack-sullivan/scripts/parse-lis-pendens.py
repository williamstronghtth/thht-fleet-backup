#!/usr/bin/env python3
"""Parse lis pendens XLS exports and extract property owner leads."""

import re
import csv
from pathlib import Path
from collections import defaultdict

# Patterns to filter out (lenders, HOAs, government, etc.)
SKIP_PATTERNS = [
    # Banks and lenders
    r'\bBANK\b', r'\bMORTGAGE\b', r'\bLOAN\b', r'\bSERVICING\b', r'\bFUNDING\b',
    r'\bTRUST\b', r'\bCREDIT\b', r'\bFINANCE\b', r'\bLENDING\b', r'\bCAPITAL\b',
    # HOAs and associations
    r'HOMEOWNERS ASSOCIATION', r'ASSOCIATION INC', r'OWNERS ASSOCIATION',
    r'CONDOMINIUM ASSN', r'CONDO ASSN', r'\bHOA\b',
    # Government entities
    r'UNITED STATES', r'STATE OF FLORIDA', r'SECRETARY OF', r'COMMISSIONER OF',
    r'CITY OF', r'COUNTY', r'\bCLERK\b', r'DEPARTMENT OF',
    # Corporate/institutional
    r'FEDERAL HOME', r'FREDDIE MAC', r'FANNIE MAE', r'FHA\b', r'VA\b',
    r'HOUSING AND URBAN', r'RURAL HOUSING', r'VETERANS AFFAIRS',
    # Finance companies
    r'ROCKET MORTGAGE', r'PENNYMAC', r'NATIONSTAR', r'NEWREZ', r'FREEDOM MORTGAGE',
    r'CARRINGTON', r'SHELLPOINT', r'LAKEVIEW LOAN', r'PLANET HOME',
    r'PHH\b', r'GUILD MORTGAGE', r'TRUIST', r'WELLS FARGO', r'JPMORGAN',
    r'DEUTSCHE BANK', r'U S BANK', r'CITIBANK', r'REGIONS BANK',
    # Legal/corporate structures
    r'\bLLC\b.*(?:MORTGAGE|LOAN|FINANCE|FUNDING|CAPITAL|TRUST)',
    r'(?:MORTGAGE|LOAN|FINANCE|FUNDING|CAPITAL|TRUST).*\bLLC\b',
    r'\bINC\b.*(?:MORTGAGE|LOAN|FINANCE)',
    r'CERTIFICATE', r'PASS.?THROUGH', r'ASSET.?BACKED',
    # Other entities to skip
    r'LVNV FUNDING', r'ISPC', r'SYNCHRONY', r'DISCOVER BANK',
    r'GOODLEAP', r'SERVICE FINANCE', r'SUNNOVA',
]

def should_skip(name):
    """Check if name matches skip patterns."""
    name_upper = name.upper()
    for pattern in SKIP_PATTERNS:
        if re.search(pattern, name_upper):
            return True
    return False

def parse_html_table(content):
    """Extract rows from HTML table in XLS file."""
    records = []
    
    # Find all table rows
    row_pattern = r'<tr[^>]*>(.*?)</tr>'
    cell_pattern = r'<td[^>]*>\s*(.*?)\s*</td>'
    
    rows = re.findall(row_pattern, content, re.DOTALL | re.IGNORECASE)
    
    for row in rows:
        cells = re.findall(cell_pattern, row, re.DOTALL | re.IGNORECASE)
        if len(cells) >= 9:
            # Columns: View, Instrument, Date, Book/Page, DocType, Name, Legal, Status, Direction
            instrument = cells[1].strip()
            date = cells[2].strip()
            doc_type = cells[4].strip()
            name = cells[5].strip()
            legal = cells[6].strip()
            status = cells[7].strip()
            direction = cells[8].strip()
            
            if instrument and name and direction:
                records.append({
                    'instrument': instrument,
                    'date': date,
                    'doc_type': doc_type,
                    'name': name,
                    'legal': legal,
                    'status': status,
                    'direction': direction
                })
    
    return records

def main():
    files = [
        '/root/.openclaw/media/inbound/file_3---2b34def7-2cf2-4ca3-82e8-d7a65ce2d058.xls',
        '/root/.openclaw/media/inbound/file_4---c13875e5-4366-44ba-8275-e1fd0c051efe.xls'
    ]
    
    all_records = []
    
    for f in files:
        print(f"Processing: {f}")
        with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
            content = fp.read()
            records = parse_html_table(content)
            all_records.extend(records)
            print(f"  Found {len(records)} rows")
    
    print(f"\nTotal raw records: {len(all_records)}")
    
    # Filter for Direction = R (defendants/owners)
    defendants = [r for r in all_records if r['direction'].strip() == 'R']
    print(f"Direction R (defendants): {len(defendants)}")
    
    # Filter out lenders, HOAs, government, etc.
    owners = [r for r in defendants if not should_skip(r['name'])]
    print(f"After filtering entities: {len(owners)}")
    
    # Group by instrument number (each LP filing)
    by_instrument = defaultdict(list)
    for r in owners:
        by_instrument[r['instrument']].append(r)
    
    print(f"Unique LP filings with owner matches: {len(by_instrument)}")
    
    # Deduplicate names per instrument (same person listed multiple ways)
    leads = []
    for instrument, records in by_instrument.items():
        # Get first record for metadata
        first = records[0]
        
        # Collect unique names (normalize)
        names = set()
        for r in records:
            # Normalize: strip suffixes like JR, SR, II, III
            name = r['name'].upper()
            name = re.sub(r'\s+(JR|SR|II|III|IV)$', '', name)
            names.add(name)
        
        # Take the longest version of similar names
        unique_names = list(names)
        
        leads.append({
            'instrument': instrument,
            'date': first['date'],
            'legal': first['legal'],
            'names': '; '.join(sorted(unique_names)[:3]),  # Max 3 names
            'name_count': len(unique_names)
        })
    
    print(f"Final lead count: {len(leads)}")
    
    # Sort by date descending (newest first)
    leads.sort(key=lambda x: x['date'], reverse=True)
    
    # Write CSV
    output = Path('/root/.openclaw/workspace-jack-sullivan/leads/lis-pendens/lis-pendens-leads-2026-02-24.csv')
    with open(output, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['instrument', 'date', 'names', 'legal', 'name_count'])
        writer.writeheader()
        writer.writerows(leads)
    
    print(f"\nSaved to: {output}")
    
    # Show sample
    print("\n=== SAMPLE LEADS (newest 10) ===")
    for lead in leads[:10]:
        print(f"{lead['date']} | {lead['names'][:50]}... | {lead['legal'][:40]}...")

if __name__ == '__main__':
    main()
