#!/usr/bin/env python3
"""
NBA Coach Tendencies Tracker
"Predict what teams WILL do, not what they SHOULD do" - Voulgaris

Track coach patterns in:
- Pace adjustments
- Late-game management
- Rotation patterns
- Play style vs specific opponents
"""

import json
import os
from datetime import datetime

DATA_DIR = os.path.dirname(os.path.abspath(__file__)) + "/data"
COACH_FILE = f"{DATA_DIR}/coach_tendencies.json"

# 2025-26 NBA Head Coaches
COACHES = {
    'ATL': {'name': 'Quin Snyder', 'style': 'defensive', 'pace': 'slow'},
    'BOS': {'name': 'Joe Mazzulla', 'style': 'offensive', 'pace': 'fast'},
    'BKN': {'name': 'Jordi Fernandez', 'style': 'developmental', 'pace': 'medium'},
    'CHA': {'name': 'Charles Lee', 'style': 'unknown', 'pace': 'medium'},
    'CHI': {'name': 'Billy Donovan', 'style': 'balanced', 'pace': 'medium'},
    'CLE': {'name': 'Kenny Atkinson', 'style': 'offensive', 'pace': 'fast'},
    'DAL': {'name': 'Jason Kidd', 'style': 'defensive', 'pace': 'slow'},
    'DEN': {'name': 'Michael Malone', 'style': 'balanced', 'pace': 'medium'},
    'DET': {'name': 'J.B. Bickerstaff', 'style': 'defensive', 'pace': 'slow'},
    'GSW': {'name': 'Steve Kerr', 'style': 'motion', 'pace': 'fast'},
    'HOU': {'name': 'Ime Udoka', 'style': 'defensive', 'pace': 'slow'},
    'IND': {'name': 'Rick Carlisle', 'style': 'offensive', 'pace': 'fast'},
    'LAC': {'name': 'Tyronn Lue', 'style': 'balanced', 'pace': 'medium'},
    'LAL': {'name': 'JJ Redick', 'style': 'offensive', 'pace': 'fast'},
    'MEM': {'name': 'Taylor Jenkins', 'style': 'balanced', 'pace': 'fast'},
    'MIA': {'name': 'Erik Spoelstra', 'style': 'defensive', 'pace': 'slow'},
    'MIL': {'name': 'Doc Rivers', 'style': 'balanced', 'pace': 'medium'},
    'MIN': {'name': 'Chris Finch', 'style': 'defensive', 'pace': 'medium'},
    'NOP': {'name': 'Willie Green', 'style': 'balanced', 'pace': 'medium'},
    'NYK': {'name': 'Tom Thibodeau', 'style': 'defensive', 'pace': 'slow'},
    'OKC': {'name': 'Mark Daigneault', 'style': 'balanced', 'pace': 'fast'},
    'ORL': {'name': 'Jamahl Mosley', 'style': 'defensive', 'pace': 'slow'},
    'PHI': {'name': 'Nick Nurse', 'style': 'defensive', 'pace': 'medium'},
    'PHX': {'name': 'Mike Budenholzer', 'style': 'offensive', 'pace': 'slow'},
    'POR': {'name': 'Chauncey Billups', 'style': 'developmental', 'pace': 'fast'},
    'SAC': {'name': 'Mike Brown', 'style': 'balanced', 'pace': 'fast'},
    'SAS': {'name': 'Gregg Popovich', 'style': 'balanced', 'pace': 'slow'},
    'TOR': {'name': 'Darko Rajakovic', 'style': 'offensive', 'pace': 'fast'},
    'UTA': {'name': 'Will Hardy', 'style': 'developmental', 'pace': 'medium'},
    'WAS': {'name': 'Brian Keefe', 'style': 'developmental', 'pace': 'fast'},
}

# Tendencies to track
TENDENCY_TYPES = [
    'late_game_pace',      # Does coach speed up or slow down late?
    'garbage_time',        # When does coach pull starters?
    'back_to_back',        # Rest patterns on B2Bs
    'timeout_usage',       # Strategic timeout patterns
    'challenge_usage',     # When do they challenge?
    'foul_game_start',     # When trailing, when start fouling?
    'blowout_behavior',    # Behavior when up/down big
]

def load_tendencies():
    """Load coach tendencies data"""
    try:
        with open(COACH_FILE, 'r') as f:
            return json.load(f)
    except:
        # Initialize with base data
        return {'coaches': COACHES, 'observations': []}

def save_tendencies(data):
    """Save tendencies"""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(COACH_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def add_observation(team, tendency_type, observation, game_date=None):
    """
    Add a coach tendency observation
    
    Example:
    add_observation('MIA', 'late_game_pace', 'Slows pace significantly in 4th when leading')
    """
    data = load_tendencies()
    
    obs = {
        'team': team,
        'coach': COACHES.get(team, {}).get('name', 'Unknown'),
        'type': tendency_type,
        'observation': observation,
        'date': game_date or datetime.now().strftime('%Y-%m-%d'),
        'timestamp': datetime.now().isoformat()
    }
    
    data['observations'].append(obs)
    save_tendencies(data)
    print(f"✓ Observation added for {team}")

def get_coach_profile(team):
    """Get full coach profile with observations"""
    data = load_tendencies()
    
    coach = data['coaches'].get(team, {})
    obs = [o for o in data['observations'] if o['team'] == team]
    
    return {
        'team': team,
        'coach': coach,
        'observations': obs
    }

def matchup_notes(home_team, away_team):
    """Get relevant coach notes for a matchup"""
    home = get_coach_profile(home_team)
    away = get_coach_profile(away_team)
    
    notes = []
    
    # Pace matchup
    home_pace = home['coach'].get('pace', 'medium')
    away_pace = away['coach'].get('pace', 'medium')
    
    if home_pace == 'fast' and away_pace == 'slow':
        notes.append(f"Pace mismatch: {home_team} wants to run, {away_team} wants to grind")
    elif home_pace == 'slow' and away_pace == 'fast':
        notes.append(f"Pace mismatch: {away_team} wants to run, {home_team} wants to grind")
    
    # Style matchup
    home_style = home['coach'].get('style', 'balanced')
    away_style = away['coach'].get('style', 'balanced')
    
    if home_style == 'defensive' and away_style == 'defensive':
        notes.append("Both teams defensive-minded → lean UNDER")
    elif home_style == 'offensive' and away_style == 'offensive':
        notes.append("Both teams offensive-minded → lean OVER")
    
    return {
        'home': home,
        'away': away,
        'notes': notes
    }


if __name__ == "__main__":
    # Initialize the file
    data = load_tendencies()
    save_tendencies(data)
    print(f"Coach database initialized with {len(COACHES)} coaches")
    
    # Example matchup
    print("\nExample matchup: MEM @ POR")
    notes = matchup_notes('POR', 'MEM')
    print(f"Home coach: {notes['home']['coach']}")
    print(f"Away coach: {notes['away']['coach']}")
    for note in notes['notes']:
        print(f"  • {note}")
