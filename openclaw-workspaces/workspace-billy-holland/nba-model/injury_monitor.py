#!/usr/bin/env python3
"""
NBA Injury Monitor v1.0
Scrapes ESPN and other free sources for injury updates
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os

DATA_DIR = os.path.dirname(os.path.abspath(__file__)) + "/data"

# Key players to always track (stars that move lines)
STAR_PLAYERS = [
    "Giannis Antetokounmpo", "Luka Doncic", "Nikola Jokic", "Joel Embiid",
    "Stephen Curry", "LeBron James", "Kevin Durant", "Jayson Tatum",
    "Shai Gilgeous-Alexander", "Anthony Edwards", "Ja Morant", "Donovan Mitchell",
    "Damian Lillard", "Trae Young", "Tyrese Haliburton", "De'Aaron Fox",
    "Devin Booker", "Kyrie Irving", "Anthony Davis", "Kawhi Leonard",
    "Paul George", "Jimmy Butler", "Bam Adebayo", "Paolo Banchero",
    "Zion Williamson", "Chet Holmgren", "Victor Wembanyama", "Scottie Barnes",
    "Jalen Brunson", "Karl-Anthony Towns", "Domantas Sabonis", "Jaylen Brown"
]

def fetch_espn_injuries():
    """Scrape ESPN injury report"""
    url = "https://www.espn.com/nba/injuries"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        injuries = []
        
        # Find all team sections
        tables = soup.find_all('table', class_='Table')
        team_headers = soup.find_all('div', class_='Table__Title')
        
        current_team = "Unknown"
        
        for i, table in enumerate(tables):
            # Try to get team name
            if i < len(team_headers):
                current_team = team_headers[i].get_text(strip=True)
            
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 4:
                    name = cells[0].get_text(strip=True)
                    status = cells[2].get_text(strip=True) if len(cells) > 2 else ""
                    comment = cells[3].get_text(strip=True) if len(cells) > 3 else ""
                    
                    if name and status:
                        injuries.append({
                            'team': current_team,
                            'player': name,
                            'status': status,
                            'comment': comment[:200],  # Truncate long comments
                            'is_star': name in STAR_PLAYERS,
                            'source': 'ESPN',
                            'fetched_at': datetime.now().isoformat()
                        })
        
        return injuries
    except Exception as e:
        print(f"Error fetching ESPN: {e}")
        return []

def fetch_cbssports_injuries():
    """Scrape CBS Sports injury report as backup"""
    url = "https://www.cbssports.com/nba/injuries/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        injuries = []
        
        # CBS has a different structure - adapt as needed
        rows = soup.find_all('tr', class_='TableBase-bodyTr')
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 3:
                name_elem = cells[0].find('a')
                name = name_elem.get_text(strip=True) if name_elem else cells[0].get_text(strip=True)
                status = cells[2].get_text(strip=True) if len(cells) > 2 else ""
                
                if name and status:
                    injuries.append({
                        'player': name,
                        'status': status,
                        'is_star': name in STAR_PLAYERS,
                        'source': 'CBS',
                        'fetched_at': datetime.now().isoformat()
                    })
        
        return injuries
    except Exception as e:
        print(f"Error fetching CBS: {e}")
        return []

def get_all_injuries():
    """Get injuries from all sources"""
    espn = fetch_espn_injuries()
    
    # Combine and dedupe
    all_injuries = espn
    
    # Filter to stars and recent updates
    star_injuries = [i for i in all_injuries if i.get('is_star')]
    other_injuries = [i for i in all_injuries if not i.get('is_star')]
    
    return {
        'star_injuries': star_injuries,
        'all_injuries': all_injuries,
        'star_count': len(star_injuries),
        'total_count': len(all_injuries),
        'fetched_at': datetime.now().isoformat()
    }

def get_injuries_for_teams(teams):
    """Get injuries for specific teams"""
    all_data = get_all_injuries()
    
    team_injuries = []
    for injury in all_data['all_injuries']:
        team = injury.get('team', '').lower()
        for t in teams:
            if t.lower() in team or team in t.lower():
                team_injuries.append(injury)
                break
    
    return team_injuries

def format_injury_alert(injuries):
    """Format injuries as alert message"""
    if not injuries:
        return "✅ No significant injuries found"
    
    lines = ["⚠️ **INJURY ALERTS**\n"]
    
    # Group by team
    by_team = {}
    for inj in injuries:
        team = inj.get('team', 'Unknown')
        if team not in by_team:
            by_team[team] = []
        by_team[team].append(inj)
    
    for team, team_injuries in by_team.items():
        lines.append(f"**{team}**")
        for inj in team_injuries:
            status = inj['status']
            star = "🔴" if inj.get('is_star') else "🟡"
            lines.append(f"{star} {inj['player']}: {status}")
        lines.append("")
    
    return '\n'.join(lines)

def save_injuries(injuries):
    """Save injuries to file for tracking"""
    filepath = f"{DATA_DIR}/injuries_{datetime.now().strftime('%Y%m%d')}.json"
    with open(filepath, 'w') as f:
        json.dump(injuries, f, indent=2)
    return filepath

if __name__ == "__main__":
    print("Fetching NBA injury updates...\n")
    
    data = get_all_injuries()
    
    print(f"Found {data['total_count']} total injuries")
    print(f"Star players out: {data['star_count']}\n")
    
    # Show star injuries
    if data['star_injuries']:
        print("⭐ STAR PLAYER INJURIES:")
        print("-" * 40)
        for inj in data['star_injuries']:
            print(f"🔴 {inj['player']} ({inj.get('team', 'Unknown')})")
            print(f"   Status: {inj['status']}")
            if inj.get('comment'):
                print(f"   Note: {inj['comment'][:100]}...")
            print()
    
    # Save to file
    filepath = save_injuries(data)
    print(f"\nSaved to: {filepath}")
