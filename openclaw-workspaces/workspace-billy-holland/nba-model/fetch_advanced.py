#!/usr/bin/env python3
"""
Advanced NBA Data Fetcher
Pulls from NBAStuffer, ESPN injuries, and other sources
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import re
import os
from datetime import datetime

DATA_DIR = os.path.dirname(os.path.abspath(__file__)) + "/data"


def fetch_nbastuffer_stats():
    """
    Fetch team stats from NBAStuffer including:
    - oEFF, dEFF (efficiency)
    - Pace
    - SoS (strength of schedule)
    - Last 5 games performance
    """
    url = "https://www.nbastuffer.com/2025-2026-nba-team-stats/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Find all tables
        tables = soup.find_all('table')
        
        all_data = {}
        
        for table in tables:
            try:
                df = pd.read_html(str(table))[0]
                
                # Try to identify table type by columns
                cols_lower = [str(c).lower() for c in df.columns]
                cols_str = ' '.join(cols_lower)
                
                if 'team' in cols_str and 'oeff' in cols_str:
                    # Main season stats table
                    if 'season' not in all_data:
                        all_data['season'] = df
                        print(f"Found season stats: {len(df)} teams")
                        
            except Exception as e:
                continue
        
        if 'season' in all_data:
            all_data['season'].to_csv(f"{DATA_DIR}/nbastuffer_season.csv", index=False)
            
        return all_data
        
    except Exception as e:
        print(f"Error fetching NBAStuffer: {e}")
        return None


def fetch_espn_injuries():
    """
    Fetch current NBA injuries from ESPN
    Returns dict of team -> list of injured players with status
    """
    url = "https://www.espn.com/nba/injuries"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        injuries = {}
        
        # Find all tables with class containing 'Table'
        tables = soup.find_all('table')
        
        # Also try to find team sections by looking for team name patterns
        # ESPN uses divs with team names followed by injury tables
        team_sections = soup.find_all('div', class_=re.compile(r'(ResponsiveTable|Table__Title)'))
        
        # Parse each table, looking for preceding team name
        current_team = None
        
        # Look for team names in specific spans/divs
        for element in soup.find_all(['span', 'div', 'h2', 'h3']):
            text = element.get_text(strip=True)
            # Check if this looks like a team name
            if any(team in text for team in [
                'Hawks', 'Celtics', 'Nets', 'Hornets', 'Bulls', 'Cavaliers',
                'Mavericks', 'Nuggets', 'Pistons', 'Warriors', 'Rockets', 'Pacers',
                'Clippers', 'Lakers', 'Grizzlies', 'Heat', 'Bucks', 'Timberwolves',
                'Pelicans', 'Knicks', 'Thunder', 'Magic', '76ers', 'Suns',
                'Trail Blazers', 'Kings', 'Spurs', 'Raptors', 'Jazz', 'Wizards'
            ]):
                current_team = text
                if current_team not in injuries:
                    injuries[current_team] = []
        
        # Now parse tables for player data
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 3:
                    # Try to extract player name from first cell
                    first_cell = cells[0]
                    player_link = first_cell.find('a')
                    player_name = player_link.get_text(strip=True) if player_link else first_cell.get_text(strip=True)
                    
                    # Skip header rows
                    if player_name.upper() in ['NAME', 'PLAYER', '']:
                        continue
                    
                    # Try to find the team this player belongs to
                    # Look at parent elements for team info
                    parent = row.find_parent('div')
                    team_found = None
                    while parent and not team_found:
                        prev = parent.find_previous(['span', 'div', 'h2'])
                        if prev:
                            prev_text = prev.get_text(strip=True)
                            for team_key in injuries.keys():
                                if team_key in prev_text or prev_text in team_key:
                                    team_found = team_key
                                    break
                        parent = parent.find_parent('div')
                    
                    if team_found and player_name:
                        injury_info = {
                            'player': player_name,
                            'position': cells[1].get_text(strip=True) if len(cells) > 1 else '',
                            'status': cells[3].get_text(strip=True) if len(cells) > 3 else 'Out',
                        }
                        injuries[team_found].append(injury_info)
        
        # If we didn't get good data, try a simpler approach - just parse all text
        if sum(len(v) for v in injuries.values()) < 10:
            # Fallback: use the raw text we fetched earlier from ESPN
            injuries = parse_injuries_from_text(resp.text)
        
        # Save to file
        with open(f"{DATA_DIR}/injuries.json", 'w') as f:
            json.dump(injuries, f, indent=2)
            
        return injuries
        
    except Exception as e:
        print(f"Error fetching injuries: {e}")
        return {}


def parse_injuries_from_text(html_text):
    """
    Fallback parser that looks for team names and player patterns in raw HTML
    """
    injuries = {}
    
    # Team name patterns
    teams = [
        'Atlanta Hawks', 'Boston Celtics', 'Brooklyn Nets', 'Charlotte Hornets',
        'Chicago Bulls', 'Cleveland Cavaliers', 'Dallas Mavericks', 'Denver Nuggets',
        'Detroit Pistons', 'Golden State Warriors', 'Houston Rockets', 'Indiana Pacers',
        'LA Clippers', 'Los Angeles Lakers', 'Memphis Grizzlies', 'Miami Heat',
        'Milwaukee Bucks', 'Minnesota Timberwolves', 'New Orleans Pelicans',
        'New York Knicks', 'Oklahoma City Thunder', 'Orlando Magic',
        'Philadelphia 76ers', 'Phoenix Suns', 'Portland Trail Blazers',
        'Sacramento Kings', 'San Antonio Spurs', 'Toronto Raptors',
        'Utah Jazz', 'Washington Wizards'
    ]
    
    # Initialize all teams
    for team in teams:
        injuries[team] = []
    
    # Split by team names and parse
    for i, team in enumerate(teams):
        # Find section for this team
        team_idx = html_text.find(team)
        if team_idx == -1:
            continue
            
        # Find next team or end
        next_team_idx = len(html_text)
        for other_team in teams:
            if other_team != team:
                idx = html_text.find(other_team, team_idx + len(team))
                if idx != -1 and idx < next_team_idx:
                    next_team_idx = idx
        
        section = html_text[team_idx:next_team_idx]
        
        # Look for player links and status
        soup = BeautifulSoup(section, 'html.parser')
        for link in soup.find_all('a'):
            href = link.get('href', '')
            if '/nba/player/' in href:
                player_name = link.get_text(strip=True)
                if player_name:
                    # Find status in nearby text
                    parent = link.find_parent('tr') or link.find_parent('div')
                    if parent:
                        text = parent.get_text()
                        status = 'Out' if 'Out' in text else 'Day-To-Day' if 'Day-To-Day' in text else 'Unknown'
                        injuries[team].append({'player': player_name, 'status': status})
    
    return injuries


def get_key_injuries_tonight(games, injuries):
    """
    Given tonight's games, return key injury impacts
    """
    key_injuries = {}
    
    for game in games:
        home = game.get('home_team', game.get('home_name', ''))
        away = game.get('away_team', game.get('away_name', ''))
        
        home_impact = calculate_injury_impact(home, injuries)
        away_impact = calculate_injury_impact(away, injuries)
        
        key_injuries[f"{away} @ {home}"] = {
            'home_impact': home_impact,
            'away_impact': away_impact,
            'net_impact': away_impact - home_impact  # Positive = favors home
        }
    
    return key_injuries


def calculate_injury_impact(team_name, injuries_data):
    """
    Calculate point impact of injuries for a team
    
    Rough impact estimates:
    - Star player (All-Star level): 3-5 points
    - Starter: 1-2 points
    - Rotation player: 0.5-1 point
    - End of bench: 0-0.5 points
    
    Status multipliers:
    - Out: 1.0
    - Doubtful: 0.8
    - Questionable: 0.4
    - Probable/GTD: 0.2
    """
    
    # Map common team name variations
    team_variations = {
        'Boston Celtics': ['BOS', 'Boston'],
        'Los Angeles Lakers': ['LAL', 'LA Lakers', 'Lakers'],
        'Golden State Warriors': ['GSW', 'GS', 'Warriors'],
        'Miami Heat': ['MIA', 'Miami'],
        'Milwaukee Bucks': ['MIL', 'Milwaukee'],
        'Phoenix Suns': ['PHX', 'PHO', 'Phoenix'],
        'Minnesota Timberwolves': ['MIN', 'Minnesota'],
        'Denver Nuggets': ['DEN', 'Denver'],
        'Cleveland Cavaliers': ['CLE', 'Cleveland'],
        'New York Knicks': ['NYK', 'NY', 'Knicks'],
        'Philadelphia 76ers': ['PHI', 'Philadelphia', 'Sixers'],
        'Dallas Mavericks': ['DAL', 'Dallas'],
        'Memphis Grizzlies': ['MEM', 'Memphis'],
        'Sacramento Kings': ['SAC', 'Sacramento'],
        'Indiana Pacers': ['IND', 'Indiana'],
        'New Orleans Pelicans': ['NOP', 'NO', 'Pelicans'],
        'Oklahoma City Thunder': ['OKC', 'Thunder'],
        'Detroit Pistons': ['DET', 'Detroit'],
        'Chicago Bulls': ['CHI', 'Chicago'],
        'Atlanta Hawks': ['ATL', 'Atlanta'],
        'Orlando Magic': ['ORL', 'Orlando'],
        'Toronto Raptors': ['TOR', 'Toronto'],
        'Brooklyn Nets': ['BKN', 'Brooklyn'],
        'Charlotte Hornets': ['CHA', 'Charlotte'],
        'Houston Rockets': ['HOU', 'Houston'],
        'Portland Trail Blazers': ['POR', 'Portland'],
        'San Antonio Spurs': ['SAS', 'SA', 'Spurs'],
        'Utah Jazz': ['UTA', 'UTAH', 'Utah'],
        'LA Clippers': ['LAC', 'LA', 'Clippers'],
        'Washington Wizards': ['WAS', 'WSH', 'Washington'],
    }
    
    # Find matching team in injuries data
    matched_team = None
    for full_name, variations in team_variations.items():
        if team_name in variations or team_name == full_name:
            if full_name in injuries_data:
                matched_team = full_name
                break
            # Also check if any variation matches a key
            for var in variations:
                for key in injuries_data.keys():
                    if var.lower() in key.lower():
                        matched_team = key
                        break
    
    if not matched_team or matched_team not in injuries_data:
        return 0.0
    
    team_injuries = injuries_data[matched_team]
    
    # Star players (rough list - should be updated)
    star_players = [
        'LeBron James', 'Stephen Curry', 'Kevin Durant', 'Giannis Antetokounmpo',
        'Luka Doncic', 'Nikola Jokic', 'Joel Embiid', 'Jayson Tatum',
        'Ja Morant', 'Trae Young', 'Donovan Mitchell', 'Devin Booker',
        'Anthony Edwards', 'Shai Gilgeous-Alexander', 'Tyrese Haliburton',
        'Paolo Banchero', 'Zion Williamson', 'Cade Cunningham',
        'James Harden', 'Kyrie Irving', 'Anthony Davis', 'Kawhi Leonard',
        'Paul George', 'Jimmy Butler', 'Damian Lillard', 'Bam Adebayo',
        'Domantas Sabonis', 'De\'Aaron Fox', 'LaMelo Ball', 'Jalen Brunson',
        'Victor Wembanyama', 'Evan Mobley', 'Scottie Barnes', 'Franz Wagner'
    ]
    
    status_multipliers = {
        'out': 1.0,
        'doubtful': 0.8,
        'questionable': 0.4,
        'day-to-day': 0.3,
        'probable': 0.1,
    }
    
    total_impact = 0.0
    
    for injury in team_injuries:
        player = injury.get('player', '')
        status = injury.get('status', '').lower()
        
        # Determine base impact
        if any(star.lower() in player.lower() for star in star_players):
            base_impact = 4.0  # Star player
        elif injury.get('position', '') in ['G', 'F', 'C']:
            base_impact = 1.5  # Likely starter
        else:
            base_impact = 0.5  # Rotation/bench
        
        # Apply status multiplier
        multiplier = 0.5  # Default
        for status_key, mult in status_multipliers.items():
            if status_key in status:
                multiplier = mult
                break
        
        total_impact += base_impact * multiplier
    
    return round(total_impact, 1)


def get_team_last5_form(team_abbrev, nbastuffer_data):
    """
    Extract last 5 games performance for momentum calculation
    Returns dict with L5 stats if available
    """
    # This would parse the L5 section from NBAStuffer
    # For now return None - would need to implement
    return None


if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    
    print("Fetching NBAStuffer stats...")
    stuffer = fetch_nbastuffer_stats()
    
    print("\nFetching ESPN injuries...")
    injuries = fetch_espn_injuries()
    
    if injuries:
        print(f"\nInjuries by team:")
        for team, players in injuries.items():
            if players:
                impact = calculate_injury_impact(team, injuries)
                print(f"  {team}: {len(players)} players, ~{impact} pts impact")
