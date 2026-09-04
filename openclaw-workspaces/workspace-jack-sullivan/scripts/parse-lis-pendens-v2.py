#!/usr/bin/env python3
"""Parse lis pendens XLS exports - refined version."""

import re
import csv
from pathlib import Path
from collections import defaultdict

# More comprehensive skip patterns
SKIP_PATTERNS = [
    # Banks and lenders
    r'\bBANK\b', r'\bMORTGAGE\b', r'\bLOAN\b', r'\bSERVICING\b', r'\bFUNDING\b',
    r'\bTRUST\b', r'\bCREDIT\b', r'\bFINANCE\b', r'\bLENDING\b', r'\bCAPITAL\b',
    # HOAs and associations  
    r'HOMEOWNERS ASSOCIATION', r'ASSOCIATION INC', r'OWNERS ASSOCIATION',
    r'CONDOMINIUM', r'\bHOA\b', r'COMMUNITY ASSN',
    # Government entities
    r'UNITED STATES', r'STATE OF FLORIDA', r'SECRETARY OF', r'COMMISSIONER OF',
    r'CITY OF', r'COUNTY', r'\bCLERK\b', r'DEPARTMENT OF', r'FLORIDA HOUSING',
    # Corporate/institutional
    r'FEDERAL HOME', r'FREDDIE MAC', r'FANNIE MAE', r'\bFHA\b', r'\bVA\b',
    r'HOUSING AND URBAN', r'RURAL HOUSING', r'VETERANS AFFAIRS',
    # Companies/investors
    r'\bLLC\b', r'\bINC\b', r'\bCORP\b', r'CORPORATION', r'COMPANY',
    r'COLLEGE', r'UNIVERSITY', r'INVESTMENTS',
    # Trusts that aren't personal
    r'(?<!LIVING )TRUST(?! AGREEMENT)',
    # Other
    r'MERS\b', r'MORTGAGE ELECTRONIC',
]

# Patterns that indicate a personal name (override skip)
PERSONAL_PATTERNS = [
    r'^[A-Z]+\s+[A-Z]+$',  # FIRST LAST
    r'^[A-Z]+\s+[A-Z]+\s+[A-Z]$',  # FIRST MIDDLE LAST
    r'^[A-Z]+\s+[A-Z]+\s+(JR|SR|II|III|IV)$',  # With suffix
]

def should_skip(name):
    """Check if name matches skip patterns."""
    name_upper = name.upper().strip()
    
    # Skip empty or very short
    if len(name_upper) < 5:
        return True
    
    # Skip single word (likely partial)
    if ' ' not in name_upper and len(name_upper) < 15:
        return True
        
    for pattern in SKIP_PATTERNS:
        if re.search(pattern, name_upper):
            return True
    return False

def parse_html_table(content):
    """Extract rows from HTML table in XLS file."""
    records = []
    
    row_pattern = r'<tr[^>]*>(.*?)</tr>'
    cell_pattern = r'<td[^>]*>\s*(.*?)\s*</td>'
    
    rows = re.findall(row_pattern, content, re.DOTALL | re.IGNORECASE)
    
    for row in rows:
        cells = re.findall(cell_pattern, row, re.DOTALL | re.IGNORECASE)
        if len(cells) >= 9:
            instrument = cells[1].strip()
            date = cells[2].strip()
            doc_type = cells[4].strip()
            name = re.sub(r'<[^>]+>', '', cells[5]).strip()  # Strip any HTML
            legal = re.sub(r'<[^>]+>', '', cells[6]).strip()
            status = cells[7].strip()
            direction = cells[8].strip()
            
            if instrument and name and direction and date:
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

def normalize_name(name):
    """Normalize a name for deduplication."""
    name = name.upper().strip()
    # Remove common suffixes
    name = re.sub(r'\s+(JR|SR|II|III|IV)$', '', name)
    # Remove middle initials
    name = re.sub(r'\s+[A-Z]$', '', name)
    name = re.sub(r'\s+[A-Z]\s+', ' ', name)
    return name

def extract_primary_name(names):
    """Get the best/primary name from a list of name variations."""
    if not names:
        return ''
    # Prefer longest name (usually most complete)
    sorted_names = sorted(names, key=len, reverse=True)
    return sorted_names[0]

def main():
    files = [
        '/root/.openclaw/media/inbound/file_3---2b34def7-2cf2-4ca3-82e8-d7a65ce2d058.xls',
        '/root/.openclaw/media/inbound/file_4---c13875e5-4366-44ba-8275-e1fd0c051efe.xls'
    ]
    
    all_records = []
    
    for f in files:
        with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
            content = fp.read()
            records = parse_html_table(content)
            all_records.extend(records)
    
    print(f"Total raw records: {len(all_records)}")
    
    # Filter for Direction = R (defendants/owners)
    defendants = [r for r in all_records if r['direction'].strip() == 'R']
    print(f"Direction R (defendants): {len(defendants)}")
    
    # Filter out institutions
    owners = [r for r in defendants if not should_skip(r['name'])]
    print(f"After filtering entities: {len(owners)}")
    
    # Group by instrument number
    by_instrument = defaultdict(list)
    for r in owners:
        by_instrument[r['instrument']].append(r)
    
    print(f"Unique LP filings with owner matches: {len(by_instrument)}")
    
    # Build final leads with deduplicated names
    leads = []
    for instrument, records in by_instrument.items():
        first = records[0]
        
        # Collect and deduplicate names
        name_variations = defaultdict(set)
        for r in records:
            normalized = normalize_name(r['name'])
            name_variations[normalized].add(r['name'])
        
        # Get primary names (most complete version)
        primary_names = []
        for normalized, variations in name_variations.items():
            primary = extract_primary_name(variations)
            primary_names.append(primary)
        
        # Limit to top 2 names
        primary_names = sorted(primary_names, key=len, reverse=True)[:2]
        
        leads.append({
            'instrument': instrument,
            'date': first['date'],
            'legal_desc': first['legal'][:100],  # Truncate long descriptions
            'name_1': primary_names[0] if len(primary_names) > 0 else '',
            'name_2': primary_names[1] if len(primary_names) > 1 else '',
            'full_legal': first['legal']
        })
    
    # Sort by date descending
    leads.sort(key=lambda x: x['date'], reverse=True)
    
    print(f"\n=== FINAL STATS ===")
    print(f"Total leads: {len(leads)}")
    
    # Date range
    dates = [l['date'] for l in leads if l['date']]
    if dates:
        print(f"Date range: {min(dates)} to {max(dates)}")
    
    # Write CSV
    output = Path('/root/.openclaw/workspace-jack-sullivan/leads/lis-pendens/lis-pendens-owners-2026-02-24.csv')
    with open(output, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['instrument', 'date', 'name_1', 'name_2', 'legal_desc'])
        writer.writeheader()
        for lead in leads:
            writer.writerow({
                'instrument': lead['instrument'],
                'date': lead['date'],
                'name_1': lead['name_1'],
                'name_2': lead['name_2'],
                'legal_desc': lead['legal_desc']
            })
    
    print(f"Saved to: {output}")
    
    # Show sample
    print("\n=== NEWEST 15 LEADS ===")
    for lead in leads[:15]:
        names = lead['name_1']
        if lead['name_2']:
            names += f" / {lead['name_2']}"
        print(f"{lead['date']} | {names[:40]:<40} | {lead['legal_desc'][:35]}...")

if __name__ == '__main__':
    main()
