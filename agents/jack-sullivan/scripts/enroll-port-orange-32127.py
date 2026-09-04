#!/usr/bin/env python3
"""
Enroll Port Orange 32127 absentee owners into the Fly In cadence.
Rules:
  - Skip LLCs, LPs, Inc, trusts, and other non-person entities
  - Skip leads with no email
  - Dedupe against existing leads.csv by email AND property address
  - Add new leads at Touch 1, enrolled today
"""

import csv
import re
import sys
from datetime import date

INBOX_CSV = "/root/agents/jack-sullivan/workspace/inbox/Port Orange Absentee - Sheet1 (1).csv"
LEADS_CSV = "/root/agents/jack-sullivan/workspace/campaigns/fly-in-absentee/leads.csv"
TODAY = date.today().isoformat()

# Patterns that indicate a non-person entity
ENTITY_PATTERNS = re.compile(
    r'\b(llc|l\.l\.c|lp|l\.p\.|inc|corp|trust|tr\b|properties|assets|propco|borrower|construction|county|church|bishop)\b',
    re.IGNORECASE
)

def is_entity(first_name, last_name):
    full = f"{first_name} {last_name}".strip()
    return bool(ENTITY_PATTERNS.search(full))

def normalize_address(street, city, state, zipcode):
    return f"{street.strip().upper()} {city.strip().upper()} {state.strip().upper()} {zipcode.strip()}"

def load_existing_leads():
    existing_emails = set()
    existing_addresses = set()
    with open(LEADS_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('email'):
                existing_emails.add(row['email'].strip().lower())
            if row.get('property_address'):
                existing_addresses.add(row['property_address'].strip().upper())
    return existing_emails, existing_addresses

def clean_phone(raw):
    digits = re.sub(r'\D', '', raw or '')
    return digits if len(digits) >= 10 else ''

def main():
    existing_emails, existing_addresses = load_existing_leads()
    print(f"Existing leads: {len(existing_emails)} emails, {len(existing_addresses)} addresses")

    new_leads = []
    skipped_entity = []
    skipped_no_email = []
    skipped_duplicate = []

    with open(INBOX_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            first = row.get('First Name', '').strip()
            last = row.get('Last Name', '').strip()
            email = row.get('Email', '').strip()
            phone = clean_phone(row.get('Phone Number', ''))
            street = row.get('Address Street', '').strip()
            city = row.get('City', '').strip()
            state = row.get('State', '').strip()
            zipcode = row.get('Zip', '').strip()

            full_name = f"{first} {last}".strip()
            address_normalized = normalize_address(street, city, state, zipcode)

            # Skip non-person entities
            if is_entity(first, last):
                skipped_entity.append(full_name)
                continue

            # Skip no email
            if not email:
                skipped_no_email.append(f"{full_name} @ {street}")
                continue

            # Dedupe by email
            if email.lower() in existing_emails:
                skipped_duplicate.append(f"{full_name} ({email}) — duplicate email")
                continue

            # Dedupe by address
            if address_normalized in existing_addresses:
                skipped_duplicate.append(f"{full_name} @ {street} — duplicate address")
                continue

            new_leads.append({
                'first_name': first,
                'last_name': last,
                'email': email,
                'phone': phone,
                'property_address': address_normalized,
                'enrolled_date': TODAY,
                'last_touch_date': '',
                'current_touch': '0',
                'status': 'active',
                'crm_id': '',
            })

            # Track to avoid intra-file dupes
            existing_emails.add(email.lower())
            existing_addresses.add(address_normalized)

    print(f"\nResults:")
    print(f"  New leads to enroll: {len(new_leads)}")
    print(f"  Skipped (entity/LLC): {len(skipped_entity)}")
    print(f"  Skipped (no email): {len(skipped_no_email)}")
    print(f"  Skipped (duplicate): {len(skipped_duplicate)}")

    if skipped_entity:
        print(f"\nEntities skipped:")
        for e in skipped_entity:
            print(f"  - {e}")

    if skipped_no_email:
        print(f"\nNo email (skipped):")
        for e in skipped_no_email:
            print(f"  - {e}")

    if skipped_duplicate:
        print(f"\nDuplicates skipped:")
        for e in skipped_duplicate:
            print(f"  - {e}")

    if not new_leads:
        print("\nNo new leads to add. Exiting.")
        sys.exit(0)

    print(f"\nNew leads preview (first 5):")
    for lead in new_leads[:5]:
        print(f"  {lead['first_name']} {lead['last_name']} | {lead['email']} | {lead['property_address']}")

    # Append to leads.csv
    with open(LEADS_CSV, 'a', newline='', encoding='utf-8') as f:
        fieldnames = ['first_name','last_name','email','phone','property_address',
                      'enrolled_date','last_touch_date','current_touch','status','crm_id']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        for lead in new_leads:
            writer.writerow(lead)

    print(f"\nDone. {len(new_leads)} new leads appended to {LEADS_CSV}")

if __name__ == '__main__':
    main()
