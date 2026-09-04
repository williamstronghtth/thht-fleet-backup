#!/usr/bin/env python3
"""
NBA Data Fetcher
Scrapes team and player stats from Basketball Reference and NBA.com
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import json
import time
import os

# Constants
BR_BASE = "https://www.basketball-reference.com"
DATA_DIR = os.path.dirname(os.path.abspath(__file__)) + "/data"

TEAM_ABBREVS = {
    'Atlanta Hawks': 'ATL', 'Boston Celtics': 'BOS', 'Brooklyn Nets': 'BKN',
    'Charlotte Hornets': 'CHA', 'Chicago Bulls': 'CHI', 'Cleveland Cavaliers': 'CLE',
    'Dallas Mavericks': 'DAL', 'Denver Nuggets': 'DEN', 'Detroit Pistons': 'DET',
    'Golden State Warriors': 'GSW', 'Houston Rockets': 'HOU', 'Indiana Pacers': 'IND',
    'LA Clippers': 'LAC', 'Los Angeles Lakers': 'LAL', 'Memphis Grizzlies': 'MEM',
    'Miami Heat': 'MIA', 'Milwaukee Bucks': 'MIL', 'Minnesota Timberwolves': 'MIN',
    'New Orleans Pelicans': 'NOP', 'New York Knicks': 'NYK', 'Oklahoma City Thunder': 'OKC',
    'Orlando Magic': 'ORL', 'Philadelphia 76ers': 'PHI', 'Phoenix Suns': 'PHX',
    'Portland Trail Blazers': 'POR', 'Sacramento Kings': 'SAC', 'San Antonio Spurs': 'SAS',
    'Toronto Raptors': 'TOR', 'Utah Jazz': 'UTA', 'Washington Wizards': 'WAS'
}

def fetch_team_ratings(season="2026"):
    """
    Fetch team offensive/defensive ratings from Basketball Reference
    Returns DataFrame with ORtg, DRtg, Pace, etc.
    """
    url = f"{BR_BASE}/leagues/NBA_{season}_ratings.html"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        table = soup.find('table', {'id': 'ratings'})
        
        if table is None:
            print(f"Could not find ratings table for {season}")
            return None
            
        df = pd.read_html(str(table))[0]
        
        # Clean column names (handle multi-level headers)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = ['_'.join(col).strip() for col in df.columns.values]
        
        # Save to cache
        df.to_csv(f"{DATA_DIR}/team_ratings_{season}.csv", index=False)
        return df
        
    except Exception as e:
        print(f"Error fetching team ratings: {e}")
        return None


def fetch_team_stats_per100(season="2026"):
    """
    Fetch per-100 possession team stats
    """
    url = f"{BR_BASE}/leagues/NBA_{season}_per_poss.html"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        table = soup.find('table', {'id': 'per_poss-team'})
        
        if table is None:
            # Try alternate table id
            table = soup.find('table', {'id': 'team-stats-per_poss'})
        
        if table is None:
            print(f"Could not find per-100 stats table for {season}")
            return None
            
        df = pd.read_html(str(table))[0]
        df.to_csv(f"{DATA_DIR}/team_per100_{season}.csv", index=False)
        return df
        
    except Exception as e:
        print(f"Error fetching per-100 stats: {e}")
        return None


def fetch_todays_games():
    """
    Fetch today's NBA schedule from ESPN
    """
    today = datetime.now().strftime("%Y%m%d")
    url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={today}"
    
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        
        games = []
        for event in data.get('events', []):
            game = {
                'id': event['id'],
                'date': event['date'],
                'name': event['name'],
                'status': event['status']['type']['name']
            }
            
            for comp in event.get('competitions', []):
                for team in comp.get('competitors', []):
                    prefix = 'home' if team['homeAway'] == 'home' else 'away'
                    game[f'{prefix}_team'] = team['team']['abbreviation']
                    game[f'{prefix}_name'] = team['team']['displayName']
                    game[f'{prefix}_score'] = team.get('score', 0)
                    
                # Get odds if available
                for odds in comp.get('odds', []):
                    game['spread'] = odds.get('details', '')
                    game['over_under'] = odds.get('overUnder', 0)
                    break
                    
            games.append(game)
        
        # Save to file
        with open(f"{DATA_DIR}/todays_games.json", 'w') as f:
            json.dump(games, f, indent=2)
            
        return games
        
    except Exception as e:
        print(f"Error fetching today's games: {e}")
        return []


def fetch_team_schedule(team_abbrev, season="2026"):
    """
    Fetch recent game results for a team to calculate form/momentum
    """
    url = f"{BR_BASE}/teams/{team_abbrev}/{season}_games.html"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        table = soup.find('table', {'id': 'games'})
        
        if table:
            df = pd.read_html(str(table))[0]
            return df
            
    except Exception as e:
        print(f"Error fetching schedule for {team_abbrev}: {e}")
        
    return None


def calculate_rest_days(team_abbrev, game_date):
    """
    Calculate days since last game (0 = back-to-back)
    """
    # Simplified - would need schedule data
    # Return placeholder for now
    return 1


if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    
    print("Fetching team ratings...")
    ratings = fetch_team_ratings()
    if ratings is not None:
        print(f"Got {len(ratings)} teams")
        print(ratings.head())
    
    print("\nFetching today's games...")
    games = fetch_todays_games()
    for g in games:
        print(f"  {g.get('away_team', '?')} @ {g.get('home_team', '?')}: {g.get('spread', 'N/A')}")
