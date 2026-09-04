#!/usr/bin/env python3
"""
NBA Model Backtest
Fetches completed 2025-26 season games and evaluates model performance
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import time
import os
import re

from model import NBAModel

DATA_DIR = os.path.dirname(os.path.abspath(__file__)) + "/data"
BR_BASE = "https://www.basketball-reference.com"

# Team abbreviations used by Basketball Reference
BR_TEAM_ABBREVS = {
    'Atlanta Hawks': 'ATL', 'Boston Celtics': 'BOS', 'Brooklyn Nets': 'BRK',
    'Charlotte Hornets': 'CHO', 'Chicago Bulls': 'CHI', 'Cleveland Cavaliers': 'CLE',
    'Dallas Mavericks': 'DAL', 'Denver Nuggets': 'DEN', 'Detroit Pistons': 'DET',
    'Golden State Warriors': 'GSW', 'Houston Rockets': 'HOU', 'Indiana Pacers': 'IND',
    'Los Angeles Clippers': 'LAC', 'Los Angeles Lakers': 'LAL', 'Memphis Grizzlies': 'MEM',
    'Miami Heat': 'MIA', 'Milwaukee Bucks': 'MIL', 'Minnesota Timberwolves': 'MIN',
    'New Orleans Pelicans': 'NOP', 'New York Knicks': 'NYK', 'Oklahoma City Thunder': 'OKC',
    'Orlando Magic': 'ORL', 'Philadelphia 76ers': 'PHI', 'Phoenix Suns': 'PHO',
    'Portland Trail Blazers': 'POR', 'Sacramento Kings': 'SAC', 'San Antonio Spurs': 'SAS',
    'Toronto Raptors': 'TOR', 'Utah Jazz': 'UTA', 'Washington Wizards': 'WAS',
    'LA Clippers': 'LAC'
}

# Reverse mapping
ABBREV_TO_FULL = {v: k for k, v in BR_TEAM_ABBREVS.items()}
# Add alternate abbreviations
ABBREV_TO_FULL['BKN'] = 'Brooklyn Nets'
ABBREV_TO_FULL['CHO'] = 'Charlotte Hornets'
ABBREV_TO_FULL['CHA'] = 'Charlotte Hornets'
ABBREV_TO_FULL['PHX'] = 'Phoenix Suns'


def fetch_season_schedule(season="2026"):
    """
    Fetch all games for the NBA season from Basketball Reference
    Season 2026 = 2025-26 season
    """
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    all_games = []
    
    # Fetch October through current month
    months = ['october', 'november', 'december', 'january', 'february', 'march', 'april']
    
    for month in months:
        month_url = f"{BR_BASE}/leagues/NBA_{season}_games-{month}.html"
        print(f"Fetching {month}...")
        
        try:
            resp = requests.get(month_url, headers=headers, timeout=30)
            if resp.status_code == 404:
                print(f"  No data for {month}")
                continue
            resp.raise_for_status()
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            table = soup.find('table', {'id': 'schedule'})
            
            if table is None:
                print(f"  No schedule table found for {month}")
                continue
            
            # Use pandas to parse the table
            from io import StringIO
            df = pd.read_html(StringIO(str(table)))[0]
            
            # Columns are: Date, Start (ET), Visitor/Neutral, PTS, Home/Neutral, PTS.1, ...
            month_games = 0
            for _, row in df.iterrows():
                try:
                    date_str = str(row.get('Date', ''))
                    if 'Date' in date_str or not date_str or pd.isna(row.get('Date')):
                        continue
                    
                    visitor = str(row.get('Visitor/Neutral', ''))
                    home = str(row.get('Home/Neutral', ''))
                    visitor_pts = row.get('PTS', '')
                    home_pts = row.get('PTS.1', '')
                    
                    # Skip if no scores (game not played yet)
                    if pd.isna(visitor_pts) or pd.isna(home_pts):
                        continue
                    if str(visitor_pts) == '' or str(home_pts) == '':
                        continue
                    
                    try:
                        v_score = int(float(visitor_pts))
                        h_score = int(float(home_pts))
                    except (ValueError, TypeError):
                        continue
                    
                    game = {
                        'date': date_str,
                        'away_team': visitor,
                        'home_team': home,
                        'away_score': v_score,
                        'home_score': h_score,
                        'margin': h_score - v_score  # positive = home won
                    }
                    all_games.append(game)
                    month_games += 1
                    
                except Exception as e:
                    continue
            
            print(f"  Found {month_games} completed games")
            time.sleep(2)  # Rate limiting
            
        except Exception as e:
            print(f"  Error fetching {month}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print(f"\nTotal completed games: {len(all_games)}")
    
    # Save to cache
    with open(f"{DATA_DIR}/season_games_{season}.json", 'w') as f:
        json.dump(all_games, f, indent=2)
    
    return all_games


def get_team_abbrev(team_name):
    """Convert full team name to abbreviation used by our model"""
    # Direct mapping
    abbrev = BR_TEAM_ABBREVS.get(team_name)
    if abbrev:
        # Convert BR abbreviations to model abbreviations
        if abbrev == 'BRK':
            return 'BKN'
        if abbrev == 'CHO':
            return 'CHA'
        if abbrev == 'PHO':
            return 'PHX'
        return abbrev
    
    # Try partial match
    team_lower = team_name.lower()
    for full_name, ab in BR_TEAM_ABBREVS.items():
        if team_lower in full_name.lower() or full_name.lower() in team_lower:
            if ab == 'BRK':
                return 'BKN'
            if ab == 'CHO':
                return 'CHA'
            if ab == 'PHO':
                return 'PHX'
            return ab
    
    return team_name[:3].upper()


def run_backtest(games, model):
    """
    Run model predictions on all games and compare to actual results
    """
    results = []
    
    for game in games:
        home_abbrev = get_team_abbrev(game['home_team'])
        away_abbrev = get_team_abbrev(game['away_team'])
        
        # Get model prediction
        pred = model.predict_spread(home_abbrev, away_abbrev)
        
        # Calculate actual margin (positive = home won)
        actual_margin = game['margin']
        predicted_margin = pred['predicted_spread']
        
        # Model's predicted winner
        model_home_favored = predicted_margin > 0
        actual_home_won = actual_margin > 0
        
        # Did model pick the winner correctly?
        winner_correct = model_home_favored == actual_home_won
        
        # Calculate spread error
        spread_error = actual_margin - predicted_margin
        
        result = {
            'date': game['date'],
            'home_team': home_abbrev,
            'away_team': away_abbrev,
            'home_score': game['home_score'],
            'away_score': game['away_score'],
            'actual_margin': actual_margin,
            'predicted_margin': predicted_margin,
            'spread_error': spread_error,
            'abs_error': abs(spread_error),
            'winner_correct': winner_correct,
            'home_ratings': pred['home_ratings'],
            'away_ratings': pred['away_ratings'],
            'reliability': pred['reliability']
        }
        results.append(result)
    
    return results


def calculate_ats_performance(results, edge_threshold=2.0):
    """
    Calculate ATS (against the spread) performance assuming we bet when we have an edge
    
    In real betting:
    - Model predicts spread
    - We compare to market line (hypothetically assume market line is closer to 0)
    - We bet when model has 2+ point edge
    
    Since we don't have historical market lines, we'll simulate:
    - Assume market line was actual_margin +/- some noise
    - Or simply: did model's predicted winner cover a reasonable spread?
    """
    ats_results = {
        'all': {'wins': 0, 'losses': 0, 'pushes': 0},
        'home_plays': {'wins': 0, 'losses': 0},
        'away_plays': {'wins': 0, 'losses': 0},
        'big_edge': {'wins': 0, 'losses': 0},  # 4+ point edge
        'medium_edge': {'wins': 0, 'losses': 0},  # 2-4 point edge
        'favorites': {'wins': 0, 'losses': 0},  # When we back favorites
        'underdogs': {'wins': 0, 'losses': 0}   # When we back underdogs
    }
    
    plays = []
    
    for r in results:
        pred_margin = r['predicted_margin']
        actual_margin = r['actual_margin']
        edge = abs(pred_margin)  # How much we think home team wins/loses by
        
        # Only consider plays where model has strong opinion (2+ points)
        if edge >= edge_threshold:
            # We're betting on whoever model favors
            if pred_margin > 0:
                # Model likes home team to cover
                # Home covers if actual margin > predicted margin - edge_threshold
                # Actually, let's use a simpler approach:
                # If model says home -5, they cover if actual margin > 5 - 2 = 3
                # This simulates that market might have home at -3
                
                # Simpler: Model predicted home to win by X
                # Home covers our theoretical spread if actual >= predicted - 1.5 (hook)
                simulated_line = pred_margin - 1.5  # Market might be 1.5 pts tighter
                covered = actual_margin > simulated_line
                
                play = {
                    'date': r['date'],
                    'bet_on': r['home_team'],
                    'against': r['away_team'],
                    'is_home': True,
                    'predicted': pred_margin,
                    'actual': actual_margin,
                    'line': simulated_line,
                    'covered': covered,
                    'edge': edge,
                    'is_favorite': pred_margin > 0
                }
            else:
                # Model likes away team (pred_margin < 0 means away favored)
                simulated_line = -pred_margin - 1.5
                covered = -actual_margin > simulated_line  # Away margin
                
                play = {
                    'date': r['date'],
                    'bet_on': r['away_team'],
                    'against': r['home_team'],
                    'is_home': False,
                    'predicted': -pred_margin,  # Convert to positive
                    'actual': -actual_margin,
                    'line': simulated_line,
                    'covered': covered,
                    'edge': edge,
                    'is_favorite': True
                }
            
            plays.append(play)
            
            # Track results
            if covered:
                ats_results['all']['wins'] += 1
                if play['is_home']:
                    ats_results['home_plays']['wins'] += 1
                else:
                    ats_results['away_plays']['wins'] += 1
                
                if edge >= 4:
                    ats_results['big_edge']['wins'] += 1
                else:
                    ats_results['medium_edge']['wins'] += 1
                    
                if play['is_favorite']:
                    ats_results['favorites']['wins'] += 1
                else:
                    ats_results['underdogs']['wins'] += 1
            else:
                ats_results['all']['losses'] += 1
                if play['is_home']:
                    ats_results['home_plays']['losses'] += 1
                else:
                    ats_results['away_plays']['losses'] += 1
                    
                if edge >= 4:
                    ats_results['big_edge']['losses'] += 1
                else:
                    ats_results['medium_edge']['losses'] += 1
                    
                if play['is_favorite']:
                    ats_results['favorites']['losses'] += 1
                else:
                    ats_results['underdogs']['losses'] += 1
    
    return ats_results, plays


def calculate_roi(wins, losses, vig=-110):
    """
    Calculate ROI assuming standard -110 odds
    Win: returns $100 profit on $110 bet
    Loss: lose $110
    """
    if wins + losses == 0:
        return 0.0
    
    total_wagered = (wins + losses) * 110  # $110 per bet
    profit = wins * 100 - losses * 110
    roi = (profit / total_wagered) * 100
    return roi


def analyze_patterns(results):
    """
    Analyze where model over/underperforms
    """
    patterns = {
        'by_home_nrtg': {},  # Performance when home team is good/bad
        'by_mismatch': {},   # Close games vs blowouts (predicted)
        'by_actual_margin': {},  # How we did in close vs blowout actual games
        'monthly': {},
        'by_reliability': {}
    }
    
    for r in results:
        # By home team strength
        home_nrtg = r['home_ratings']['NRtg']
        if home_nrtg > 5:
            bucket = 'elite_home'
        elif home_nrtg > 0:
            bucket = 'good_home'
        elif home_nrtg > -5:
            bucket = 'mediocre_home'
        else:
            bucket = 'bad_home'
        
        if bucket not in patterns['by_home_nrtg']:
            patterns['by_home_nrtg'][bucket] = {'correct': 0, 'total': 0, 'mae': []}
        patterns['by_home_nrtg'][bucket]['total'] += 1
        if r['winner_correct']:
            patterns['by_home_nrtg'][bucket]['correct'] += 1
        patterns['by_home_nrtg'][bucket]['mae'].append(r['abs_error'])
        
        # By predicted mismatch
        pred_abs = abs(r['predicted_margin'])
        if pred_abs > 10:
            mismatch = 'big_mismatch'
        elif pred_abs > 5:
            mismatch = 'moderate'
        else:
            mismatch = 'close_game'
        
        if mismatch not in patterns['by_mismatch']:
            patterns['by_mismatch'][mismatch] = {'correct': 0, 'total': 0, 'mae': []}
        patterns['by_mismatch'][mismatch]['total'] += 1
        if r['winner_correct']:
            patterns['by_mismatch'][mismatch]['correct'] += 1
        patterns['by_mismatch'][mismatch]['mae'].append(r['abs_error'])
        
        # By actual margin
        actual_abs = abs(r['actual_margin'])
        if actual_abs <= 5:
            actual_bucket = 'nail_biter'
        elif actual_abs <= 10:
            actual_bucket = 'comfortable'
        else:
            actual_bucket = 'blowout'
        
        if actual_bucket not in patterns['by_actual_margin']:
            patterns['by_actual_margin'][actual_bucket] = {'correct': 0, 'total': 0}
        patterns['by_actual_margin'][actual_bucket]['total'] += 1
        if r['winner_correct']:
            patterns['by_actual_margin'][actual_bucket]['correct'] += 1
        
        # By month
        try:
            date_parts = r['date'].split(',')
            if len(date_parts) >= 2:
                month = date_parts[0].split()[0][:3]  # Get first 3 letters of month
            else:
                month = 'Unknown'
        except:
            month = 'Unknown'
        
        if month not in patterns['monthly']:
            patterns['monthly'][month] = {'correct': 0, 'total': 0, 'mae': []}
        patterns['monthly'][month]['total'] += 1
        if r['winner_correct']:
            patterns['monthly'][month]['correct'] += 1
        patterns['monthly'][month]['mae'].append(r['abs_error'])
        
        # By reliability score
        rel = r['reliability']
        if rel >= 8:
            rel_bucket = 'high_reliability'
        elif rel >= 6:
            rel_bucket = 'medium_reliability'
        else:
            rel_bucket = 'low_reliability'
        
        if rel_bucket not in patterns['by_reliability']:
            patterns['by_reliability'][rel_bucket] = {'correct': 0, 'total': 0, 'mae': []}
        patterns['by_reliability'][rel_bucket]['total'] += 1
        if r['winner_correct']:
            patterns['by_reliability'][rel_bucket]['correct'] += 1
        patterns['by_reliability'][rel_bucket]['mae'].append(r['abs_error'])
    
    return patterns


def generate_report(results, ats_results, patterns):
    """
    Generate markdown report with findings
    """
    lines = []
    lines.append("# NBA Model Backtest Results - 2025-26 Season\n")
    lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}*\n")
    
    # Summary stats
    total_games = len(results)
    correct = sum(1 for r in results if r['winner_correct'])
    accuracy = correct / total_games * 100 if total_games > 0 else 0
    
    mae = np.mean([r['abs_error'] for r in results])
    rmse = np.sqrt(np.mean([r['spread_error']**2 for r in results]))
    avg_error = np.mean([r['spread_error'] for r in results])  # Bias check
    
    lines.append("## Summary Statistics\n")
    lines.append(f"- **Total Games Analyzed:** {total_games}")
    lines.append(f"- **Winner Prediction Accuracy:** {correct}/{total_games} ({accuracy:.1f}%)")
    lines.append(f"- **Mean Absolute Error (MAE):** {mae:.2f} points")
    lines.append(f"- **Root Mean Square Error (RMSE):** {rmse:.2f} points")
    lines.append(f"- **Average Error (Bias):** {avg_error:+.2f} points")
    if avg_error > 0.5:
        lines.append(f"  - ⚠️ Model tends to overrate home teams")
    elif avg_error < -0.5:
        lines.append(f"  - ⚠️ Model tends to underrate home teams")
    else:
        lines.append(f"  - ✅ Model bias is minimal")
    
    # ATS Performance
    lines.append("\n## Against The Spread (ATS) Performance\n")
    lines.append("*Simulated betting with 2+ point edge, assuming market 1.5 pts tighter than model*\n")
    
    all_w = ats_results['all']['wins']
    all_l = ats_results['all']['losses']
    all_total = all_w + all_l
    
    if all_total > 0:
        all_pct = all_w / all_total * 100
        all_roi = calculate_roi(all_w, all_l)
        
        lines.append(f"### Overall ATS Record: {all_w}-{all_l} ({all_pct:.1f}%)")
        lines.append(f"- **ROI at -110 odds:** {all_roi:+.2f}%")
        lines.append(f"- **Break-even requirement:** 52.4%")
        
        if all_pct > 52.4:
            lines.append(f"- ✅ **PROFITABLE** - Above break-even")
        else:
            lines.append(f"- ❌ **Unprofitable** - Below break-even")
        
        lines.append("\n### ATS Breakdown:\n")
        lines.append("| Category | W-L | Win% | ROI |")
        lines.append("|----------|-----|------|-----|")
        
        for cat, name in [('home_plays', 'Home Picks'), ('away_plays', 'Away Picks'),
                          ('big_edge', '4+ Point Edge'), ('medium_edge', '2-4 Point Edge'),
                          ('favorites', 'Backing Favorites'), ('underdogs', 'Backing Underdogs')]:
            w = ats_results[cat]['wins']
            l = ats_results[cat]['losses']
            t = w + l
            if t > 0:
                pct = w / t * 100
                roi = calculate_roi(w, l)
                lines.append(f"| {name} | {w}-{l} | {pct:.1f}% | {roi:+.1f}% |")
    
    # Pattern Analysis
    lines.append("\n## Pattern Analysis\n")
    
    lines.append("### By Home Team Strength:\n")
    lines.append("| Category | Games | Accuracy | MAE |")
    lines.append("|----------|-------|----------|-----|")
    for cat in ['elite_home', 'good_home', 'mediocre_home', 'bad_home']:
        if cat in patterns['by_home_nrtg']:
            data = patterns['by_home_nrtg'][cat]
            acc = data['correct'] / data['total'] * 100
            mae = np.mean(data['mae'])
            lines.append(f"| {cat.replace('_', ' ').title()} | {data['total']} | {acc:.1f}% | {mae:.1f} |")
    
    lines.append("\n### By Game Type (Predicted):\n")
    lines.append("| Category | Games | Accuracy | MAE |")
    lines.append("|----------|-------|----------|-----|")
    for cat in ['big_mismatch', 'moderate', 'close_game']:
        if cat in patterns['by_mismatch']:
            data = patterns['by_mismatch'][cat]
            acc = data['correct'] / data['total'] * 100
            mae = np.mean(data['mae'])
            lines.append(f"| {cat.replace('_', ' ').title()} | {data['total']} | {acc:.1f}% | {mae:.1f} |")
    
    lines.append("\n### By Actual Game Result:\n")
    lines.append("| Category | Games | Accuracy |")
    lines.append("|----------|-------|----------|")
    for cat in ['blowout', 'comfortable', 'nail_biter']:
        if cat in patterns['by_actual_margin']:
            data = patterns['by_actual_margin'][cat]
            acc = data['correct'] / data['total'] * 100
            lines.append(f"| {cat.replace('_', ' ').title()} | {data['total']} | {acc:.1f}% |")
    
    lines.append("\n### By Month:\n")
    lines.append("| Month | Games | Accuracy | MAE |")
    lines.append("|-------|-------|----------|-----|")
    for month in ['Oct', 'Nov', 'Dec', 'Jan', 'Feb']:
        if month in patterns['monthly']:
            data = patterns['monthly'][month]
            acc = data['correct'] / data['total'] * 100
            mae = np.mean(data['mae']) if data['mae'] else 0
            lines.append(f"| {month} | {data['total']} | {acc:.1f}% | {mae:.1f} |")
    
    lines.append("\n### By Reliability Score:\n")
    lines.append("| Category | Games | Accuracy | MAE |")
    lines.append("|----------|-------|----------|-----|")
    for cat in ['high_reliability', 'medium_reliability', 'low_reliability']:
        if cat in patterns['by_reliability']:
            data = patterns['by_reliability'][cat]
            acc = data['correct'] / data['total'] * 100
            mae = np.mean(data['mae'])
            lines.append(f"| {cat.replace('_', ' ').title()} | {data['total']} | {acc:.1f}% | {mae:.1f} |")
    
    # Model Improvement Suggestions
    lines.append("\n## Model Improvement Suggestions\n")
    
    # Analyze bias
    if avg_error > 0.5:
        lines.append("### 1. Reduce Home Court Advantage")
        lines.append(f"- Current HCA: 3.2 points")
        lines.append(f"- Model overestimates home margins by {avg_error:.1f} points on average")
        lines.append(f"- **Recommendation:** Reduce HCA to ~{3.2 - avg_error/2:.1f} points")
    elif avg_error < -0.5:
        lines.append("### 1. Increase Home Court Advantage")
        lines.append(f"- Current HCA: 3.2 points")
        lines.append(f"- Model underestimates home margins by {abs(avg_error):.1f} points on average")
        lines.append(f"- **Recommendation:** Increase HCA to ~{3.2 - avg_error/2:.1f} points")
    
    # Check close games
    if 'close_game' in patterns['by_mismatch']:
        close_acc = patterns['by_mismatch']['close_game']['correct'] / patterns['by_mismatch']['close_game']['total'] * 100
        if close_acc < 55:
            lines.append("\n### 2. Improve Close Game Prediction")
            lines.append(f"- Current accuracy in close games (predicted <5 pts): {close_acc:.1f}%")
            lines.append("- **Recommendations:**")
            lines.append("  - Add recent form/momentum weighting (last 5-10 games)")
            lines.append("  - Factor in rest days more heavily")
            lines.append("  - Consider clutch/late-game performance metrics")
    
    # Check elite teams
    if 'elite_home' in patterns['by_home_nrtg']:
        elite_data = patterns['by_home_nrtg']['elite_home']
        elite_mae = np.mean(elite_data['mae'])
        if elite_mae > mae * 1.2:  # 20% worse than average
            lines.append("\n### 3. Better Model Elite Teams")
            lines.append(f"- MAE for elite home teams: {elite_mae:.1f} (vs overall {mae:.1f})")
            lines.append("- **Recommendations:**")
            lines.append("  - Cap maximum predicted margins (regression to mean)")
            lines.append("  - Account for opponent adjustments in blowouts")
    
    # Check bad teams
    if 'bad_home' in patterns['by_home_nrtg']:
        bad_data = patterns['by_home_nrtg']['bad_home']
        bad_acc = bad_data['correct'] / bad_data['total'] * 100
        if bad_acc < accuracy - 5:
            lines.append("\n### 4. Better Model Bad Teams")
            lines.append(f"- Accuracy for bad home teams: {bad_acc:.1f}% (vs overall {accuracy:.1f}%)")
            lines.append("- **Recommendations:**")
            lines.append("  - Bad teams have higher variance - factor into reliability")
            lines.append("  - Consider tanking/motivation factors late season")
    
    # ATS specific
    if all_total > 0:
        if ats_results['big_edge']['wins'] + ats_results['big_edge']['losses'] > 0:
            big_w = ats_results['big_edge']['wins']
            big_l = ats_results['big_edge']['losses']
            big_pct = big_w / (big_w + big_l) * 100
            med_w = ats_results['medium_edge']['wins']
            med_l = ats_results['medium_edge']['losses']
            med_pct = med_w / (med_w + med_l) * 100 if (med_w + med_l) > 0 else 0
            
            if big_pct < med_pct:
                lines.append("\n### 5. Re-evaluate Large Edge Plays")
                lines.append(f"- 4+ point edge: {big_pct:.1f}% ({big_w}-{big_l})")
                lines.append(f"- 2-4 point edge: {med_pct:.1f}% ({med_w}-{med_l})")
                lines.append("- **Recommendation:** Larger edges aren't performing better, suggesting:")
                lines.append("  - Market is efficient at pricing large mismatches")
                lines.append("  - Consider reducing confidence on extreme predictions")
    
    # General recommendations
    lines.append("\n### General Recommendations\n")
    lines.append("1. **Add Historical Market Lines** - Compare against actual Vegas lines for true edge detection")
    lines.append("2. **Include Player-Level Data** - Track injuries, rest, minutes trends")
    lines.append("3. **Incorporate Recent Form** - Weight last 10 games more heavily")
    lines.append("4. **Tempo Matching** - Factor in pace mismatches more explicitly")
    lines.append("5. **Home/Road Splits** - Some teams perform very differently home vs away")
    
    return '\n'.join(lines)


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    
    print("=" * 60)
    print("NBA Model Backtest - 2025-26 Season")
    print("=" * 60)
    
    # Check for cached games
    cache_file = f"{DATA_DIR}/season_games_2026.json"
    if os.path.exists(cache_file):
        print(f"\nLoading cached games from {cache_file}")
        with open(cache_file, 'r') as f:
            games = json.load(f)
        print(f"Loaded {len(games)} games from cache")
        
        # Check if cache is stale (more than 1 day old)
        cache_age = time.time() - os.path.getmtime(cache_file)
        if cache_age > 86400:  # 24 hours
            print("Cache is stale, refreshing...")
            games = fetch_season_schedule("2026")
    else:
        print("\nFetching season schedule from Basketball Reference...")
        games = fetch_season_schedule("2026")
    
    if not games:
        print("ERROR: No games found!")
        return
    
    # Initialize model
    print("\nInitializing model...")
    model = NBAModel()
    if not model.load_data():
        print("ERROR: Could not load team ratings")
        return
    
    # Run backtest
    print(f"\nRunning backtest on {len(games)} games...")
    results = run_backtest(games, model)
    
    # Calculate ATS performance
    print("Calculating ATS performance...")
    ats_results, plays = calculate_ats_performance(results, edge_threshold=2.0)
    
    # Analyze patterns
    print("Analyzing patterns...")
    patterns = analyze_patterns(results)
    
    # Generate report
    print("Generating report...")
    report = generate_report(results, ats_results, patterns)
    
    # Save report
    report_path = os.path.dirname(os.path.abspath(__file__)) + "/backtest_results.md"
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"\nReport saved to {report_path}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("BACKTEST COMPLETE")
    print("=" * 60)
    
    total = len(results)
    correct = sum(1 for r in results if r['winner_correct'])
    print(f"Winner Accuracy: {correct}/{total} ({correct/total*100:.1f}%)")
    print(f"MAE: {np.mean([r['abs_error'] for r in results]):.2f} points")
    
    all_w = ats_results['all']['wins']
    all_l = ats_results['all']['losses']
    if all_w + all_l > 0:
        print(f"ATS Record (2+ edge): {all_w}-{all_l} ({all_w/(all_w+all_l)*100:.1f}%)")
        print(f"ROI: {calculate_roi(all_w, all_l):+.2f}%")
    
    return results, ats_results, patterns


if __name__ == "__main__":
    main()
