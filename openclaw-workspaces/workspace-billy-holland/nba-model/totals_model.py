#!/usr/bin/env python3
"""
NBA Totals (Over/Under) Model v1.0

Key insight: Totals = f(pace, efficiency)
Most bettors focus on spreads. Totals often have softer lines.

Formula:
  Expected Total = (Combined ORtg) * (Expected Possessions) / 100
  
Where:
  Combined ORtg = weighted average of both teams' offensive output vs opponent defense
  Expected Possessions = f(pace_home, pace_away, rest, tempo matchup)
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime

DATA_DIR = os.path.dirname(os.path.abspath(__file__)) + "/data"

# League average pace (possessions per 48 min, 2024-25 season)
LEAGUE_AVG_PACE = 99.0

# Pace adjustment for rest (fewer possessions when tired)
REST_PACE_ADJ = {
    0: -2.0,   # B2B: slower pace
    1: 0.0,    # Normal rest
    2: 0.5,    # Extra rest: slightly faster
    3: 1.0,    # Extended rest: faster
}

# Home court total adjustment (slight bump - more energy)
HOME_TOTAL_ADJ = 1.5

# Max edge we trust (beyond this, line is probably right)
MAX_TOTAL_EDGE = 8.0


class TotalsModel:
    """
    Predict game totals using pace and efficiency
    """
    
    def __init__(self):
        self.pace_data = None
        
    def load_data(self, season="2026"):
        """Load team pace and efficiency data"""
        try:
            pace_file = f"{DATA_DIR}/team_pace_{season}.csv"
            if os.path.exists(pace_file):
                self.pace_data = pd.read_csv(pace_file)
                # Clean team names
                self.pace_data['Team'] = self.pace_data['Team'].str.replace('*', '', regex=False)
                print(f"Loaded pace data for {len(self.pace_data)} teams")
                return True
            else:
                print(f"No pace file: {pace_file}")
                return False
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def get_team_stats(self, team_name):
        """Get ORtg, DRtg, Pace for a team"""
        if self.pace_data is None:
            return {'ORtg': 115.0, 'DRtg': 115.0, 'Pace': LEAGUE_AVG_PACE}
        
        # Fuzzy match team name
        for _, row in self.pace_data.iterrows():
            if team_name.lower() in row['Team'].lower() or row['Team'].lower() in team_name.lower():
                return {
                    'ORtg': float(row['ORtg']),
                    'DRtg': float(row['DRtg']),
                    'Pace': float(row['Pace'])
                }
        
        # Map common abbreviations
        abbrev_map = {
            'BOS': 'Boston', 'LAL': 'Lakers', 'GSW': 'Golden State', 'GS': 'Golden State',
            'MIA': 'Miami', 'MIL': 'Milwaukee', 'PHI': 'Philadelphia', 'NYK': 'Knicks', 'NY': 'Knicks',
            'BKN': 'Brooklyn', 'TOR': 'Toronto', 'CHI': 'Chicago', 'CLE': 'Cleveland',
            'IND': 'Indiana', 'DET': 'Detroit', 'ATL': 'Atlanta', 'CHA': 'Charlotte',
            'ORL': 'Orlando', 'WAS': 'Washington', 'DEN': 'Denver', 'MIN': 'Minnesota',
            'OKC': 'Oklahoma', 'POR': 'Portland', 'UTA': 'Utah', 'PHX': 'Phoenix', 'PHO': 'Phoenix',
            'SAC': 'Sacramento', 'LAC': 'Clippers', 'DAL': 'Dallas', 'HOU': 'Houston',
            'SAS': 'San Antonio', 'SA': 'San Antonio', 'MEM': 'Memphis', 'NOP': 'Pelicans', 'NO': 'Pelicans'
        }
        
        if team_name.upper() in abbrev_map:
            search = abbrev_map[team_name.upper()]
            for _, row in self.pace_data.iterrows():
                if search.lower() in row['Team'].lower():
                    return {
                        'ORtg': float(row['ORtg']),
                        'DRtg': float(row['DRtg']),
                        'Pace': float(row['Pace'])
                    }
        
        print(f"Warning: Team '{team_name}' not found, using league avg")
        return {'ORtg': 115.0, 'DRtg': 115.0, 'Pace': LEAGUE_AVG_PACE}
    
    def predict_total(self, home_team, away_team, home_rest=1, away_rest=1):
        """
        Predict game total
        
        Returns: dict with predicted total and breakdown
        """
        home = self.get_team_stats(home_team)
        away = self.get_team_stats(away_team)
        
        # Expected pace for this game
        # Fast team pulls slow team up; slow team pulls fast team down
        # Weight toward faster team slightly (they control tempo more)
        base_pace = (home['Pace'] * 0.55 + away['Pace'] * 0.45)
        
        # Rest adjustments to pace
        home_rest_adj = REST_PACE_ADJ.get(min(home_rest, 3), 0)
        away_rest_adj = REST_PACE_ADJ.get(min(away_rest, 3), 0)
        pace_adj = (home_rest_adj + away_rest_adj) / 2
        
        expected_pace = base_pace + pace_adj
        
        # Expected points per possession for each team
        # Home team: their ORtg vs away DRtg (adjusted for matchup)
        home_ppp = (home['ORtg'] + (115 - away['DRtg'])) / 2 / 100  # Per possession
        away_ppp = (away['ORtg'] + (115 - home['DRtg'])) / 2 / 100
        
        # Simpler alternative: average of team's O and opponent's D
        home_pts_100 = (home['ORtg'] + away['DRtg']) / 2
        away_pts_100 = (away['ORtg'] + home['DRtg']) / 2
        
        # Total expected points
        possessions = expected_pace * 0.98  # Slight adjustment factor
        home_expected = home_pts_100 * possessions / 100
        away_expected = away_pts_100 * possessions / 100
        
        # Small home court bump
        home_expected += HOME_TOTAL_ADJ / 2
        away_expected += HOME_TOTAL_ADJ / 2
        
        predicted_total = home_expected + away_expected
        
        return {
            'home_team': home_team,
            'away_team': away_team,
            'predicted_total': round(predicted_total, 1),
            'home_expected': round(home_expected, 1),
            'away_expected': round(away_expected, 1),
            'expected_pace': round(expected_pace, 1),
            'components': {
                'home_ortg': home['ORtg'],
                'home_drtg': home['DRtg'],
                'away_ortg': away['ORtg'],
                'away_drtg': away['DRtg'],
                'home_pace': home['Pace'],
                'away_pace': away['Pace'],
                'rest_adj': round(pace_adj, 1)
            }
        }
    
    def find_value(self, prediction, market_total):
        """
        Compare model total to market O/U line
        
        Returns: dict with value assessment
        """
        model_total = prediction['predicted_total']
        edge = model_total - market_total
        
        # Threshold for value (need ~3 pts edge for totals)
        VALUE_THRESHOLD = 3.0
        
        if abs(edge) >= VALUE_THRESHOLD:
            if abs(edge) > MAX_TOTAL_EDGE:
                # Edge too big - probably missing something
                return {
                    'has_value': False,
                    'edge': round(edge, 1),
                    'warning': 'Edge too large - verify line/injuries'
                }
            
            side = 'OVER' if edge > 0 else 'UNDER'
            
            # Confidence based on edge size
            if abs(edge) >= 5.0:
                confidence = 'HIGH'
            elif abs(edge) >= 4.0:
                confidence = 'MEDIUM'
            else:
                confidence = 'LOW'
            
            return {
                'has_value': True,
                'edge': round(abs(edge), 1),
                'side': side,
                'line': market_total,
                'confidence': confidence,
                'model_total': model_total
            }
        
        return {
            'has_value': False,
            'edge': round(abs(edge), 1),
            'side': 'OVER' if edge > 0 else 'UNDER'
        }
    
    def explain_matchup(self, home_team, away_team):
        """Explain pace/style matchup for totals betting"""
        home = self.get_team_stats(home_team)
        away = self.get_team_stats(away_team)
        
        # Pace classification
        def classify_pace(pace):
            if pace >= 101: return 'FAST'
            elif pace >= 99: return 'AVERAGE'
            else: return 'SLOW'
        
        home_pace_class = classify_pace(home['Pace'])
        away_pace_class = classify_pace(away['Pace'])
        
        # Efficiency classification
        def classify_offense(ortg):
            if ortg >= 117: return 'ELITE'
            elif ortg >= 114: return 'GOOD'
            elif ortg >= 110: return 'AVERAGE'
            else: return 'POOR'
        
        def classify_defense(drtg):
            if drtg <= 110: return 'ELITE'
            elif drtg <= 113: return 'GOOD'
            elif drtg <= 116: return 'AVERAGE'
            else: return 'POOR'
        
        return {
            'home': {
                'pace': f"{home['Pace']} ({home_pace_class})",
                'offense': f"{home['ORtg']} ({classify_offense(home['ORtg'])})",
                'defense': f"{home['DRtg']} ({classify_defense(home['DRtg'])})"
            },
            'away': {
                'pace': f"{away['Pace']} ({away_pace_class})",
                'offense': f"{away['ORtg']} ({classify_offense(away['ORtg'])})",
                'defense': f"{away['DRtg']} ({classify_defense(away['DRtg'])})"
            },
            'matchup_notes': self._generate_notes(home, away, home_pace_class, away_pace_class)
        }
    
    def _generate_notes(self, home, away, home_pace, away_pace):
        """Generate betting notes for matchup"""
        notes = []
        
        # Pace mismatch
        if home_pace == 'FAST' and away_pace == 'SLOW':
            notes.append("Pace mismatch: Home wants to run, away wants to grind")
        elif home_pace == 'SLOW' and away_pace == 'FAST':
            notes.append("Pace mismatch: Away wants to run, home controls tempo at home")
        elif home_pace == 'FAST' and away_pace == 'FAST':
            notes.append("Both teams run - lean OVER")
        elif home_pace == 'SLOW' and away_pace == 'SLOW':
            notes.append("Both teams grind - lean UNDER")
        
        # Defensive matchup
        if home['DRtg'] <= 111 and away['DRtg'] <= 111:
            notes.append("Elite defenses on both sides - UNDER pressure")
        elif home['DRtg'] >= 117 and away['DRtg'] >= 117:
            notes.append("Poor defenses both sides - OVER pressure")
        
        # Offensive mismatch
        if abs(home['ORtg'] - away['ORtg']) >= 6:
            better = 'Home' if home['ORtg'] > away['ORtg'] else 'Away'
            notes.append(f"{better} significantly better offense")
        
        return notes if notes else ["No strong matchup indicators"]


def format_total_prediction(pred, market_total=None):
    """Format totals prediction for output"""
    lines = []
    lines.append(f"\n{'='*50}")
    lines.append(f"TOTALS: {pred['away_team']} @ {pred['home_team']}")
    lines.append(f"{'='*50}")
    lines.append(f"Model Total: {pred['predicted_total']}")
    lines.append(f"  Home Expected: {pred['home_expected']}")
    lines.append(f"  Away Expected: {pred['away_expected']}")
    lines.append(f"  Expected Pace: {pred['expected_pace']}")
    
    if market_total:
        lines.append(f"\nMarket O/U: {market_total}")
        edge = pred['predicted_total'] - market_total
        side = 'OVER' if edge > 0 else 'UNDER'
        lines.append(f"Edge: {abs(edge):.1f} pts {side}")
        if abs(edge) >= 3:
            lines.append(f">>> VALUE: {side} {market_total} <<<")
    
    return '\n'.join(lines)


if __name__ == "__main__":
    model = TotalsModel()
    model.load_data()
    
    # Test some games
    test_games = [
        ('OKC', 'MEM'),  # Fast vs fast
        ('MIN', 'ORL'),  # Slow vs slow
        ('IND', 'BOS'),  # Run and gun matchup
    ]
    
    for home, away in test_games:
        pred = model.predict_total(home, away)
        print(format_total_prediction(pred))
        
        matchup = model.explain_matchup(home, away)
        print(f"\nMatchup Analysis:")
        print(f"  {home}: Pace {matchup['home']['pace']}, O {matchup['home']['offense']}, D {matchup['home']['defense']}")
        print(f"  {away}: Pace {matchup['away']['pace']}, O {matchup['away']['offense']}, D {matchup['away']['defense']}")
        print(f"  Notes: {matchup['matchup_notes']}")
        print()
