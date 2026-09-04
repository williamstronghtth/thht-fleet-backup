#!/usr/bin/env python3
"""
NBA Model V3 Backtest
Walk-forward analysis on 2025-26 season

Methodology (Pardo):
- Train on games BEFORE each date
- 1 pick per day (best edge)
- Include vig (-110)
- Track CLV where possible
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from collections import defaultdict
import os

DATA_DIR = os.path.dirname(os.path.abspath(__file__)) + "/data"

# ============ CONSTANTS ============

BASE_HCA = 3.9
ALTITUDE_TEAMS = ['DEN', 'UTA']
ALTITUDE_BONUS = 1.0
EDGE_MIN = 2.0
EDGE_SWEET_SPOT = (2.0, 4.0)
EDGE_DANGER = 6.0

# Team name mapping
TEAM_MAP = {
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
    'Sacramento Kings': 'SAC', 'Washington Wizards': 'WAS'
}

ABBREV_MAP = {v: k for k, v in TEAM_MAP.items()}


def load_ratings():
    """Load team ratings from CSV"""
    ratings_path = f"{DATA_DIR}/team_ratings_2026.csv"
    df = pd.read_csv(ratings_path)
    
    ratings = {}
    for _, row in df.iterrows():
        team_name = row.iloc[1]  # Team name is second column
        abbrev = TEAM_MAP.get(team_name, team_name[:3].upper())
        
        ratings[abbrev] = {
            'ORtg': float(row.iloc[8]),   # Unadjusted_ORtg
            'DRtg': float(row.iloc[9]),   # Unadjusted_DRtg
            'NRtg': float(row.iloc[10]),  # Unadjusted_NRtg
            'W': int(row.iloc[4]),
            'L': int(row.iloc[5]),
        }
    
    return ratings


def load_games():
    """Load season games"""
    games_path = f"{DATA_DIR}/season_games_2026.json"
    with open(games_path, 'r') as f:
        games = json.load(f)
    
    # Parse and structure games
    parsed = []
    for g in games:
        try:
            # Parse date
            date_str = g['date']
            date = datetime.strptime(date_str, "%a, %b %d, %Y")
            
            home = TEAM_MAP.get(g['home_team'], g['home_team'][:3].upper())
            away = TEAM_MAP.get(g['away_team'], g['away_team'][:3].upper())
            
            parsed.append({
                'date': date,
                'home': home,
                'away': away,
                'home_score': g['home_score'],
                'away_score': g['away_score'],
                'margin': g['margin'],  # Positive = home win
            })
        except Exception as e:
            continue
    
    return sorted(parsed, key=lambda x: x['date'])


def get_rolling_ratings(games, up_to_date, min_games=10):
    """Calculate ratings from games up to a specific date"""
    team_games = defaultdict(list)
    
    for g in games:
        if g['date'] >= up_to_date:
            break
        
        home, away = g['home'], g['away']
        margin = g['margin']
        
        # Home perspective
        team_games[home].append({
            'margin': margin,
            'home': True,
            'opp': away,
        })
        # Away perspective
        team_games[away].append({
            'margin': -margin,
            'home': False,
            'opp': home,
        })
    
    # Calculate simple ratings
    ratings = {}
    for team, games_list in team_games.items():
        if len(games_list) < min_games:
            ratings[team] = {'NRtg': 0, 'games': len(games_list)}
            continue
        
        # Adjust for home/away
        adj_margins = []
        for g in games_list:
            adj = g['margin']
            if g['home']:
                adj -= BASE_HCA  # Remove HCA for neutral
            else:
                adj += BASE_HCA
            adj_margins.append(adj)
        
        ratings[team] = {
            'NRtg': np.mean(adj_margins),
            'games': len(games_list),
        }
    
    return ratings


def predict_spread(home, away, ratings):
    """Predict spread using current ratings"""
    home_rtg = ratings.get(home, {'NRtg': 0})['NRtg']
    away_rtg = ratings.get(away, {'NRtg': 0})['NRtg']
    
    # Bayesian shrinkage
    home_games = ratings.get(home, {'games': 0})['games']
    away_games = ratings.get(away, {'games': 0})['games']
    
    prior_weight = 15
    home_shrunk = home_rtg * (home_games / (home_games + prior_weight))
    away_shrunk = away_rtg * (away_games / (away_games + prior_weight))
    
    # Predict
    raw = (home_shrunk - away_shrunk) / 2
    hca = BASE_HCA + (ALTITUDE_BONUS if home in ALTITUDE_TEAMS else 0)
    
    predicted = raw + hca
    predicted = np.clip(predicted, -15, 15)
    
    return predicted


def simulate_market_line(actual_margin, noise_std=2.5):
    """
    Simulate what the market line might have been
    In reality we'd need historical odds data
    Add noise to actual margin to simulate market inefficiency
    """
    # Market is pretty efficient, so line is close to outcome on average
    # But we add noise to simulate the uncertainty
    market_line = -actual_margin + np.random.normal(0, noise_std)
    return round(market_line * 2) / 2  # Round to 0.5


def run_backtest():
    """Main backtest loop"""
    print("=" * 70)
    print("NBA MODEL V3 BACKTEST - 2025-26 SEASON")
    print("=" * 70)
    
    games = load_games()
    print(f"\nLoaded {len(games)} games")
    print(f"Date range: {games[0]['date'].strftime('%Y-%m-%d')} to {games[-1]['date'].strftime('%Y-%m-%d')}")
    
    # Group games by date
    games_by_date = defaultdict(list)
    for g in games:
        date_key = g['date'].strftime('%Y-%m-%d')
        games_by_date[date_key].append(g)
    
    dates = sorted(games_by_date.keys())
    print(f"Total game days: {len(dates)}")
    
    # Start after first 2 weeks (need data to train)
    start_idx = 14
    
    # Track results
    picks = []
    
    print(f"\nStarting backtest from day {start_idx} ({dates[start_idx]})")
    print("-" * 70)
    
    for i, date in enumerate(dates[start_idx:], start=start_idx):
        # Get ratings from games before this date
        current_date = datetime.strptime(date, '%Y-%m-%d')
        ratings = get_rolling_ratings(games, current_date)
        
        # Evaluate all games on this date
        candidates = []
        for g in games_by_date[date]:
            home, away = g['home'], g['away']
            actual_margin = g['margin']
            
            # Skip if teams don't have enough games
            if ratings.get(home, {'games': 0})['games'] < 5:
                continue
            if ratings.get(away, {'games': 0})['games'] < 5:
                continue
            
            # Predict
            predicted = predict_spread(home, away, ratings)
            
            # Simulate market line (in real backtest, use historical lines)
            # Here we're using actual margin + noise as proxy
            market_line = simulate_market_line(actual_margin)
            
            # Calculate edge (model says home favored by predicted, market says by -market_line)
            model_line = -predicted  # Convert to market convention
            edge = model_line - market_line  # Positive = value on home
            
            if abs(edge) >= EDGE_MIN:
                if edge > 0:
                    side = home
                    bet_line = market_line
                    won = actual_margin > -market_line
                else:
                    side = away
                    bet_line = -market_line
                    won = actual_margin < -market_line
                
                candidates.append({
                    'date': date,
                    'game': f"{away} @ {home}",
                    'side': side,
                    'line': bet_line,
                    'edge': abs(edge),
                    'predicted': predicted,
                    'actual': actual_margin,
                    'won': won,
                    'quality': 'SWEET' if EDGE_SWEET_SPOT[0] <= abs(edge) <= EDGE_SWEET_SPOT[1] else 
                              ('DANGER' if abs(edge) > EDGE_DANGER else 'PLAY'),
                })
        
        # Pick best candidate (prefer sweet spot, then highest edge)
        if candidates:
            # Sort: sweet spot first, then by edge
            candidates.sort(key=lambda x: (
                x['quality'] != 'SWEET',  # Sweet spot first
                x['quality'] == 'DANGER',  # Danger last
                -x['edge']  # Then by edge
            ))
            
            # Pick top 4 candidates (skip danger zone)
            valid = [c for c in candidates if c['quality'] != 'DANGER']
            for pick in valid[:4]:  # Top 4 per day
                picks.append(pick)
    
    # Results
    print(f"\n{'=' * 70}")
    print("BACKTEST RESULTS")
    print("=" * 70)
    
    if not picks:
        print("No picks generated!")
        return
    
    wins = sum(1 for p in picks if p['won'])
    total = len(picks)
    win_pct = wins / total * 100
    
    # Calculate P&L (at -110)
    profit = 0
    for p in picks:
        if p['won']:
            profit += 100 / 110  # Win $100 on $110 bet
        else:
            profit -= 1  # Lose 1 unit
    
    roi = profit / total * 100
    
    print(f"\nTotal picks: {total}")
    print(f"Record: {wins}-{total-wins} ({win_pct:.1f}%)")
    print(f"Profit: {profit:+.2f} units")
    print(f"ROI: {roi:+.2f}%")
    
    # By quality
    print("\nBy Edge Quality:")
    for quality in ['SWEET', 'PLAY']:
        q_picks = [p for p in picks if p['quality'] == quality]
        if q_picks:
            q_wins = sum(1 for p in q_picks if p['won'])
            q_pct = q_wins / len(q_picks) * 100
            print(f"  {quality}: {q_wins}-{len(q_picks)-q_wins} ({q_pct:.1f}%)")
    
    # Monthly breakdown
    print("\nBy Month:")
    monthly = defaultdict(lambda: {'wins': 0, 'total': 0})
    for p in picks:
        month = p['date'][:7]
        monthly[month]['total'] += 1
        if p['won']:
            monthly[month]['wins'] += 1
    
    for month in sorted(monthly.keys()):
        m = monthly[month]
        pct = m['wins'] / m['total'] * 100 if m['total'] > 0 else 0
        print(f"  {month}: {m['wins']}-{m['total']-m['wins']} ({pct:.1f}%)")
    
    # Sample picks
    print("\nSample Recent Picks:")
    for p in picks[-10:]:
        result = "✅" if p['won'] else "❌"
        print(f"  {p['date']}: {p['side']} {p['line']:+.1f} ({p['edge']:.1f}pt edge) → {result}")
    
    # Statistical significance check
    print("\n" + "=" * 70)
    print("STATISTICAL NOTES (Pardo/Buchdahl)")
    print("=" * 70)
    
    # Binomial test
    from scipy import stats
    break_even = 0.524  # At -110
    p_value = stats.binom_test(wins, total, break_even, alternative='greater')
    
    print(f"\nNull hypothesis: True win rate = {break_even:.1%} (break-even)")
    print(f"Observed: {win_pct:.1f}%")
    print(f"P-value: {p_value:.4f}")
    
    if p_value < 0.05:
        print("→ SIGNIFICANT at 95% confidence ✅")
    elif p_value < 0.10:
        print("→ Marginally significant (90% confidence)")
    else:
        print("→ NOT SIGNIFICANT - Could be luck ⚠️")
    
    print(f"\nPardo's rule: Need ~200+ bets for reliable significance")
    print(f"Current sample: {total} bets")
    if total < 200:
        print("→ Sample size too small for strong conclusions")
    
    return picks


if __name__ == "__main__":
    picks = run_backtest()
