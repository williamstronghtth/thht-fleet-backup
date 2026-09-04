#!/usr/bin/env python3
"""
Scrape Vegas lines from scoresandodds.com for March 1-15 2026,
match with simulation predictions, categorize into edge tiers,
and calculate ATS records.
"""

import re
import csv
import time
import urllib.request
from datetime import datetime, timedelta

TEAM_MAP = {
    'Thunder': 'OKC', 'Timberwolves': 'MIN', 'Celtics': 'BOS', 'Cavaliers': 'CLE',
    'Rockets': 'HOU', 'Nuggets': 'DEN', 'Warriors': 'GSW', 'Knicks': 'NYK',
    'Bucks': 'MIL', 'Lakers': 'LAL', 'Clippers': 'LAC', 'Suns': 'PHX',
    'Grizzlies': 'MEM', 'Mavericks': 'DAL', 'Heat': 'MIA', 'Pacers': 'IND',
    'Hawks': 'ATL', '76ers': 'PHI', 'Kings': 'SAC', 'Spurs': 'SAS',
    'Magic': 'ORL', 'Nets': 'BKN', 'Bulls': 'CHI', 'Pistons': 'DET',
    'Raptors': 'TOR', 'Pelicans': 'NOP', 'Hornets': 'CHA', 'Wizards': 'WAS',
    'Trail Blazers': 'POR', 'Jazz': 'UTA',
}

def scrape_date(date_str):
    """Scrape Vegas closing lines for a date. Returns list of dicts."""
    url = f'https://www.scoresandodds.com/nba?date={date_str}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'})
    resp = urllib.request.urlopen(req, timeout=15)
    text = resp.read().decode('utf-8')
    
    games = []
    blocks = text.split('Last play:')
    
    for block in blocks[:-1]:
        try:
            # Find team names via links like /nba/teams/celtics
            team_links = re.findall(r'/nba/teams/([\w-]+)', block)
            if len(team_links) < 2:
                continue
            
            away_slug = team_links[0].replace('-', ' ').title().replace(' ', ' ')
            home_slug = team_links[1].replace('-', ' ').title().replace(' ', ' ')
            
            # Map slug to abbreviation
            slug_map = {
                'Thunder': 'OKC', 'Timberwolves': 'MIN', 'Celtics': 'BOS', 'Cavaliers': 'CLE',
                'Rockets': 'HOU', 'Nuggets': 'DEN', 'Warriors': 'GSW', 'Knicks': 'NYK',
                'Bucks': 'MIL', 'Lakers': 'LAL', 'Clippers': 'LAC', 'Suns': 'PHX',
                'Grizzlies': 'MEM', 'Mavericks': 'DAL', 'Heat': 'MIA', 'Pacers': 'IND',
                'Hawks': 'ATL', '76Ers': 'PHI', 'Kings': 'SAC', 'Spurs': 'SAS',
                'Magic': 'ORL', 'Nets': 'BKN', 'Bulls': 'CHI', 'Pistons': 'DET',
                'Raptors': 'TOR', 'Pelicans': 'NOP', 'Hornets': 'CHA', 'Wizards': 'WAS',
                'Trail Blazers': 'POR', 'Jazz': 'UTA',
            }
            
            away_name = away_slug.replace('-', ' ').title()
            home_name = home_slug.replace('-', ' ').title()
            
            # Handle "Trail Blazers" -> "Trail Blazers"
            if 'trail' in team_links[0]:
                away_name = 'Trail Blazers'
            if 'trail' in team_links[1]:
                home_name = 'Trail Blazers'
            if '76' in team_links[0]:
                away_name = '76Ers'
            if '76' in team_links[1]:
                home_name = '76Ers'
                
            away_abbr = slug_map.get(away_name, away_name[:3].upper())
            home_abbr = slug_map.get(home_name, home_name[:3].upper())
            
            # Find all spreads: pattern like "-8.5 -110" or "+8.5 -115"
            # The closing spread is the last one before the moneyline section
            # Look for the spread column entries
            spread_pattern = r'([+-]\d+\.?\d*)\s+-\d+'
            spreads = re.findall(spread_pattern, block)
            
            # The spread values alternate: away spread entries, then home spread entries
            # In the format, each team row has multiple spread values (opening, movements, closing)
            # The closing spread is typically the last one
            # For away team: positive = underdog, negative = favorite
            # For home team: opposite sign
            
            # Simpler: find all spread values and take the home team's closing line
            # The block has away team data first, then home team data
            # Each has spread values like "-2.5 -108" repeated for open/close
            
            if len(spreads) >= 2:
                # Last spread value should be the closing line for the home team
                # But actually, spreads alternate away/home across columns
                # Let's take the first negative value as the favorite's spread
                home_spread = float(spreads[-1])  # last spread is typically home closing
            else:
                home_spread = None
            
            games.append({
                'date': date_str,
                'home': home_abbr,
                'away': away_abbr,
                'vegas_home_spread': home_spread,
            })
        except Exception as e:
            continue
    
    return games

def load_sims(path):
    """Load simulation CSV."""
    games = []
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            games.append({
                'date': row['game_date'],
                'home': row['home'],
                'away': row['away'],
                'pred_spread': float(row['pred_spread']),
                'actual_spread': float(row['actual_spread']),
            })
    return games

def main():
    # Load sim results
    sims = load_sims('data/reports/march2026_sims.csv')
    print(f"Loaded {len(sims)} sim results")
    
    # Scrape Vegas lines
    print("Scraping Vegas lines from scoresandodds.com...")
    all_vegas = []
    for day in range(1, 16):
        date_str = f"2026-03-{day:02d}"
        try:
            games = scrape_date(date_str)
            all_vegas.extend(games)
            print(f"  {date_str}: {len(games)} games")
        except Exception as e:
            print(f"  {date_str}: ERROR - {e}")
        time.sleep(0.5)
    
    print(f"\nTotal Vegas lines scraped: {len(all_vegas)}")
    
    # Build lookup: (date, home) -> vegas_home_spread
    vegas_lookup = {}
    for g in all_vegas:
        key = (g['date'], g['home'])
        vegas_lookup[key] = g['vegas_home_spread']
    
    # Match and calculate edges
    results = []
    matched = 0
    unmatched = 0
    for sim in sims:
        key = (sim['date'], sim['home'])
        vegas_spread = vegas_lookup.get(key)
        if vegas_spread is None:
            unmatched += 1
            continue
        matched += 1
        
        # Edge = how much better we think home is vs Vegas
        # pred_spread > 0 means we think home wins by that much
        # vegas_spread < 0 means Vegas thinks home wins by that much (home favored)
        # So: edge = pred_spread - vegas_spread  (if both from home perspective)
        # But scoresandodds shows the favorite's spread as negative
        # We need to figure out the home team's spread from Vegas
        
        # Our pred_spread: positive = home favored
        # Vegas: the scraped value might be either team
        # For now, assume vegas_home_spread is from home perspective (negative = home favored)
        
        edge = sim['pred_spread'] - vegas_spread
        
        # ATS: did our predicted side cover?
        # If edge > 0: we'd bet home (we think home is better than Vegas)
        # If edge < 0: we'd bet away
        # ATS cover: home actual_spread > vegas_spread means home covered
        actual = sim['actual_spread']
        
        if edge > 0:
            # Bet home: home covers if actual_spread > vegas_spread (they won by more than the line)
            # Wait, spread convention: actual_spread = home_score - away_score
            # vegas_spread (from home perspective): negative means home needs to win by that much
            # Home covers if actual_spread + vegas_spread > 0? No...
            # If vegas_spread = -8.5 (home favored by 8.5), home covers if they win by more than 8.5
            # actual_spread > abs(vegas_spread) when favored
            # More simply: home covers if actual_spread > -vegas_spread... no
            # Standard: home_score - away_score + spread > 0 means the spread side covers
            # If we bet HOME at spread = vegas_spread: home covers if actual + vegas > 0
            # e.g., vegas=-8.5, actual=10 -> 10 + (-8.5) = 1.5 > 0 = covers
            # e.g., vegas=-8.5, actual=5 -> 5 + (-8.5) = -3.5 < 0 = doesn't cover
            covered = (actual + vegas_spread) > 0  # betting home
            bet_side = 'home'
        elif edge < 0:
            # Bet away: away covers if actual_spread + vegas_spread < 0
            covered = (actual + vegas_spread) < 0  # betting away
            bet_side = 'away'
        else:
            continue  # no edge, skip
        
        push = (actual + vegas_spread) == 0
        
        # Categorize edge tier by absolute edge
        abs_edge = abs(edge)
        if abs_edge < 1.5:
            tier = "Flip/Coin Toss (<1.5)"
        elif abs_edge < 3:
            tier = "Small Edge (1.5-3)"
        elif abs_edge < 5:
            tier = "Moderate Edge (3-5)"
        else:
            tier = "Big Edge (5+)"
        
        results.append({
            'date': sim['date'],
            'home': sim['home'],
            'away': sim['away'],
            'pred_spread': sim['pred_spread'],
            'vegas_spread': vegas_spread,
            'edge': round(edge, 1),
            'abs_edge': round(abs_edge, 1),
            'bet_side': bet_side,
            'actual_spread': actual,
            'covered': covered,
            'push': push,
            'tier': tier,
        })
    
    print(f"\nMatched: {matched}, Unmatched: {unmatched}")
    
    # Calculate ATS by tier
    tiers = {}
    for r in results:
        t = r['tier']
        if t not in tiers:
            tiers[t] = {'wins': 0, 'losses': 0, 'pushes': 0, 'games': []}
        if r['push']:
            tiers[t]['pushes'] += 1
        elif r['covered']:
            tiers[t]['wins'] += 1
        else:
            tiers[t]['losses'] += 1
        tiers[t]['games'].append(r)
    
    # Print results
    print("\n" + "="*60)
    print("EDGE TIER ANALYSIS: March 1-15, 2026")
    print("="*60)
    
    tier_order = ["Big Edge (5+)", "Moderate Edge (3-5)", "Small Edge (1.5-3)", "Flip/Coin Toss (<1.5)"]
    
    overall_w, overall_l, overall_p = 0, 0, 0
    for tier_name in tier_order:
        if tier_name not in tiers:
            continue
        t = tiers[tier_name]
        w, l, p = t['wins'], t['losses'], t['pushes']
        overall_w += w
        overall_l += l
        overall_p += p
        total = w + l + p
        pct = w / (w + l) * 100 if (w + l) > 0 else 0
        print(f"\n{tier_name}")
        print(f"  ATS Record: {w}-{l}-{p} ({pct:.1f}%)")
        print(f"  Games: {total}")
        # Show individual games
        for g in sorted(t['games'], key=lambda x: -abs(x['edge'])):
            side = g['bet_side'].upper()
            result = "✅" if g['covered'] else ("➖" if g['push'] else "❌")
            print(f"    {g['date']} {g['away']}@{g['home']} | Edge: {g['edge']:+.1f} | Bet: {side} | Vegas: {g['vegas_spread']} | Actual: {g['actual_spread']} | {result}")
    
    total_games = overall_w + overall_l + overall_p
    overall_pct = overall_w / (overall_w + overall_l) * 100 if (overall_w + overall_l) > 0 else 0
    print(f"\nOVERALL: {overall_w}-{overall_l}-{overall_p} ({overall_pct:.1f}%)")
    print(f"Total games analyzed: {total_games}")

if __name__ == '__main__':
    main()
