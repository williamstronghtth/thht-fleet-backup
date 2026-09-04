#!/usr/bin/env python3
"""
Scrape current NBA injury reports and store in DuckDB.

Sources: Basketball-Reference injury page
Stores in injury_report table for use by the predictor.
"""

import re
import duckdb
import requests
from datetime import datetime, date
from bs4 import BeautifulSoup

DB_PATH = 'data/nbadb/nba.duckdb'
INJURY_URL = 'https://www.basketball-reference.com/friv/injuries.fcgi'

# BBRef team abbr -> NBA API team abbr mapping (where they differ)
BBREF_TO_NBA = {
    'BRK': 'BKN',
    'CHO': 'CHA',
    'NOP': 'NOP',
    'PHO': 'PHX',
}


def create_injury_table(con):
    """Create injury_report table if it doesn't exist."""
    con.execute("""
        CREATE TABLE IF NOT EXISTS injury_report (
            player_id BIGINT,
            player_name VARCHAR,
            team_id BIGINT,
            team_abbreviation VARCHAR,
            status VARCHAR,
            injury_description VARCHAR,
            report_date DATE
        )
    """)


def resolve_player_id(con, player_name: str, team_abbr: str) -> int:
    """Try to resolve a player name to their NBA player_id."""
    # Try exact match on player_game_log (most reliable, has current roster)
    row = con.execute("""
        SELECT player_id FROM player_game_log 
        WHERE player_name = ? AND team_abbreviation = ?
        AND season = '2025-26'
        LIMIT 1
    """, [player_name, team_abbr]).fetchone()
    if row:
        return int(row[0])

    # Try fuzzy: last name match
    parts = player_name.split()
    if len(parts) >= 2:
        last = parts[-1]
        row = con.execute("""
            SELECT player_id FROM player_game_log 
            WHERE player_name LIKE ? AND team_abbreviation = ?
            AND season = '2025-26'
            LIMIT 1
        """, [f'%{last}', team_abbr]).fetchone()
        if row:
            return int(row[0])

    # Try player table
    row = con.execute("""
        SELECT id FROM player WHERE full_name = ? LIMIT 1
    """, [player_name]).fetchone()
    if row:
        return int(row[0])

    return 0


def resolve_team_id(con, team_abbr: str) -> int:
    """Resolve team abbreviation to team_id."""
    row = con.execute("""
        SELECT id FROM team WHERE abbreviation = ? LIMIT 1
    """, [team_abbr]).fetchone()
    if row:
        return int(row[0])
    return 0


def parse_status(description: str) -> str:
    """Extract status from the injury description text."""
    desc_lower = description.lower()
    if 'out for season' in desc_lower:
        return 'Out'
    if desc_lower.startswith('out '):
        return 'Out'
    if 'day to day' in desc_lower:
        # Check if listed as questionable, probable, etc.
        if 'questionable' in desc_lower:
            return 'Questionable'
        if 'probable' in desc_lower:
            return 'Probable'
        if 'doubtful' in desc_lower:
            return 'Doubtful'
        return 'Day-To-Day'
    if 'questionable' in desc_lower:
        return 'Questionable'
    if 'doubtful' in desc_lower:
        return 'Doubtful'
    if 'probable' in desc_lower:
        return 'Probable'
    return 'Unknown'


def scrape_injuries():
    """Scrape Basketball-Reference injury page and return list of injuries."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    resp = requests.get(INJURY_URL, headers=headers, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, 'html.parser')

    injuries = []
    # The page has a table with class "sortable"
    table = soup.find('table')
    if not table:
        print("Warning: Could not find injury table on page")
        return injuries

    tbody = table.find('tbody')
    if not tbody:
        print("Warning: No tbody found")
        return injuries

    for row in tbody.find_all('tr'):
        cells = row.find_all(['th', 'td'])
        if len(cells) < 4:
            continue

        # Cell 0: Player name (with link)
        player_cell = cells[0]
        player_link = player_cell.find('a')
        player_name = player_link.text.strip() if player_link else player_cell.text.strip()

        # Cell 1: Team (with link)
        team_cell = cells[1]
        team_link = team_cell.find('a')
        team_text = team_link.text.strip() if team_link else team_cell.text.strip()
        # Extract abbreviation from the link href if available
        team_abbr = ''
        if team_link and team_link.get('href'):
            # /teams/BOS/2026.html -> BOS
            match = re.search(r'/teams/(\w+)/', team_link['href'])
            if match:
                team_abbr = match.group(1)
                # Map BBRef abbreviations to NBA API ones
                team_abbr = BBREF_TO_NBA.get(team_abbr, team_abbr)

        # Cell 2: Date
        date_cell = cells[2]
        date_text = date_cell.text.strip()

        # Cell 3: Description
        desc_cell = cells[3]
        description = desc_cell.text.strip()

        status = parse_status(description)

        # Parse date
        try:
            report_date = datetime.strptime(date_text, '%a, %b %d, %Y').date()
        except ValueError:
            report_date = date.today()

        injuries.append({
            'player_name': player_name,
            'team_abbreviation': team_abbr,
            'team_name': team_text,
            'status': status,
            'injury_description': description,
            'report_date': report_date,
        })

    return injuries


def update_injury_table(injuries: list, db_path: str = DB_PATH):
    """Update the injury_report table with scraped data."""
    con = duckdb.connect(db_path)
    create_injury_table(con)

    # Clear old data and insert fresh
    con.execute("DELETE FROM injury_report")

    resolved = 0
    unresolved = []

    for inj in injuries:
        player_id = resolve_player_id(con, inj['player_name'], inj['team_abbreviation'])
        team_id = resolve_team_id(con, inj['team_abbreviation'])

        if player_id == 0:
            unresolved.append(inj['player_name'])

        con.execute("""
            INSERT INTO injury_report VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [
            player_id,
            inj['player_name'],
            team_id,
            inj['team_abbreviation'],
            inj['status'],
            inj['injury_description'],
            inj['report_date'],
        ])

        if player_id > 0:
            resolved += 1

    con.close()
    return resolved, unresolved


def main():
    print("Scraping NBA injury reports from Basketball-Reference...")
    injuries = scrape_injuries()
    print(f"Found {len(injuries)} injury entries")

    if not injuries:
        print("No injuries found. Exiting.")
        return

    # Show summary by status
    from collections import Counter
    status_counts = Counter(inj['status'] for inj in injuries)
    for status, count in sorted(status_counts.items()):
        print(f"  {status}: {count}")

    print("\nUpdating injury_report table...")
    resolved, unresolved = update_injury_table(injuries)
    print(f"Resolved {resolved}/{len(injuries)} player IDs")

    if unresolved:
        print(f"Unresolved players ({len(unresolved)}):")
        for name in unresolved[:10]:
            print(f"  - {name}")
        if len(unresolved) > 10:
            print(f"  ... and {len(unresolved) - 10} more")

    # Verify
    con = duckdb.connect(DB_PATH, read_only=True)
    count = con.execute("SELECT COUNT(*) FROM injury_report").fetchone()[0]
    out_count = con.execute(
        "SELECT COUNT(*) FROM injury_report WHERE status IN ('Out', 'Doubtful')"
    ).fetchone()[0]
    print(f"\nVerification: {count} total entries, {out_count} Out/Doubtful")

    # Show Out/Doubtful players
    print("\nPlayers currently OUT or DOUBTFUL:")
    rows = con.execute("""
        SELECT player_name, team_abbreviation, status, injury_description
        FROM injury_report
        WHERE status IN ('Out', 'Doubtful')
        ORDER BY team_abbreviation, player_name
    """).fetchdf()
    for _, r in rows.iterrows():
        print(f"  {r['team_abbreviation']} - {r['player_name']}: {r['status']}")

    con.close()


if __name__ == '__main__':
    main()
