#!/usr/bin/env python3
"""
NBA Model V3 Backtest - Clean Methodology
Test: Does our model predict game outcomes better than chance?

Two tests:
1. DIRECTION: Did we predict who would win/cover correctly?
2. MARGIN ACCURACY: How close are our predictions to actual margins?
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime
from collections import defaultdict
import os

DATA_DIR = os.path.dirname(os.path.abspath(__file__)) + "/data"

# Constants
BASE_HCA = 3.9
ALTITUDE_TEAMS = ['DEN', 'UTA']
ALTITUDE_BONUS = 1.0

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


def load_games():
    """Load season games"""
    games_path = f"{DATA_DIR}/season_games_2026.json"
    with open(games_path, 'r') as f:
        games = json.load(f)
    
    parsed = []
    for g in games:
        try:
            date = datetime.strptime(g['date'], "%a, %b %d, %Y")
            home = TEAM_MAP.get(g['home_team'], g['home_team'][:3].upper())
            away = TEAM_MAP.get(g['away_team'], g['away_team'][:3].upper())
            
            parsed.append({
                'date': date,
                'home': home,
                'away': away,
                'home_score': g['home_score'],
                'away_score': g['away_score'],
                'margin': g['margin'],
            })
        except:
            continue
    
    return sorted(parsed, key=lambda x: x['date'])


def get_rolling_ratings(games, up_to_date, min_games=5):
    """Calculate ratings from games up to a specific date"""
    team_games = defaultdict(list)
    
    for g in games:
        if g['date'] >= up_to_date:
            break
        
        home, away = g['home'], g['away']
        margin = g['margin']
        
        team_games[home].append({'margin': margin, 'home': True})
        team_games[away].append({'margin': -margin, 'home': False})
    
    ratings = {}
    for team, games_list in team_games.items():
        if len(games_list) < min_games:
            ratings[team] = {'NRtg': 0, 'games': len(games_list)}
            continue
        
        adj_margins = []
        for g in games_list:
            adj = g['margin']
            adj -= BASE_HCA if g['home'] else -BASE_HCA
            adj_margins.append(adj)
        
        ratings[team] = {
            'NRtg': np.mean(adj_margins),
            'games': len(games_list),
        }
    
    return ratings


def predict_margin(home, away, ratings):
    """Predict home margin"""
    home_rtg = ratings.get(home, {'NRtg': 0, 'games': 0})
    away_rtg = ratings.get(away, {'NRtg': 0, 'games': 0})
    
    # Bayesian shrinkage
    prior_weight = 15
    h_weight = home_rtg['games'] / (home_rtg['games'] + prior_weight)
    a_weight = away_rtg['games'] / (away_rtg['games'] + prior_weight)
    
    home_shrunk = home_rtg['NRtg'] * h_weight
    away_shrunk = away_rtg['NRtg'] * a_weight
    
    raw = (home_shrunk - away_shrunk) / 2
    hca = BASE_HCA + (ALTITUDE_BONUS if home in ALTITUDE_TEAMS else 0)
    
    return np.clip(raw + hca, -20, 20)


def run_backtest():
    print("=" * 70)
    print("NBA MODEL V3 BACKTEST - CLEAN METHODOLOGY")
    print("=" * 70)
    
    games = load_games()
    print(f"\nLoaded {len(games)} games")
    
    # Start after 2 weeks
    start_date = games[0]['date'] + pd.Timedelta(days=14)
    
    results = []
    
    for g in games:
        if g['date'] < start_date:
            continue
        
        ratings = get_rolling_ratings(games, g['date'])
        
        if (ratings.get(g['home'], {'games': 0})['games'] < 5 or
            ratings.get(g['away'], {'games': 0})['games'] < 5):
            continue
        
        predicted = predict_margin(g['home'], g['away'], ratings)
        actual = g['margin']
        
        results.append({
            'date': g['date'],
            'game': f"{g['away']} @ {g['home']}",
            'predicted': predicted,
            'actual': actual,
            'pred_winner': g['home'] if predicted > 0 else g['away'],
            'actual_winner': g['home'] if actual > 0 else g['away'],
            'correct_winner': (predicted > 0) == (actual > 0),
            'error': abs(predicted - actual),
        })
    
    print(f"Total predictions: {len(results)}")
    
    # === ANALYSIS ===
    
    print("\n" + "=" * 70)
    print("TEST 1: WINNER PREDICTION (Moneyline)")
    print("=" * 70)
    
    correct = sum(1 for r in results if r['correct_winner'])
    pct = correct / len(results) * 100
    print(f"\nCorrect: {correct}/{len(results)} ({pct:.1f}%)")
    
    if pct > 50:
        print("→ Model predicts winners better than coin flip ✅")
    else:
        print("→ Model no better than coin flip ❌")
    
    print("\n" + "=" * 70)
    print("TEST 2: SPREAD PREDICTION (ATS Simulation)")
    print("=" * 70)
    
    # Simulate betting ATS: if we predict margin of X, and actual is Y,
    # we "win" if we're on the right side of 0 after accounting for spread
    
    # Use model prediction as the "fair line" and see if actual beats it
    ats_wins = 0
    ats_losses = 0
    pushes = 0
    
    for r in results:
        # Our prediction is the "line" we'd set
        # If actual > predicted, home covered our line
        # We always bet the side our model favors
        
        if r['predicted'] > 0:  # Model favors home
            # We bet home at our predicted spread
            # Home covers if actual > (predicted - some buffer)
            # Actually, let's simplify: model vs coin flip
            spread_diff = r['actual'] - r['predicted']
            if spread_diff > 0:
                ats_wins += 1  # Actual exceeded our prediction = we win
            elif spread_diff < 0:
                ats_losses += 1
            else:
                pushes += 1
        else:  # Model favors away
            spread_diff = r['actual'] - r['predicted']
            if spread_diff < 0:
                ats_wins += 1  # Actual less than predicted = away better than expected
            elif spread_diff > 0:
                ats_losses += 1
            else:
                pushes += 1
    
    total_ats = ats_wins + ats_losses
    ats_pct = ats_wins / total_ats * 100 if total_ats > 0 else 0
    
    print(f"\nATS Record: {ats_wins}-{ats_losses}-{pushes} ({ats_pct:.1f}%)")
    
    print("\n" + "=" * 70)
    print("TEST 3: MARGIN ACCURACY")
    print("=" * 70)
    
    errors = [r['error'] for r in results]
    mae = np.mean(errors)
    rmse = np.sqrt(np.mean([e**2 for e in errors]))
    
    print(f"\nMean Absolute Error (MAE): {mae:.1f} points")
    print(f"Root Mean Square Error (RMSE): {rmse:.1f} points")
    print(f"Median Error: {np.median(errors):.1f} points")
    
    # Compare to naive baseline (always predict HCA only)
    naive_errors = [abs(BASE_HCA - r['actual']) for r in results]
    naive_mae = np.mean(naive_errors)
    
    print(f"\nBaseline (predict HCA only): MAE = {naive_mae:.1f} points")
    if mae < naive_mae:
        print(f"→ Model beats baseline by {naive_mae - mae:.1f} points ✅")
    else:
        print(f"→ Model worse than baseline by {mae - naive_mae:.1f} points ❌")
    
    print("\n" + "=" * 70)
    print("TEST 4: BY CONFIDENCE (Edge Size)")
    print("=" * 70)
    
    # Group by how far our prediction was from 0 (higher = more confident)
    for confidence_level, (low, high) in [
        ("Low (0-3 pts)", (0, 3)),
        ("Medium (3-6 pts)", (3, 6)),
        ("High (6-10 pts)", (6, 10)),
        ("Very High (10+ pts)", (10, 100)),
    ]:
        subset = [r for r in results if low <= abs(r['predicted']) < high]
        if len(subset) > 10:
            correct = sum(1 for r in subset if r['correct_winner'])
            pct = correct / len(subset) * 100
            print(f"{confidence_level}: {correct}/{len(subset)} ({pct:.1f}%)")
    
    print("\n" + "=" * 70)
    print("TEST 5: BY MONTH (Time Stability)")
    print("=" * 70)
    
    monthly = defaultdict(list)
    for r in results:
        month = r['date'].strftime('%Y-%m')
        monthly[month].append(r)
    
    for month in sorted(monthly.keys()):
        subset = monthly[month]
        correct = sum(1 for r in subset if r['correct_winner'])
        pct = correct / len(subset) * 100
        mae = np.mean([r['error'] for r in subset])
        print(f"{month}: {correct}/{len(subset)} ({pct:.1f}%) | MAE: {mae:.1f}")
    
    print("\n" + "=" * 70)
    print("STATISTICAL SIGNIFICANCE")
    print("=" * 70)
    
    from scipy import stats
    
    # Binomial test for winner prediction
    _, p_value = stats.binomtest(correct, len(results), 0.5, alternative='greater')
    
    print(f"\nWinner prediction vs 50%:")
    print(f"  Observed: {pct:.1f}%")
    print(f"  P-value: {p_value:.4f}")
    if p_value < 0.05:
        print("  → SIGNIFICANT ✅")
    else:
        print("  → Not significant")
    
    return results


if __name__ == "__main__":
    results = run_backtest()
