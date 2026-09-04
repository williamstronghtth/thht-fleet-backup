#!/usr/bin/env python3
"""
Scrape 2025-26 NBA betting lines from scoresandodds.com and store in DuckDB.
Scrapes once, stores forever. Re-run to pick up new dates only.
"""

import re
import sys
import time
import duckdb
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

DB_PATH = 'data/nbadb/nba.duckdb'
SEASON = 2026
SEASON_START = '2025-10-21'
DELAY = 0.3

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


def parse_game_block(block, date_str):
    """Parse a single game block text into a dict."""
    team_re = r'(\d{3})\s+((?:Trail Blazers|76ers|[\w]+))\s+(\d+-\d+)\s+(\d+)\s+'
    parts = list(re.finditer(team_re, block))
    if len(parts) < 2:
        return None

    away_match, home_match = parts[0], parts[1]
    away_rest = block[away_match.end():home_match.start()]
    home_rest = block[home_match.end():]

    away_team = away_match.group(2).strip()
    home_team = home_match.group(2).strip()
    away_score = int(away_match.group(4))
    home_score = int(home_match.group(4))

    # Extract spread: signed numbers followed by juice, excluding totals (o/u prefix)
    away_spread_vals = re.findall(r'(?<![ou\d])([+-]\d+\.?\d*)\s+-\d+', away_rest)
    home_spread_vals = re.findall(r'(?<![ou\d])([+-]\d+\.?\d*)\s+-\d+', home_rest)

    away_spread = float(away_spread_vals[0]) if away_spread_vals else None
    home_spread = float(home_spread_vals[0]) if home_spread_vals else None

    # Total
    total_match = re.search(r'[ou](\d+\.?\d*)', away_rest + ' ' + home_rest)
    total = float(total_match.group(1)) if total_match else None

    # Determine who's favored and the spread magnitude
    if home_spread is not None and home_spread < 0:
        whos_favored = 'home'
        spread_val = abs(home_spread)
    elif away_spread is not None and away_spread < 0:
        whos_favored = 'away'
        spread_val = abs(away_spread)
    else:
        whos_favored = None
        spread_val = None

    away_abbr = TEAM_MAP.get(away_team, away_team.lower()[:3])
    home_abbr = TEAM_MAP.get(home_team, home_team.lower()[:3])

    return {
        'season': SEASON,
        'date': date_str,
        'regular': True,
        'playoffs': False,
        'away': away_abbr,
        'home': home_abbr,
        'score_away': away_score,
        'score_home': home_score,
        'whos_favored': whos_favored,
        'spread': spread_val,
        'total': total,
    }


def scrape_date(date_str):
    """Fetch and parse all games for a date."""
    url = f'https://www.scoresandodds.com/nba?date={date_str}'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, 'html.parser')
    text = soup.get_text(separator=' ', strip=True)

    games = []
    blocks = text.split('Last play:')
    for block in blocks[:-1]:
        # Find the relevant part after "FINAL"
        idx = block.rfind('FINAL')
        if idx >= 0:
            block = block[idx:]
        result = parse_game_block(block, date_str)
        if result:
            games.append(result)
    return games


def main():
    con = duckdb.connect(DB_PATH)

    # Clear bad data (no spreads)
    con.execute(f"DELETE FROM betting_lines WHERE season = {SEASON}")

    start = datetime.strptime(SEASON_START, '%Y-%m-%d')
    end = datetime.now() - timedelta(days=1)
    all_dates = pd.date_range(start, end)

    print(f'Scraping {len(all_dates)} dates...')

    all_games = []
    no_games_dates = 0

    for i, d in enumerate(all_dates):
        date_str = d.strftime('%Y-%m-%d')
        try:
            games = scrape_date(date_str)
            if games:
                all_games.extend(games)
            else:
                no_games_dates += 1
        except Exception as e:
            pass

        if (i + 1) % 10 == 0:
            with_spread = sum(1 for g in all_games if g['spread'] is not None)
            print(f'  {i+1}/{len(all_dates)} dates | {len(all_games)} games ({with_spread} with spread)')

        time.sleep(DELAY)

    print(f'\nTotal: {len(all_games)} games, {no_games_dates} dates with no games')
    with_spread = sum(1 for g in all_games if g['spread'] is not None)
    print(f'Games with spreads: {with_spread}/{len(all_games)}')

    if all_games:
        df = pd.DataFrame(all_games)
        db_cols = [r[0] for r in con.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_name = 'betting_lines' ORDER BY ordinal_position"
        ).fetchall()]
        for col in db_cols:
            if col not in df.columns:
                df[col] = None
        df = df[db_cols]

        con.execute("INSERT INTO betting_lines SELECT * FROM df")
        count = con.execute(f"SELECT COUNT(*) FROM betting_lines WHERE season = {SEASON}").fetchone()[0]
        with_sp = con.execute(f"SELECT COUNT(*) FROM betting_lines WHERE season = {SEASON} AND spread IS NOT NULL").fetchone()[0]
        print(f'Stored {count} lines ({with_sp} with spreads)')

    con.close()
    print('Done!')


if __name__ == '__main__':
    main()
