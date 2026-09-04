#!/usr/bin/env python3
"""
NBA Player Props Model v1.0

Key insight: Books are slower to adjust player lines for:
1. Matchup-based adjustments (elite D vs poor D)
2. Pace adjustments (fast game = more possessions = more stats)
3. Injury-based usage bumps
4. Recent role changes

Focus on:
- Points (most liquid, most data)
- Rebounds (matchup dependent)
- Assists (pace/system dependent)
"""

import pandas as pd
import numpy as np
import os
import json

DATA_DIR = os.path.dirname(os.path.abspath(__file__)) + "/data"

# Defensive ratings by position (approximate)
# Lower = better defense
POSITION_DEFENSE = {
    # Format: team -> {position: rating vs that position}
    # This would ideally be scraped from BBRef or NBA.com
}

# Usage boost when star is out
USAGE_BUMP = {
    'primary': 1.15,    # Primary option gets 15% boost
    'secondary': 1.08,  # Secondary gets 8%
    'tertiary': 1.04,   # Others get 4%
}


class PropsModel:
    """
    Player props prediction model
    """
    
    def __init__(self):
        self.player_averages = {}
        self.pace_data = None
        
    def load_pace_data(self, season="2026"):
        """Load team pace for game projection"""
        try:
            pace_file = f"{DATA_DIR}/team_pace_{season}.csv"
            if os.path.exists(pace_file):
                self.pace_data = pd.read_csv(pace_file)
                self.pace_data['Team'] = self.pace_data['Team'].str.replace('*', '', regex=False)
                return True
        except:
            pass
        return False
    
    def get_team_pace(self, team_name):
        """Get team's pace"""
        if self.pace_data is None:
            return 99.0
        
        # Abbreviation mapping
        abbrev_map = {
            'BOS': 'Boston', 'LAL': 'Lakers', 'GSW': 'Golden State', 'GS': 'Golden State',
            'MIA': 'Miami', 'MIL': 'Milwaukee', 'PHI': 'Philadelphia', 'NYK': 'Knicks',
            'BKN': 'Brooklyn', 'TOR': 'Toronto', 'CHI': 'Chicago', 'CLE': 'Cleveland',
            'IND': 'Indiana', 'DET': 'Detroit', 'ATL': 'Atlanta', 'CHA': 'Charlotte',
            'ORL': 'Orlando', 'WAS': 'Washington', 'DEN': 'Denver', 'MIN': 'Minnesota',
            'OKC': 'Oklahoma', 'POR': 'Portland', 'UTA': 'Utah', 'PHX': 'Phoenix',
            'SAC': 'Sacramento', 'LAC': 'Clippers', 'DAL': 'Dallas', 'HOU': 'Houston',
            'SAS': 'San Antonio', 'MEM': 'Memphis', 'NOP': 'Pelicans', 'NO': 'Pelicans'
        }
        
        search = abbrev_map.get(team_name.upper(), team_name)
        for _, row in self.pace_data.iterrows():
            if search.lower() in row['Team'].lower():
                return float(row['Pace'])
        return 99.0
    
    def get_team_drtg(self, team_name):
        """Get team's defensive rating"""
        if self.pace_data is None:
            return 115.0
        
        abbrev_map = {
            'BOS': 'Boston', 'LAL': 'Lakers', 'GSW': 'Golden State', 'GS': 'Golden State',
            'MIA': 'Miami', 'MIL': 'Milwaukee', 'PHI': 'Philadelphia', 'NYK': 'Knicks',
            'BKN': 'Brooklyn', 'TOR': 'Toronto', 'CHI': 'Chicago', 'CLE': 'Cleveland',
            'IND': 'Indiana', 'DET': 'Detroit', 'ATL': 'Atlanta', 'CHA': 'Charlotte',
            'ORL': 'Orlando', 'WAS': 'Washington', 'DEN': 'Denver', 'MIN': 'Minnesota',
            'OKC': 'Oklahoma', 'POR': 'Portland', 'UTA': 'Utah', 'PHX': 'Phoenix',
            'SAC': 'Sacramento', 'LAC': 'Clippers', 'DAL': 'Dallas', 'HOU': 'Houston',
            'SAS': 'San Antonio', 'MEM': 'Memphis', 'NOP': 'Pelicans', 'NO': 'Pelicans'
        }
        
        search = abbrev_map.get(team_name.upper(), team_name)
        for _, row in self.pace_data.iterrows():
            if search.lower() in row['Team'].lower():
                return float(row['DRtg'])
        return 115.0
    
    def calculate_pace_factor(self, team, opponent):
        """Calculate pace adjustment for game"""
        team_pace = self.get_team_pace(team)
        opp_pace = self.get_team_pace(opponent)
        game_pace = (team_pace + opp_pace) / 2
        return game_pace / 99.0  # Ratio vs league average
    
    def calculate_matchup_factor(self, opponent):
        """
        Calculate defensive matchup adjustment
        Uses opponent DRtg to estimate scoring environment
        """
        opp_drtg = self.get_team_drtg(opponent)
        league_avg = 115.0
        
        # Higher DRtg = worse defense = easier to score
        # Each point of DRtg difference = ~1% adjustment
        matchup_factor = 1 + (opp_drtg - league_avg) / 100
        return matchup_factor
    
    def project_points(self, player_name, player_avg, player_team, opponent,
                      teammate_out=None, is_primary_scorer=False):
        """
        Project player's points for a specific game
        
        Args:
            player_name: Player name
            player_avg: Season PPG average
            player_team: Player's team
            opponent: Opponent team
            teammate_out: Name of injured star teammate (optional)
            is_primary_scorer: Is this player the primary scoring option?
        
        Returns: dict with projection and confidence
        """
        base = player_avg
        
        # Pace adjustment
        pace_factor = self.calculate_pace_factor(player_team, opponent)
        pace_adj = base * (pace_factor - 1)
        
        # Matchup adjustment
        matchup_factor = self.calculate_matchup_factor(opponent)
        matchup_adj = base * (matchup_factor - 1)
        
        # Injury/usage bump
        usage_adj = 0
        if teammate_out:
            if is_primary_scorer:
                usage_adj = base * (USAGE_BUMP['primary'] - 1)
            else:
                usage_adj = base * (USAGE_BUMP['secondary'] - 1)
        
        # Total projection
        projected = base + pace_adj + matchup_adj + usage_adj
        
        # Confidence based on sample size and adjustments
        total_adj = abs(pace_adj) + abs(matchup_adj) + abs(usage_adj)
        if total_adj > 5:
            confidence = 'HIGH'  # Large adjustments = potential edge
        elif total_adj > 3:
            confidence = 'MEDIUM'
        else:
            confidence = 'LOW'  # Close to average
        
        return {
            'player': player_name,
            'team': player_team,
            'opponent': opponent,
            'season_avg': player_avg,
            'projected': round(projected, 1),
            'adjustments': {
                'pace': round(pace_adj, 1),
                'matchup': round(matchup_adj, 1),
                'usage': round(usage_adj, 1)
            },
            'confidence': confidence
        }
    
    def find_points_value(self, projection, market_line):
        """
        Compare projected points to market line
        
        Returns: dict with value assessment
        """
        proj = projection['projected']
        edge = proj - market_line
        
        # Need ~2 pt edge on points props
        VALUE_THRESHOLD = 2.0
        
        if abs(edge) >= VALUE_THRESHOLD:
            side = 'OVER' if edge > 0 else 'UNDER'
            
            # Confidence
            if abs(edge) >= 4:
                bet_conf = 'HIGH'
            elif abs(edge) >= 3:
                bet_conf = 'MEDIUM'
            else:
                bet_conf = 'LOW'
            
            return {
                'has_value': True,
                'side': side,
                'line': market_line,
                'edge': round(abs(edge), 1),
                'bet_confidence': bet_conf,
                'projection': proj
            }
        
        return {'has_value': False, 'edge': round(abs(edge), 1)}


class ReboundsModel:
    """
    Rebounds props - heavily matchup dependent
    """
    
    def __init__(self, pace_data=None):
        self.pace_data = pace_data
    
    def get_team_orb_rate(self, team):
        """Get team's ORB% (opportunity for boards)"""
        # Would need to scrape this data
        # For now, return league average
        return 25.0
    
    def project_rebounds(self, player_name, player_avg, minutes, opponent,
                        opponent_pace, is_center=False):
        """
        Project rebounds for a game
        
        Key factors:
        - Pace (more possessions = more rebounds)
        - Opponent's miss rate
        - Player's rebounding role
        - Minutes played
        """
        base = player_avg
        
        # Pace adjustment (more misses in faster games)
        pace_factor = opponent_pace / 99.0
        pace_adj = base * (pace_factor - 1) * 0.5  # 50% weight
        
        # Minutes adjustment if known
        if minutes:
            min_factor = minutes / 32.0  # vs typical starter minutes
            min_adj = base * (min_factor - 1) * 0.3
        else:
            min_adj = 0
        
        projected = base + pace_adj + min_adj
        
        return {
            'player': player_name,
            'season_avg': player_avg,
            'projected': round(projected, 1),
            'adjustments': {
                'pace': round(pace_adj, 1),
                'minutes': round(min_adj, 1)
            }
        }


def format_points_projection(proj, market_line=None):
    """Format points projection"""
    lines = []
    lines.append(f"\n{proj['player']} ({proj['team']}) vs {proj['opponent']}")
    lines.append(f"  Season Avg: {proj['season_avg']} PPG")
    lines.append(f"  Projected: {proj['projected']} pts")
    lines.append(f"  Adjustments:")
    for k, v in proj['adjustments'].items():
        if v != 0:
            lines.append(f"    {k}: {v:+.1f}")
    
    if market_line:
        edge = proj['projected'] - market_line
        side = 'OVER' if edge > 0 else 'UNDER'
        lines.append(f"  Market Line: {market_line}")
        lines.append(f"  Edge: {abs(edge):.1f} pts {side}")
        if abs(edge) >= 2:
            lines.append(f"  >>> VALUE: {side} {market_line} <<<")
    
    return '\n'.join(lines)


if __name__ == "__main__":
    model = PropsModel()
    model.load_pace_data()
    
    # Test projections
    print("=" * 50)
    print("PLAYER PROPS PROJECTIONS")
    print("=" * 50)
    
    # SGA vs bad defense (Utah)
    proj = model.project_points(
        "Shai Gilgeous-Alexander",
        player_avg=31.5,
        player_team="OKC",
        opponent="UTA"
    )
    print(format_points_projection(proj, market_line=32.5))
    
    # Ant-Man vs elite defense (OKC)
    proj = model.project_points(
        "Anthony Edwards",
        player_avg=26.0,
        player_team="MIN",
        opponent="OKC"
    )
    print(format_points_projection(proj, market_line=25.5))
    
    # Tyrese Haliburton in fast game
    proj = model.project_points(
        "Tyrese Haliburton",
        player_avg=18.5,
        player_team="IND",
        opponent="ATL"  # Fast pace, poor D
    )
    print(format_points_projection(proj, market_line=18.5))
