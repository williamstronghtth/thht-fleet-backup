#!/usr/bin/env python3
"""
Scrape 2025-26 NBA betting lines from scoresandodds.com and store in DuckDB.

Scrapes once, stores forever. Run periodically to pick up new games.
"""

import re
import sys
import time
import urllib.request
import duckdb
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

DB_PATH = 'data/nbadb/nba.duckdb'
SEASON = 2026  # scoresandodds uses calendar year of playoffs
SEASON_START = '2025-10-21'
DELAY = 0.5  # seconds between requests

# Team name mapping (scoresandodds names → NBA abbreviations)
TEAM_MAP = {
    'Thunder': 'okc', 'Timberwolves': 'min', 'Celtics': 'bos', 'Cavaliers': 'cle',
    'Rockets': 'hou', 'Nuggets': 'den', 'Warriors': 'gsw', 'Knicks': 'ny',
    'Bucks': 'mil', 'Lakers': 'lal', 'Clippers': 'lac', 'Suns': 'phx',
    'Grizzlies': 'mem', 'Mavericks': 'dal', 'Heat': 'mia', 'Pacers': 'ind',
    'Hawks': 'atl', '76ers': 'phi', 'Kings': 'sac', 'Spurs': 'sa',
    'Magic': 'orl', 'Nets': 'bkn', 'Bulls': 'chi', 'Pistons': 'det',
    'Raptors': 'tor', 'Pelicans': 'no', 'Hornets': 'cha', 'Wizards': 'wsh',
    'Trail Blazers': 'por', 'Jazz': 'utah',
}


def scrape_date(date_str: str) -> list:
    """Scrape betting lines for a single date."""
    url = f'https://www.scoresandodds.com/nba?date={date_str}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    resp = urllib.request.urlopen(req, timeout=15)
    text = resp.read().decode('utf-8')
    
    games = []
    
    # Split by "Last play:" to get individual game blocks
    blocks = text.split('Last play:')
    
    for block in blocks[:-1]:  # last block is footer
        try:
            # Find team lines: "number TeamName record score"
            # Pattern: 3-digit number, team name, W-L record, score
            team_pattern = r'(\d{3})\s+([\w\s]+?)\s+(\d+-\d+)\s+(\d+)'
            teams = re.findall(team_pattern, block)
            
            if len(teams) < 2:
                continue
            
            away_num, away_name, away_rec, away_score = teams[0]
            home_num, home_name, home_rec, home_score = teams[1]
            
            away_name = away_name.strip()
            home_name = home_name.strip()
            
            # Find spread: look for pattern like "-8.5 -110" or "+8.5 -110"
            # The home team's spread appears after the home team's score
            spread_pattern = r'([+-]\d+\.?\d*)\s+-\d+'
            spreads = re.findall(spread_pattern, block)
            
            # Find total: look for "o/u" followed by number
            total_pattern = r'[ou](\d+\.?\d*)'
            totals = re.findall(total_pattern, block)
            
            # The opening spread for home team - find it near the home team data
            # In the scraped format, spreads appear after scores
            # Away team gets + spread, home team gets - spread (if home favored)
            home_spread = None
            if len(spreads) >= 2:
                # First spread near away team, second near home team
                # The one that's negative is the favorite
                for s in spreads:
                    val = float(s)
                    if val < 0:
                        home_spread = val
                        break
                if home_spread is None:
                    # Away team is favored
                    home_spread = float(spreads[1]) if len(spreads) > 1 else None
            
            total = float(totals[0]) if totals else None
            
            # Determine who's favored
            if home_spread is not None:
                if home_spread < 0:
                    whos_favored = 'home'
                    spread_val = abs(home_spread)
                else:
                    whos_favored = 'away'
                    spread_val = abs(home_spread)
            else:
                whos_favored = None
                spread_val = None
            
            away_abbr = TEAM_MAP.get(away_name, away_name.lower()[:3])
            home_abbr = TEAM_MAP.get(home_name, home_name.lower()[:3])
            
            games.append({
                'season': SEASON,
                'date': date_str,
                'regular': True,
                'playoffs': False,
                'away': away_abbr,
                'home': home_abbr,
                'score_away': int(away_score),
                'score_home': int(home_score),
                'whos_favored': whos_favored,
                'spread': spread_val,
                'total': total,
            })
        except Exception as e:
            continue
    
    return games


def main():
    con = duckdb.connect(DB_PATH)
    
    # Check what dates we already have
    existing = con.execute(
        f"SELECT DISTINCT date FROM betting_lines WHERE season = {SEASON}"
    ).fetchdf()
    existing_dates = set(existing['date'].tolist()) if len(existing) > 0 else set()
    
    # Generate all dates from season start to yesterday
    start = datetime.strptime(SEASON_START, '%Y-%m-%d')
    end = datetime.now() - timedelta(days=1)
    all_dates = pd.date_range(start, end)
    
    # Filter to dates we don't have
    new_dates = [d for d in all_dates if d.strftime('%Y-%m-%d') not in existing_dates]
    
    print(f'Existing dates in DB: {len(existing_dates)}')
    print(f'New dates to scrape: {len(new_dates)}')
    
    if not new_dates:
        print('All caught up!')
        con.close()
        return
    
    all_games = []
    for i, d in enumerate(new_dates):
        date_str = d.strftime('%Y-%m-%d')
        try:
            games = scrape_date(date_str)
            all_games.extend(games)
            if (i + 1) % 10 == 0:
                print(f'  Scraped {i+1}/{len(new_dates)} dates ({len(all_games)} games total)')
        except Exception as e:
            print(f'  Error on {date_str}: {e}')
        time.sleep(DELAY)
    
    if not all_games:
        print('No games scraped')
        con.close()
        return
    
    df = pd.DataFrame(all_games)
    
    # Add missing columns with defaults
    for col in ['q1_away','q2_away','q3_away','q4_away','ot_away',
                'q1_home','q2_home','q3_home','q4_home','ot_home',
                'moneyline_away','moneyline_home','h2_spread','h2_total',
                'id_spread','id_total']:
        if col not in df.columns:
            df[col] = None
    
    # Reorder to match DB schema
    db_cols = [r[0] for r in con.execute(
        "SELECT column_name FROM information_schema.columns WHERE table_name = 'betting_lines' ORDER BY ordinal_position"
    ).fetchall()]
    
    for col in db_cols:
        if col not in df.columns:
            df[col] = None
    
    df = df[db_cols]
    
    # Insert
    con.execute(f"DELETE FROM betting_lines WHERE season = {SEASON}")
    con.execute("INSERT INTO betting_lines SELECT * FROM df")
    
    final_count = con.execute(f"SELECT COUNT(*) FROM betting_lines WHERE season = {SEASON}").fetchone()[0]
    print(f'\nInserted {len(df)} lines, total for season: {final_count}')
    
    con.close()
    print('Done!')


if __name__ == '__main__':
    main()
