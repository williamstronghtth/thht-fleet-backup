#!/usr/bin/env python3
"""
NBA Betting Model v1
Combines principles from NBA-Predict, Deepshot, and custom reliability scoring
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json
import os

# Import player impact module
try:
    from player_impact import get_player_impact
except ImportError:
    def get_player_impact(name): return 0.0

DATA_DIR = os.path.dirname(os.path.abspath(__file__)) + "/data"

# Home court advantage (backtest showed we underrate home teams by 1.4 pts)
# Bumped from 3.2 → 3.9 based on 769-game backtest
HOME_COURT_ADV = 3.9

# Max predicted margin (extreme predictions backfire per backtest)
MAX_MARGIN = 10.0

# Edge quality thresholds (backtest: 4+ pt edges are wrong 64% of time)
EDGE_SWEET_SPOT = (2.0, 4.0)  # Best performing range
EDGE_DANGER_ZONE = 4.0  # Edges above this are unreliable

# Rest adjustments (points)
REST_ADJ = {
    0: -3.0,   # Back-to-back
    1: 0.0,    # 1 day rest (normal)
    2: 0.5,    # 2 days rest
    3: 1.0,    # 3+ days rest
}

# EWMA span for recent form (Deepshot approach)
EWMA_SPAN = 10  # Games

# Map ESPN abbreviations to Basketball Reference team names
ABBREV_TO_TEAM = {
    'ATL': 'Atlanta Hawks', 'BOS': 'Boston Celtics', 'BKN': 'Brooklyn Nets',
    'CHA': 'Charlotte Hornets', 'CHI': 'Chicago Bulls', 'CLE': 'Cleveland Cavaliers',
    'DAL': 'Dallas Mavericks', 'DEN': 'Denver Nuggets', 'DET': 'Detroit Pistons',
    'GSW': 'Golden State Warriors', 'GS': 'Golden State Warriors',
    'HOU': 'Houston Rockets', 'IND': 'Indiana Pacers',
    'LAC': 'Los Angeles Clippers', 'LA': 'Los Angeles Clippers',
    'LAL': 'Los Angeles Lakers', 'MEM': 'Memphis Grizzlies',
    'MIA': 'Miami Heat', 'MIL': 'Milwaukee Bucks', 'MIN': 'Minnesota Timberwolves',
    'NOP': 'New Orleans Pelicans', 'NO': 'New Orleans Pelicans',
    'NYK': 'New York Knicks', 'NY': 'New York Knicks',
    'OKC': 'Oklahoma City Thunder', 'ORL': 'Orlando Magic',
    'PHI': 'Philadelphia 76ers', 'PHX': 'Phoenix Suns', 'PHO': 'Phoenix Suns',
    'POR': 'Portland Trail Blazers', 'SAC': 'Sacramento Kings',
    'SAS': 'San Antonio Spurs', 'SA': 'San Antonio Spurs',
    'TOR': 'Toronto Raptors', 'UTA': 'Utah Jazz', 'UTAH': 'Utah Jazz',
    'WAS': 'Washington Wizards', 'WSH': 'Washington Wizards'
}


class NBAModel:
    """
    NBA Game Prediction Model
    
    Core formula (spread prediction):
    Expected Margin = (Home ORtg - Away DRtg) - (Away ORtg - Home DRtg)
                    + Home Court Advantage
                    + Rest Adjustment (Home - Away)
                    + Momentum Adjustment (EWMA of recent performance)
                    + Injury Adjustment
    """
    
    def __init__(self):
        self.team_ratings = None
        self.team_stats = None
        
    def load_data(self, season="2026"):
        """Load team ratings and stats from cached files"""
        try:
            ratings_file = f"{DATA_DIR}/team_ratings_{season}.csv"
            if os.path.exists(ratings_file):
                self.team_ratings = pd.read_csv(ratings_file)
                print(f"Loaded ratings for {len(self.team_ratings)} teams")
            else:
                print(f"No ratings file found: {ratings_file}")
                return False
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def get_team_rating(self, team_abbrev):
        """
        Get ORtg, DRtg, Pace for a team
        Returns dict with ratings or defaults if not found
        """
        if self.team_ratings is None:
            return {'ORtg': 110.0, 'DRtg': 110.0, 'Pace': 100.0, 'NRtg': 0.0}
        
        # Convert abbreviation to full team name
        team_name = ABBREV_TO_TEAM.get(team_abbrev.upper(), team_abbrev)
        
        # Find team row - look for team name in any column that might contain it
        team_row = None
        for col in self.team_ratings.columns:
            if 'team' in col.lower() or 'unnamed' in col.lower():
                try:
                    mask = self.team_ratings[col].astype(str).str.contains(team_name, case=False, na=False)
                    if mask.any():
                        team_row = self.team_ratings[mask].iloc[0]
                        break
                except:
                    continue
        
        if team_row is None:
            print(f"Warning: Team {team_abbrev} ({team_name}) not found, using league avg")
            return {'ORtg': 110.0, 'DRtg': 110.0, 'Pace': 100.0, 'NRtg': 0.0}
        
        # Extract ratings (handle Basketball Reference column format)
        def get_col(df_row, patterns, default):
            for col_name in df_row.index:
                col_lower = col_name.lower()
                for pattern in patterns:
                    if pattern.lower() in col_lower:
                        try:
                            return float(df_row[col_name])
                        except:
                            pass
            return default
        
        return {
            'ORtg': get_col(team_row, ['ORtg', 'Adjusted_ORtg', 'ortg/a'], 110.0),
            'DRtg': get_col(team_row, ['DRtg', 'Adjusted_DRtg', 'drtg/a'], 110.0),
            'Pace': get_col(team_row, ['Pace'], 100.0),
            'NRtg': get_col(team_row, ['NRtg', 'Adjusted_NRtg', 'nrtg/a', 'mov'], 0.0)
        }
    
    def calculate_momentum(self, recent_margins, span=EWMA_SPAN):
        """
        Calculate EWMA-based momentum score
        recent_margins: list of point differentials (positive = win)
        Returns adjustment in points
        """
        if not recent_margins:
            return 0.0
        
        # Convert to series and calculate EWMA
        margins = pd.Series(recent_margins[-span:])
        ewma = margins.ewm(span=min(len(margins), span)).mean().iloc[-1]
        
        # Scale to reasonable adjustment (-3 to +3 points)
        momentum_adj = np.clip(ewma / 5.0, -3.0, 3.0)
        return momentum_adj
    
    def predict_spread(self, home_team, away_team, home_rest=1, away_rest=1,
                       home_injuries=0.0, away_injuries=0.0,
                       home_momentum=[], away_momentum=[]):
        """
        Predict point spread for a game
        
        Returns:
            dict with spread prediction and confidence
        """
        home_ratings = self.get_team_rating(home_team)
        away_ratings = self.get_team_rating(away_team)
        
        # Core formula: Expected points differential
        # Home team expected scoring advantage
        home_scoring = home_ratings['ORtg'] - away_ratings['DRtg']
        away_scoring = away_ratings['ORtg'] - home_ratings['DRtg']
        
        raw_margin = home_scoring - away_scoring
        
        # Adjustments
        hca_adj = HOME_COURT_ADV
        rest_adj = REST_ADJ.get(min(home_rest, 3), 0) - REST_ADJ.get(min(away_rest, 3), 0)
        momentum_adj = (self.calculate_momentum(home_momentum) - 
                       self.calculate_momentum(away_momentum))
        injury_adj = away_injuries - home_injuries  # Positive if away has more injuries
        
        # Total expected margin
        expected_margin = raw_margin + hca_adj + rest_adj + momentum_adj + injury_adj
        
        # Cap extreme predictions (backtest showed these backfire)
        expected_margin = np.clip(expected_margin, -MAX_MARGIN, MAX_MARGIN)
        
        # Reliability score (1-10)
        reliability = self.calculate_reliability(
            home_ratings, away_ratings, home_rest, away_rest,
            len(home_momentum), len(away_momentum)
        )
        
        return {
            'home_team': home_team,
            'away_team': away_team,
            'predicted_spread': round(expected_margin, 1),
            'home_favored': expected_margin > 0,
            'components': {
                'raw_margin': round(raw_margin, 2),
                'home_court': hca_adj,
                'rest_adj': round(rest_adj, 2),
                'momentum_adj': round(momentum_adj, 2),
                'injury_adj': round(injury_adj, 2)
            },
            'reliability': reliability,
            'home_ratings': home_ratings,
            'away_ratings': away_ratings
        }
    
    def predict_total(self, home_team, away_team):
        """
        Predict over/under total for a game
        """
        home_ratings = self.get_team_rating(home_team)
        away_ratings = self.get_team_rating(away_team)
        
        # Average pace
        avg_pace = (home_ratings['Pace'] + away_ratings['Pace']) / 2
        
        # Average efficiency (per 100 possessions)
        avg_off = (home_ratings['ORtg'] + away_ratings['ORtg']) / 2
        avg_def = (home_ratings['DRtg'] + away_ratings['DRtg']) / 2
        
        # Expected points (adjust pace to per-game)
        possessions_per_game = avg_pace * 0.98  # slight adjustment
        expected_total = (avg_off + avg_def) * possessions_per_game / 100
        
        return {
            'home_team': home_team,
            'away_team': away_team,
            'predicted_total': round(expected_total, 1),
            'pace_factor': round(avg_pace, 1)
        }
    
    def calculate_reliability(self, home_ratings, away_ratings, 
                             home_rest, away_rest, 
                             home_sample, away_sample):
        """
        Calculate reliability score (1-10) based on:
        - Data sample size
        - Rest day uncertainty
        - Rating confidence
        """
        score = 7.0  # Base score
        
        # Reduce for back-to-backs (more variance)
        if home_rest == 0 or away_rest == 0:
            score -= 1.0
        
        # Reduce for small sample of momentum data
        if home_sample < 5 or away_sample < 5:
            score -= 1.0
        
        # Increase for clear mismatch (more predictable)
        net_diff = abs(home_ratings['NRtg'] - away_ratings['NRtg'])
        if net_diff > 8:
            score += 1.0
        elif net_diff < 3:
            score -= 0.5
        
        return round(np.clip(score, 1, 10), 1)
    
    def find_value(self, prediction, market_spread):
        """
        Compare model spread to market spread to find value
        
        Market spread convention: negative = home favored (e.g., -6.5 means home -6.5)
        Model spread convention: positive = home favored (e.g., +6.5 means home -6.5)
        
        Returns:
            dict with value assessment
        """
        model_spread = prediction['predicted_spread']
        
        # Convert model spread to market convention (flip sign)
        model_line = -model_spread  # If model says home +6.5 favored, market equiv is -6.5
        
        # Edge = how much better is the market line than our model expects
        # Positive edge on home means home is getting more points than they should
        edge = market_spread - model_line
        
        # Determine if there's value (typically need 2+ point edge)
        VALUE_THRESHOLD = 2.0
        
        if abs(edge) >= VALUE_THRESHOLD:
            if edge > 0:
                # Market has home as bigger dog (or smaller fav) than model
                # Value is on HOME team at current line
                value_side = prediction['home_team']
                value_line = market_spread
            else:
                # Market has away as bigger dog (or smaller fav) than model  
                # Value is on AWAY team at current line
                value_side = prediction['away_team']
                value_line = -market_spread  # Flip for away perspective
                
            # Edge quality based on backtest (4+ pt edges are wrong 64% of time!)
            abs_edge = abs(edge)
            if EDGE_SWEET_SPOT[0] <= abs_edge <= EDGE_SWEET_SPOT[1]:
                edge_quality = 'SWEET_SPOT'  # Best performing range
                confidence = 'HIGH'
            elif abs_edge > EDGE_DANGER_ZONE:
                edge_quality = 'CAUTION'  # Historically unreliable
                confidence = 'LOW'  # Downgrade!
            else:
                edge_quality = 'MARGINAL'
                confidence = 'MEDIUM'
                
            return {
                'has_value': True,
                'edge': round(abs_edge, 1),
                'side': value_side,
                'line': value_line,
                'confidence': confidence,
                'edge_quality': edge_quality
            }
        
        return {'has_value': False, 'edge': round(abs(edge), 1), 'edge_quality': 'NO_VALUE'}


def format_prediction(pred, market_spread=None, market_total=None):
    """Format prediction for output"""
    lines = []
    lines.append(f"\n{'='*50}")
    lines.append(f"GAME: {pred['away_team']} @ {pred['home_team']}")
    lines.append(f"{'='*50}")
    
    # Spread
    spread_str = f"{pred['home_team']} {pred['predicted_spread']:+.1f}" if pred['predicted_spread'] > 0 else f"{pred['away_team']} {-pred['predicted_spread']:+.1f}"
    lines.append(f"Model Spread: {spread_str}")
    
    if market_spread is not None:
        lines.append(f"Market Spread: {pred['home_team']} {market_spread:+.1f}")
        edge = pred['predicted_spread'] - market_spread
        if abs(edge) >= 1.5:
            lines.append(f">>> VALUE: {abs(edge):.1f} pts edge <<<")
    
    lines.append(f"Reliability: {pred['reliability']}/10")
    
    # Components breakdown
    lines.append(f"\nComponents:")
    for k, v in pred['components'].items():
        lines.append(f"  {k}: {v:+.2f}")
    
    return '\n'.join(lines)


if __name__ == "__main__":
    model = NBAModel()
    model.load_data()
    
    # Test prediction
    pred = model.predict_spread('BOS', 'LAL', home_rest=1, away_rest=0)
    print(format_prediction(pred, market_spread=-5.5))
    
    total = model.predict_total('BOS', 'LAL')
    print(f"\nPredicted Total: {total['predicted_total']}")
