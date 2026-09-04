#!/usr/bin/env python3
"""
NBA Player Impact Model
Quantify how much each player is worth in points to the spread

Based on:
- RPM (Real Plus-Minus)
- Minutes played
- Usage rate
- Team dependency
"""

import json
import os

DATA_DIR = os.path.dirname(os.path.abspath(__file__)) + "/data"

# Star player impact estimates (points added to spread when PLAYING)
# When OUT, subtract this from team's expected margin
# Based on RPM, usage, and observed line movements

PLAYER_IMPACT = {
    # Tier 1: MVP candidates (+6 to +8 pts)
    'Nikola Jokic': 8.0,
    'Shai Gilgeous-Alexander': 7.5,
    'Luka Doncic': 7.5,
    'Giannis Antetokounmpo': 7.0,
    'Joel Embiid': 7.0,
    'Jayson Tatum': 6.5,
    'Anthony Edwards': 6.0,
    
    # Tier 2: All-NBA level (+4 to +6 pts)
    'LeBron James': 5.5,
    'Stephen Curry': 5.5,
    'Kevin Durant': 5.5,
    'Damian Lillard': 5.0,
    'Donovan Mitchell': 5.0,
    'Ja Morant': 5.0,
    'Tyrese Haliburton': 5.0,
    'Anthony Davis': 5.0,
    'Jaylen Brown': 4.5,
    'Devin Booker': 4.5,
    'Karl-Anthony Towns': 4.5,
    'Trae Young': 4.5,
    'De\'Aaron Fox': 4.5,
    'Jalen Brunson': 4.5,
    'Cade Cunningham': 4.0,
    'LaMelo Ball': 4.0,
    'Paolo Banchero': 4.0,
    'Victor Wembanyama': 4.5,
    'Chet Holmgren': 4.0,
    
    # Tier 3: All-Star level (+2.5 to +4 pts)
    'Bam Adebayo': 3.5,
    'Pascal Siakam': 3.5,
    'Domantas Sabonis': 3.5,
    'Julius Randle': 3.5,
    'Zion Williamson': 4.0,
    'Brandon Ingram': 3.5,
    'Dejounte Murray': 3.0,
    'CJ McCollum': 2.5,
    'Tyler Herro': 3.0,
    'Desmond Bane': 3.0,
    'Jaren Jackson Jr.': 3.5,
    'Myles Turner': 2.5,
    'Rudy Gobert': 3.0,
    'Mikal Bridges': 2.5,
    'OG Anunoby': 2.5,
    'Khris Middleton': 3.0,
    'Kristaps Porzingis': 3.5,
    'James Harden': 4.0,
    'Paul George': 3.5,
    'Kawhi Leonard': 5.0,
    'Jimmy Butler': 4.5,
    'Kyrie Irving': 4.5,
    
    # Tier 4: Quality starters (+1.5 to +2.5 pts)
    'Jaden Ivey': 2.0,
    'Jalen Duren': 1.5,
    'Alperen Sengun': 2.5,
    'Anfernee Simons': 2.5,
    'Franz Wagner': 3.0,
    'Scottie Barnes': 3.0,
    'Herb Jones': 1.5,
    'Derrick White': 2.0,
    'Brook Lopez': 2.0,
    'Jalen Williams': 3.0,
}

def get_player_impact(player_name):
    """Get point impact for a player. Returns 0 if unknown."""
    # Try exact match
    if player_name in PLAYER_IMPACT:
        return PLAYER_IMPACT[player_name]
    
    # Try partial match
    for name, impact in PLAYER_IMPACT.items():
        if player_name.lower() in name.lower() or name.lower() in player_name.lower():
            return impact
    
    return 0.0

def calculate_injury_adjustment(team_abbrev, injured_players):
    """
    Calculate total point adjustment for a team's injuries
    
    injured_players: list of player names who are OUT
    Returns: negative number (points to subtract from team's margin)
    """
    total_impact = 0.0
    details = []
    
    for player in injured_players:
        impact = get_player_impact(player)
        if impact > 0:
            total_impact += impact
            details.append({'player': player, 'impact': impact})
    
    return {
        'team': team_abbrev,
        'total_adjustment': -total_impact,  # Negative because player is OUT
        'players': details
    }

def compare_injury_impact(home_injuries, away_injuries):
    """
    Compare injury impact between two teams
    Returns net adjustment to spread (positive = helps home team)
    """
    home_adj = sum(get_player_impact(p) for p in home_injuries)
    away_adj = sum(get_player_impact(p) for p in away_injuries)
    
    # If away team has more injuries, home team benefits (positive adjustment)
    net = away_adj - home_adj
    
    return {
        'home_injuries_impact': -home_adj,
        'away_injuries_impact': -away_adj,
        'net_spread_adjustment': net,
        'interpretation': f"Adjust spread {net:+.1f} pts toward home team" if net != 0 else "No adjustment"
    }


def analyze_last_night():
    """Analyze last night's injury impacts vs results"""
    games = [
        {
            'game': 'MEM @ POR',
            'injuries': {'MEM': ['Ja Morant'], 'POR': []},
            'line': 9.0,  # MEM +9
            'result': -20,  # MEM lost by 20
        },
        {
            'game': 'NY @ DET', 
            'injuries': {'NY': ['Karl-Anthony Towns'], 'DET': []},
            'line': 4.0,  # NY +4
            'result': -38,  # NY lost by 38
        },
        {
            'game': 'NO @ MIN',
            'injuries': {'NO': ['Dejounte Murray'], 'MIN': []},
            'line': 8.5,  # NO +8.5
            'result': 4,  # NO won by 4
        },
    ]
    
    print("INJURY IMPACT ANALYSIS - Last Night")
    print("="*50)
    
    for game in games:
        home = game['game'].split(' @ ')[1]
        away = game['game'].split(' @ ')[0]
        
        away_impact = sum(get_player_impact(p) for p in game['injuries'].get(away, []))
        home_impact = sum(get_player_impact(p) for p in game['injuries'].get(home, []))
        
        # Adjusted line (if we had accounted for injuries)
        injury_adj = home_impact - away_impact  # Positive = away team hurt more
        adjusted_line = game['line'] + injury_adj
        
        covered = game['result'] > -game['line']
        would_cover_adjusted = game['result'] > -adjusted_line
        
        print(f"\n{game['game']}")
        print(f"  Injuries: {game['injuries']}")
        print(f"  Impact: Away -{away_impact:.1f} pts, Home -{home_impact:.1f} pts")
        print(f"  Original line: {away} +{game['line']}")
        print(f"  Adjusted line: {away} +{adjusted_line:.1f}")
        print(f"  Result: {away} {game['result']:+d}")
        print(f"  Original: {'✅ COVER' if covered else '❌ NO COVER'}")
        print(f"  Adjusted: {'✅ COVER' if would_cover_adjusted else '❌ NO COVER'}")


if __name__ == "__main__":
    analyze_last_night()
