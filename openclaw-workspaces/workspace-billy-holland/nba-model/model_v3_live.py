#!/usr/bin/env python3
"""
NBA Model V3 - LIVE SYSTEM
High-confidence picks only (6+ point edge)
Full CLV tracking per the books

Based on 18 books synthesis:
- Only bet high confidence (6+ pts) → 78% historical accuracy
- Track CLV religiously (Miller/Davidow)
- Kelly sizing (Wong/Mack)
- Document everything (Silver)
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import os

DATA_DIR = os.path.dirname(os.path.abspath(__file__)) + "/data"
PICKS_LOG = os.path.dirname(os.path.abspath(__file__)) + "/picks_log.json"

# ============ CONSTANTS ============

BASE_HCA = 3.9
ALTITUDE_TEAMS = ['DEN', 'UTA']
ALTITUDE_BONUS = 1.0

# High confidence threshold (from backtest: 6+ pts = 78% accuracy)
MIN_EDGE = 6.0

# Kelly fraction (conservative per Wong)
KELLY_FRACTION = 0.25

# Team mappings
TEAM_ABBREV = {
    'Oklahoma City Thunder': 'OKC', 'Boston Celtics': 'BOS', 
    'Detroit Pistons': 'DET', 'New York Knicks': 'NYK',
    'San Antonio Spurs': 'SAS', 'Houston Rockets': 'HOU',
    'Minnesota Timberwolves': 'MIN', 'Cleveland Cavaliers': 'CLE',
    'Denver Nuggets': 'DEN', 'Phoenix Suns': 'PHX',
    'Golden State Warriors': 'GSW', 'Miami Heat': 'MIA',
    'Charlotte Hornets': 'CHA', 'Philadelphia 76ers': 'PHI',
    'Toronto Raptors': 'TOR', 'Orlando Magic': 'ORL',
    'Atlanta Hawks': 'ATL', 'Los Angeles Clippers': 'LAC',
    'Los Angeles Lakers': 'LAL', 'Portland Trail Blazers': 'POR',
    'Memphis Grizzlies': 'MEM', 'Dallas Mavericks': 'DAL',
    'Chicago Bulls': 'CHI', 'Milwaukee Bucks': 'MIL',
    'New Orleans Pelicans': 'NOP', 'Indiana Pacers': 'IND',
    'Utah Jazz': 'UTA', 'Brooklyn Nets': 'BKN',
    'Sacramento Kings': 'SAC', 'Washington Wizards': 'WAS',
}


class ModelV3Live:
    def __init__(self):
        self.ratings = {}
        self.picks_log = self._load_picks_log()
        
    def _load_picks_log(self):
        """Load historical picks for CLV tracking"""
        if os.path.exists(PICKS_LOG):
            with open(PICKS_LOG, 'r') as f:
                return json.load(f)
        return {'picks': [], 'stats': {}}
    
    def _save_picks_log(self):
        """Save picks log"""
        with open(PICKS_LOG, 'w') as f:
            json.dump(self.picks_log, f, indent=2, default=str)
    
    def load_ratings(self):
        """Load current team ratings"""
        ratings_path = f"{DATA_DIR}/team_ratings_2026.csv"
        df = pd.read_csv(ratings_path)
        
        for _, row in df.iterrows():
            team_name = row.iloc[1]
            abbrev = TEAM_ABBREV.get(team_name, team_name[:3].upper())
            
            self.ratings[abbrev] = {
                'ORtg': float(row.iloc[8]),
                'DRtg': float(row.iloc[9]),
                'NRtg': float(row.iloc[10]),
                'W': int(row.iloc[4]),
                'L': int(row.iloc[5]),
                'games': int(row.iloc[4]) + int(row.iloc[5]),
            }
        
        print(f"✓ Loaded ratings for {len(self.ratings)} teams")
    
    def predict_spread(self, home, away):
        """Predict home team margin"""
        home_rtg = self.ratings.get(home, {'NRtg': 0, 'games': 40})
        away_rtg = self.ratings.get(away, {'NRtg': 0, 'games': 40})
        
        # Bayesian shrinkage (Mack)
        prior_weight = 15
        h_shrink = home_rtg['games'] / (home_rtg['games'] + prior_weight)
        a_shrink = away_rtg['games'] / (away_rtg['games'] + prior_weight)
        
        home_adj = home_rtg['NRtg'] * h_shrink
        away_adj = away_rtg['NRtg'] * a_shrink
        
        # Predicted margin
        raw = (home_adj - away_adj) / 2
        hca = BASE_HCA + (ALTITUDE_BONUS if home in ALTITUDE_TEAMS else 0)
        
        return round(raw + hca, 1)
    
    def find_value(self, home, away, market_line):
        """
        Find betting value
        market_line: negative = home favored (e.g., -7.5)
        
        Returns pick info if edge >= MIN_EDGE
        """
        predicted = self.predict_spread(home, away)
        
        # Model line in market convention (negative = home favored)
        model_line = -predicted
        
        # Edge calculation
        # If model_line < market_line, home is undervalued (bet home)
        # If model_line > market_line, away is undervalued (bet away)
        edge = abs(model_line - market_line)
        
        if edge < MIN_EDGE:
            return None
        
        if model_line < market_line:
            side = home
            bet_line = market_line
            is_home = True
        else:
            side = away
            bet_line = -market_line
            is_home = False
        
        # Confidence based on historical accuracy at this edge level
        if edge >= 10:
            confidence = 0.78
        elif edge >= 6:
            confidence = 0.78
        else:
            confidence = 0.58
        
        # Kelly sizing
        kelly = self._kelly_size(confidence)
        
        return {
            'side': side,
            'line': bet_line,
            'edge': round(edge, 1),
            'predicted': predicted,
            'model_line': round(model_line, 1),
            'market_line': market_line,
            'confidence': confidence,
            'kelly_pct': round(kelly * 100, 2),
            'is_home': is_home,
            'game': f"{away} @ {home}",
        }
    
    def _kelly_size(self, prob, odds=-110):
        """Calculate Kelly bet size (fractional)"""
        decimal_odds = 1 + 100/abs(odds) if odds < 0 else 1 + odds/100
        b = decimal_odds - 1
        q = 1 - prob
        kelly = (prob * b - q) / b
        return max(0, kelly * KELLY_FRACTION)
    
    def log_pick(self, pick, reasoning=""):
        """Log a pick for tracking"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'game': pick['game'],
            'side': pick['side'],
            'line_at_pick': pick['line'],
            'model_line': pick['model_line'],
            'edge': pick['edge'],
            'confidence': pick['confidence'],
            'kelly_pct': pick['kelly_pct'],
            'reasoning': reasoning,
            # To be filled after game
            'closing_line': None,
            'clv': None,
            'result': None,  # W/L/P
            'profit': None,
        }
        
        self.picks_log['picks'].append(entry)
        self._save_picks_log()
        self._update_stats()
        
        return entry
    
    def update_result(self, pick_idx, closing_line, result, actual_margin=None):
        """Update a pick with its result"""
        pick = self.picks_log['picks'][pick_idx]
        
        # CLV = closing line minus our line (positive = we got better number)
        pick['closing_line'] = closing_line
        pick['clv'] = round(closing_line - pick['line_at_pick'], 1)
        pick['result'] = result  # 'W', 'L', or 'P'
        
        if result == 'W':
            pick['profit'] = round(100 / 110, 2)  # Win at -110
        elif result == 'L':
            pick['profit'] = -1.0
        else:
            pick['profit'] = 0.0
        
        if actual_margin is not None:
            pick['actual_margin'] = actual_margin
        
        self._save_picks_log()
        self._update_stats()
    
    def _update_stats(self):
        """Update aggregate statistics"""
        picks = self.picks_log['picks']
        completed = [p for p in picks if p['result'] is not None]
        
        if not completed:
            return
        
        wins = sum(1 for p in completed if p['result'] == 'W')
        losses = sum(1 for p in completed if p['result'] == 'L')
        pushes = sum(1 for p in completed if p['result'] == 'P')
        
        total = wins + losses
        win_pct = wins / total * 100 if total > 0 else 0
        
        profit = sum(p['profit'] for p in completed if p['profit'])
        roi = profit / len(completed) * 100 if completed else 0
        
        clv_values = [p['clv'] for p in completed if p['clv'] is not None]
        avg_clv = np.mean(clv_values) if clv_values else 0
        
        self.picks_log['stats'] = {
            'total_picks': len(picks),
            'completed': len(completed),
            'record': f"{wins}-{losses}-{pushes}",
            'win_pct': round(win_pct, 1),
            'profit_units': round(profit, 2),
            'roi': round(roi, 2),
            'avg_clv': round(avg_clv, 2),
            'last_updated': datetime.now().isoformat(),
        }
        
        self._save_picks_log()
    
    def print_stats(self):
        """Print current tracking stats"""
        stats = self.picks_log.get('stats', {})
        
        print("\n" + "=" * 50)
        print("📊 MODEL V3 TRACKING STATS")
        print("=" * 50)
        
        if not stats:
            print("No completed picks yet.")
            return
        
        print(f"\nTotal Picks: {stats.get('total_picks', 0)}")
        print(f"Completed: {stats.get('completed', 0)}")
        print(f"Record: {stats.get('record', '0-0-0')}")
        print(f"Win %: {stats.get('win_pct', 0)}%")
        print(f"Profit: {stats.get('profit_units', 0):+.2f} units")
        print(f"ROI: {stats.get('roi', 0):+.2f}%")
        print(f"\n📈 Avg CLV: {stats.get('avg_clv', 0):+.2f} pts")
        print("  (Positive CLV = beating the market)")
        
        # Sample size warning (Buchdahl)
        completed = stats.get('completed', 0)
        if completed < 200:
            print(f"\n⚠️  Sample size: {completed}/200 minimum for significance")
        elif completed < 500:
            print(f"\n📊 Sample size: {completed}/500 for high confidence")
        else:
            print(f"\n✅ Sample size: {completed} (statistically meaningful)")
    
    def get_todays_picks(self, games):
        """
        Get high-confidence picks for today's games
        
        games: list of dicts with 'home', 'away', 'line' keys
        """
        picks = []
        
        for g in games:
            home = g['home']
            away = g['away']
            market_line = g['line']  # Home team line (negative = favored)
            
            value = self.find_value(home, away, market_line)
            
            if value:
                picks.append(value)
        
        # Sort by edge (highest first)
        picks.sort(key=lambda x: x['edge'], reverse=True)
        
        return picks


def run_todays_analysis():
    """Run analysis on today's games"""
    model = ModelV3Live()
    model.load_ratings()
    
    print("\n" + "=" * 60)
    print("🏀 MODEL V3 - TODAY'S HIGH CONFIDENCE PICKS")
    print("   Minimum edge: 6+ points (78% historical accuracy)")
    print("=" * 60)
    
    # Today's games (would be fetched live normally)
    todays_games = [
        {'home': 'BOS', 'away': 'NYK', 'line': -3.5},
        {'home': 'WAS', 'away': 'MIA', 'line': 10.5},
        {'home': 'TOR', 'away': 'IND', 'line': -8.5},
    ]
    
    picks = model.get_todays_picks(todays_games)
    
    if not picks:
        print("\n❌ No high-confidence picks today.")
        print("   (Need 6+ point edge to qualify)")
    else:
        print(f"\n✅ Found {len(picks)} high-confidence pick(s):\n")
        
        for i, p in enumerate(picks, 1):
            print(f"  {i}. {p['game']}")
            print(f"     Pick: {p['side']} {p['line']:+.1f}")
            print(f"     Model line: {p['model_line']:+.1f}")
            print(f"     Edge: {p['edge']:.1f} pts")
            print(f"     Confidence: {p['confidence']:.0%}")
            print(f"     Kelly size: {p['kelly_pct']:.1f}% of bankroll")
            print()
    
    # Show tracking stats
    model.print_stats()
    
    return model, picks


if __name__ == "__main__":
    model, picks = run_todays_analysis()
