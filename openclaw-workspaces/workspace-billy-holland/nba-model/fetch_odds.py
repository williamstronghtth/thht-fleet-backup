#!/usr/bin/env python3
"""
Hard Rock Bet Odds Scraper
Fetches NBA spreads from VegasInsider (includes Hard Rock column)
"""

import requests
import re
import json
import os
from datetime import datetime

DATA_DIR = os.path.dirname(os.path.abspath(__file__)) + "/data"

# Team name mapping
TEAM_TO_ABBREV = {
    'hawks': 'ATL', 'celtics': 'BOS', 'nets': 'BKN', 'hornets': 'CHA',
    'bulls': 'CHI', 'cavaliers': 'CLE', 'mavericks': 'DAL', 'nuggets': 'DEN',
    'pistons': 'DET', 'warriors': 'GSW', 'rockets': 'HOU', 'pacers': 'IND',
    'clippers': 'LAC', 'lakers': 'LAL', 'grizzlies': 'MEM', 'heat': 'MIA',
    'bucks': 'MIL', 'timberwolves': 'MIN', 'pelicans': 'NOP', 'knicks': 'NYK',
    'thunder': 'OKC', 'magic': 'ORL', '76ers': 'PHI', 'sixers': 'PHI',
    'suns': 'PHX', 'trail blazers': 'POR', 'blazers': 'POR', 'kings': 'SAC',
    'spurs': 'SAS', 'raptors': 'TOR', 'jazz': 'UTA', 'wizards': 'WAS'
}


def fetch_hardrock_lines():
    """
    Scrape NBA spreads from VegasInsider, extract Hard Rock column
    """
    url = "https://www.vegasinsider.com/nba/odds/las-vegas/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        text = resp.text
        
        games = []
        
        # VegasInsider format in the scraped markdown:
        # 531 [Knicks] +1.5 -110 [...spreads...] [HR spread] [...] 
        # Hard Rock appears after several book columns
        
        # Find all lines with rotation numbers and team names
        # Pattern: rotation# [TeamName] followed by spreads
        
        lines = text.split('\n')
        game_buffer = []
        
        for line in lines:
            # Look for rotation number + team pattern
            # Example: "531 [Knicks]" or just team name in brackets
            
            for team_name, abbrev in TEAM_TO_ABBREV.items():
                # Check if team name appears in this line
                if f'[{team_name.title()}]' in line or f'[{team_name}]' in line.lower():
                    # Extract all spread values from this line
                    # Pattern: [+/-X.X -1XX +] where X.X is the spread
                    spreads = re.findall(r'\[([+-]?\d+\.?\d*)\s+-\d+\s+\+\]', line)
                    
                    if not spreads:
                        # Try alternate pattern without brackets
                        spreads = re.findall(r'([+-]\d+\.?\d*)\s+-1[01]\d', line)
                    
                    if spreads and len(spreads) >= 5:
                        # Hard Rock is typically the 6th book (index 5)
                        # Books order: Open, Bet365, BetMGM, DraftKings, Caesars, FanDuel, HardRock
                        hr_index = 5 if len(spreads) > 5 else len(spreads) - 1
                        hr_spread = float(spreads[hr_index])
                        
                        game_buffer.append({
                            'team': abbrev,
                            'spread': hr_spread
                        })
                        
                        # If we have two teams, make a game
                        if len(game_buffer) == 2:
                            games.append({
                                'away': game_buffer[0]['team'],
                                'home': game_buffer[1]['team'],
                                'away_spread': game_buffer[0]['spread'],
                                'home_spread': game_buffer[1]['spread'],
                                'hr_line': game_buffer[1]['spread']
                            })
                            game_buffer = []
                    break
        
        # Only save if we found games (don't overwrite manual entries)
        if games:
            output = {
                'fetched_at': datetime.now().isoformat(),
                'source': 'vegasinsider_hardrock',
                'games': games
            }
            
            os.makedirs(DATA_DIR, exist_ok=True)
            with open(f"{DATA_DIR}/hardrock_lines.json", 'w') as f:
                json.dump(output, f, indent=2)
        
        return games
        
    except Exception as e:
        print(f"Error fetching odds: {e}")
        return []


def manual_update_lines(games_dict):
    """
    Manually update Hard Rock lines
    games_dict format: {'away@home': spread, ...}
    Example: {'NYK@DET': -1, 'MIA@BOS': -6.5}
    spread is HOME team spread (negative = home favored)
    """
    games = []
    for matchup, hr_line in games_dict.items():
        away, home = matchup.split('@')
        games.append({
            'away': away.strip().upper(),
            'home': home.strip().upper(),
            'hr_line': float(hr_line)
        })
    
    output = {
        'fetched_at': datetime.now().isoformat(),
        'source': 'manual',
        'games': games
    }
    
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(f"{DATA_DIR}/hardrock_lines.json", 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"Saved {len(games)} games")
    return games


def get_hardrock_line(home_team, away_team):
    """
    Get Hard Rock spread for a specific game
    Returns home team spread (negative = home favored)
    """
    try:
        with open(f"{DATA_DIR}/hardrock_lines.json", 'r') as f:
            data = json.load(f)
        
        for game in data.get('games', []):
            if game['home'] == home_team and game['away'] == away_team:
                return game['hr_line']
            if game['home'] == away_team and game['away'] == home_team:
                return -game['hr_line']
        
        return None
    except:
        return None


def load_lines():
    """Load saved Hard Rock lines"""
    try:
        with open(f"{DATA_DIR}/hardrock_lines.json", 'r') as f:
            return json.load(f)
    except:
        return {'games': []}


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--manual':
        # Manual mode: python fetch_odds.py --manual "NYK@DET:-1" "MIA@BOS:-6.5"
        games = {}
        for arg in sys.argv[2:]:
            if ':' in arg:
                matchup, spread = arg.rsplit(':', 1)
                games[matchup] = float(spread)
        if games:
            manual_update_lines(games)
        else:
            print("Usage: python fetch_odds.py --manual 'NYK@DET:-1' 'MIA@BOS:-6.5'")
    else:
        print("Fetching Hard Rock lines from VegasInsider...")
        games = fetch_hardrock_lines()
        
        if games:
            print(f"\nFound {len(games)} games:")
            for g in games:
                print(f"  {g['away']} @ {g['home']}: HR Line = {g['hr_line']:+.1f}")
        else:
            print("Auto-scrape didn't find games. Use --manual mode:")
            print("  python fetch_odds.py --manual 'NYK@DET:-1' 'MIA@BOS:-6.5'")
