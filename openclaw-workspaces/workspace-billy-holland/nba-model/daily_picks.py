#!/usr/bin/env python3
"""
Daily NBA Picks Generator
Uses Hard Rock Bet lines for value calculation
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fetch_data import fetch_team_ratings, fetch_todays_games, DATA_DIR
from fetch_odds import load_lines, get_hardrock_line
from model import NBAModel
from player_impact import get_player_impact, calculate_injury_adjustment
from injury_check import check_tonight_injuries
from datetime import datetime
import json


def generate_daily_report(top_n=3, verbose=False):
    """
    Generate picks report for today's games using Hard Rock lines
    Returns top N value plays
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Fetch fresh data
    if verbose:
        print("Fetching team ratings...")
    ratings = fetch_team_ratings()
    
    if verbose:
        print("Fetching today's games...")
    games = fetch_todays_games()
    if not games:
        return []
    
    # Load Hard Rock lines from file (updated via fetch_odds.py)
    hr_data = load_lines()
    if verbose:
        print(f"Loaded {len(hr_data.get('games', []))} Hard Rock lines")
    
    # Initialize model
    model = NBAModel()
    model.load_data()
    
    # Process each game
    picks = []
    for game in games:
        home = game.get('home_team')
        away = game.get('away_team')
        
        if not home or not away:
            continue
        
        # Get Hard Rock line (falls back to ESPN if not found)
        hr_line = get_hardrock_line(home, away)
        if hr_line is None:
            # Parse ESPN spread as fallback
            spread_str = game.get('spread', '')
            if spread_str:
                try:
                    parts = spread_str.split()
                    for p in parts:
                        if p.lstrip('-+').replace('.','').isdigit():
                            if parts[0] == home:
                                hr_line = float(p) if p.startswith('-') else -float(p)
                            else:
                                hr_line = -float(p) if p.startswith('-') else float(p)
                            break
                except:
                    pass
        
        if hr_line is None:
            continue
        
        # Make prediction
        pred = model.predict_spread(home, away)
        model_spread = pred['predicted_spread']
        
        # Get injury adjustments
        injury_alerts = check_tonight_injuries([{'home': home, 'away': away}])
        injury_adj = 0.0
        injury_notes = []
        
        for alert in injury_alerts:
            for inj in alert.get('injuries', []):
                if inj['status'] == 'Out':
                    impact = get_player_impact(inj['player'])
                    if impact > 0:
                        # If home player out, subtract from home margin (makes it lower)
                        # If away player out, add to home margin (makes it higher)
                        if inj['team'] == home:
                            injury_adj -= impact
                        else:
                            injury_adj += impact
                        injury_notes.append(f"{inj['player']} OUT ({impact:+.1f})")
        
        # Apply injury adjustment to model spread
        adjusted_spread = model_spread + injury_adj
        
        # Calculate edge using ADJUSTED spread
        # adjusted_spread > 0 means home favored
        # hr_line < 0 means home favored  
        # Edge = how much better the line is vs model expectation
        edge = adjusted_spread - (-hr_line)
        
        if edge > 0:
            value_team = home
            value_line = hr_line
        else:
            value_team = away
            value_line = -hr_line
        
        abs_edge = abs(edge)
        
        # Confidence based on backtest findings
        # SWEET SPOT: 2-4 pt edges (best performing)
        # CAUTION: 4+ pt edges (historically wrong 64%!)
        if 2.0 <= abs_edge <= 4.0:
            confidence = 'SWEET ✓'  # Best range per backtest
            edge_quality = 'sweet_spot'
        elif abs_edge > 4.0:
            confidence = 'CAUTION ⚠️'  # Historically unreliable
            edge_quality = 'danger'
        else:
            confidence = 'MARGINAL'
            edge_quality = 'marginal'
        
        # ATS probability estimate (rough)
        ats_prob = min(50 + (abs_edge * 3), 78)
        
        picks.append({
            'matchup': f"{away} @ {home}",
            'home': home,
            'away': away,
            'model_spread': model_spread,
            'adjusted_spread': adjusted_spread,
            'injury_adj': injury_adj,
            'injury_notes': injury_notes,
            'hr_line': hr_line,
            'edge': abs_edge,
            'value_team': value_team,
            'value_line': value_line,
            'confidence': confidence,
            'edge_quality': edge_quality,
            'ats_prob': ats_prob,
            'reliability': pred['reliability']
        })
    
    # Sort by edge (best first)
    picks.sort(key=lambda x: x['edge'], reverse=True)
    
    # Save full report
    report_file = f"{DATA_DIR}/picks_{datetime.now().strftime('%Y%m%d')}.json"
    with open(report_file, 'w') as f:
        json.dump(picks, f, indent=2)
    
    return picks[:top_n]


def format_picks_mobile(picks):
    """Format picks for mobile/Telegram"""
    if not picks:
        return "No games found or no value plays identified."
    
    lines = [f"🏀 TOP {len(picks)} BETS (Hard Rock)"]
    lines.append("")
    
    for i, p in enumerate(picks, 1):
        sign = '+' if p['value_line'] > 0 else ''
        lines.append(f"{i}. **{p['value_team']} {sign}{p['value_line']}**")
        lines.append(f"   Edge: {p['edge']:.1f} pts | ~{p['ats_prob']:.0f}% ATS")
        
        # Show injury adjustments if any
        if p.get('injury_notes'):
            lines.append(f"   ⚠️ {', '.join(p['injury_notes'])}")
        lines.append(f"   Reliability: {p['reliability']}/10 | {p['confidence']}")
        lines.append("")
    
    return '\n'.join(lines)


def main():
    """CLI entry point"""
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--top', type=int, default=3, help='Number of top picks')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--json', action='store_true', help='Output JSON')
    args = parser.parse_args()
    
    picks = generate_daily_report(top_n=args.top, verbose=args.verbose)
    
    if args.json:
        print(json.dumps(picks, indent=2))
    else:
        print(format_picks_mobile(picks))


if __name__ == "__main__":
    main()
