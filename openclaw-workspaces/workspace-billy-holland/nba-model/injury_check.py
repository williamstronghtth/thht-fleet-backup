#!/usr/bin/env python3
"""
NBA Star Player Injury Checker
Flags key players OUT/Questionable before game time
"""

import requests
import re
import json
import os
from datetime import datetime

DATA_DIR = os.path.dirname(os.path.abspath(__file__)) + "/data"

# Star players to track (move lines significantly)
STAR_PLAYERS = {
    'ATL': ['Trae Young', 'Jalen Johnson'],
    'BOS': ['Jayson Tatum', 'Jaylen Brown', 'Derrick White'],
    'BKN': ['Cam Thomas', 'Nic Claxton'],
    'CHA': ['LaMelo Ball', 'Brandon Miller'],
    'CHI': ['Zach LaVine', 'Coby White', 'Nikola Vucevic'],
    'CLE': ['Donovan Mitchell', 'Darius Garland', 'Evan Mobley', 'James Harden'],
    'DAL': ['Luka Doncic', 'Kyrie Irving'],
    'DEN': ['Nikola Jokic', 'Jamal Murray', 'Aaron Gordon', 'Michael Porter Jr.'],
    'DET': ['Cade Cunningham', 'Jaden Ivey', 'Jalen Duren'],
    'GSW': ['Stephen Curry', 'Draymond Green', 'Kristaps Porzingis'],
    'HOU': ['Jalen Green', 'Alperen Sengun', 'Jabari Smith Jr.'],
    'IND': ['Tyrese Haliburton', 'Pascal Siakam', 'Myles Turner'],
    'LAC': ['Kawhi Leonard', 'James Harden', 'Norman Powell'],
    'LAL': ['LeBron James', 'Anthony Davis', 'Luka Doncic'],
    'MEM': ['Ja Morant', 'Desmond Bane', 'Jaren Jackson Jr.'],
    'MIA': ['Jimmy Butler', 'Bam Adebayo', 'Tyler Herro'],
    'MIL': ['Giannis Antetokounmpo', 'Damian Lillard', 'Khris Middleton'],
    'MIN': ['Anthony Edwards', 'Rudy Gobert', 'Julius Randle'],
    'NOP': ['Zion Williamson', 'Brandon Ingram', 'CJ McCollum', 'Dejounte Murray'],
    'NYK': ['Jalen Brunson', 'Karl-Anthony Towns', 'Mikal Bridges', 'OG Anunoby'],
    'OKC': ['Shai Gilgeous-Alexander', 'Chet Holmgren', 'Jalen Williams'],
    'ORL': ['Paolo Banchero', 'Franz Wagner'],
    'PHI': ['Joel Embiid', 'Tyrese Maxey', 'Paul George'],
    'PHX': ['Kevin Durant', 'Devin Booker', 'Bradley Beal'],
    'POR': ['Anfernee Simons', 'Scoot Henderson', 'Deandre Ayton'],
    'SAC': ['De\'Aaron Fox', 'Domantas Sabonis', 'Keegan Murray'],
    'SAS': ['Victor Wembanyama', 'Devin Vassell'],
    'TOR': ['Scottie Barnes', 'RJ Barrett', 'Immanuel Quickley'],
    'UTA': ['Lauri Markkanen', 'Collin Sexton', 'Jordan Clarkson'],
    'WAS': ['Jordan Poole', 'Kyle Kuzma'],
    # ESPN alternate abbreviations
    'NY': ['Jalen Brunson', 'Karl-Anthony Towns', 'Mikal Bridges', 'OG Anunoby'],
    'NO': ['Zion Williamson', 'Brandon Ingram', 'CJ McCollum', 'Dejounte Murray'],
    'GS': ['Stephen Curry', 'Draymond Green'],
    'SA': ['Victor Wembanyama', 'Devin Vassell'],
}


def fetch_injuries_html():
    """Fetch raw HTML from ESPN injuries page"""
    url = "https://www.espn.com/nba/injuries"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"Error fetching injuries: {e}")
        return ""


def parse_player_status(html, player_name):
    """
    Find a specific player in the HTML and extract their status
    Returns: {'status': 'Out/Questionable/etc', 'return_date': 'Feb 20', 'note': '...'} or None
    """
    # Find player in HTML
    idx = html.find(player_name)
    if idx < 0:
        return None
    
    # Get context around player (the table row)
    context = html[idx:idx+500]
    
    # Look for status span
    # Pattern: <span class="TextStatus TextStatus--red plain">Out</span>
    status_match = re.search(r'TextStatus[^>]*>(\w+(?:-\w+)?)</span>', context)
    status = status_match.group(1) if status_match else None
    
    # Look for return date
    # Pattern: <td class="col-date Table__TD">Feb 20</td>
    date_match = re.search(r'col-date[^>]*>([^<]+)</td>', context)
    return_date = date_match.group(1).strip() if date_match else None
    
    if status:
        return {
            'status': status,
            'return_date': return_date,
        }
    
    return None


def check_tonight_injuries(games):
    """
    Check star player injuries for tonight's games
    games: list of {'home': 'BOS', 'away': 'MIA'} dicts
    Returns formatted injury alerts
    """
    html = fetch_injuries_html()
    if not html:
        return "❌ Could not fetch injury data"
    
    alerts = []
    
    for game in games:
        home = game.get('home', '')
        away = game.get('away', '')
        game_alerts = []
        
        # Check both teams
        for team in [home, away]:
            stars = STAR_PLAYERS.get(team, [])
            for player in stars:
                info = parse_player_status(html, player)
                if info and info['status'] in ['Out', 'Doubtful', 'Questionable', 'Day-To-Day']:
                    severity = '🔴' if info['status'] == 'Out' else '🟡' if info['status'] in ['Doubtful', 'Questionable'] else '🟠'
                    game_alerts.append({
                        'player': player,
                        'team': team,
                        'status': info['status'],
                        'return': info.get('return_date', ''),
                        'severity': severity
                    })
        
        if game_alerts:
            alerts.append({
                'matchup': f"{away} @ {home}",
                'injuries': game_alerts
            })
    
    return alerts


def format_injury_alerts(alerts):
    """Format alerts for mobile display"""
    if not alerts:
        return "✅ No star injuries for tonight's games"
    
    lines = ["⚠️ **INJURY ALERTS**", ""]
    
    for game in alerts:
        lines.append(f"**{game['matchup']}**")
        for inj in game['injuries']:
            lines.append(f"{inj['severity']} {inj['player']}: {inj['status']}")
        lines.append("")
    
    return '\n'.join(lines)


def get_injury_impact_warning(alerts, pick_team):
    """
    Check if a pick is affected by injuries
    Returns warning string or None
    """
    for game in alerts:
        for inj in game.get('injuries', []):
            if inj['team'] == pick_team and inj['status'] == 'Out':
                return f"⚠️ {inj['player']} OUT"
    return None


if __name__ == "__main__":
    print("Checking injuries for tonight's games...\n")
    
    games = [
        {'home': 'DET', 'away': 'NY'},
        {'home': 'BOS', 'away': 'MIA'},
        {'home': 'MIL', 'away': 'IND'},
        {'home': 'MIN', 'away': 'NO'},
        {'home': 'POR', 'away': 'MEM'},
        {'home': 'SAC', 'away': 'LAC'},
    ]
    
    alerts = check_tonight_injuries(games)
    print(format_injury_alerts(alerts))
