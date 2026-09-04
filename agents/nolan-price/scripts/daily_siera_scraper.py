#!/usr/bin/env python3
"""
Daily SIERA Scraper — Live 2026 Starting Pitcher Stats
Pulls current-season pitcher stats from FanGraphs via pybaseball.
Designed to run daily via openclaw cron (~2am ET / 7am UTC).

Output: model/production/live_pitcher_stats.json
"""

import json
import os
import sys
from datetime import datetime, timezone

# pybaseball import
try:
    from pybaseball import pitching_stats
except ImportError:
    print("ERROR: pybaseball not installed. Run: pip install pybaseball")
    sys.exit(1)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.dirname(SCRIPT_DIR)
OUTPUT_FILE = os.path.join(WORKSPACE, 'model', 'production', 'live_pitcher_stats.json')
PROFILES_FILE = os.path.join(WORKSPACE, 'model', 'production', 'starter_profiles_by_season.json')

SEASON = 2026
MIN_IP = 5  # Low threshold early season, captures openers/spot starters

TEAM_NORMALIZE = {
    'ARI': 'ARI', 'ATL': 'ATL', 'BAL': 'BAL', 'BOS': 'BOS',
    'CHC': 'CHC', 'CHW': 'CWS', 'CWS': 'CWS', 'CIN': 'CIN',
    'CLE': 'CLE', 'COL': 'COL', 'DET': 'DET', 'HOU': 'HOU',
    'KCR': 'KC', 'KC': 'KC', 'LAA': 'LAA', 'LAD': 'LAD',
    'MIA': 'MIA', 'MIL': 'MIL', 'MIN': 'MIN', 'NYM': 'NYM',
    'NYY': 'NYY', 'OAK': 'OAK', 'PHI': 'PHI', 'PIT': 'PIT',
    'SDP': 'SD', 'SD': 'SD', 'SFG': 'SF', 'SF': 'SF',
    'SEA': 'SEA', 'STL': 'STL', 'TBR': 'TB', 'TB': 'TB',
    'TEX': 'TEX', 'TOR': 'TOR', 'WSN': 'WSH', 'WSH': 'WSH',
    '- - -': 'MULTI',
}

# Common name aliases (FanGraphs vs MLB Stats API)
NAME_ALIASES = {
    "Yoshinobu Yamamoto": ["Yoshinobu Yamamoto"],
    "J.P. Feyereisen": ["JP Feyereisen", "J.P. Feyereisen"],
    "J.T. Brubaker": ["JT Brubaker", "J.T. Brubaker"],
    "A.J. Minter": ["AJ Minter", "A.J. Minter"],
    "C.J. Abrams": ["CJ Abrams", "C.J. Abrams"],
}


def build_alias_map():
    """Build reverse alias map: alternate_name -> canonical_name."""
    alias_map = {}
    # Load existing profile names as canonical
    if os.path.exists(PROFILES_FILE):
        with open(PROFILES_FILE) as f:
            profiles = json.load(f)
        for name in profiles:
            alias_map[name] = name
    
    for canonical, aliases in NAME_ALIASES.items():
        for alias in aliases:
            alias_map[alias] = canonical
    
    return alias_map


def scrape_live_stats():
    """Pull current-season pitcher stats from FanGraphs."""
    print(f"Pulling {SEASON} pitcher stats from FanGraphs...")
    
    try:
        df = pitching_stats(SEASON, SEASON, qual=MIN_IP)
    except Exception as e:
        print(f"ERROR pulling stats: {e}")
        print("FanGraphs may be down or season hasn't started yet.")
        return None
    
    if df is None or len(df) == 0:
        print("No data returned — season may not have started yet.")
        return None
    
    print(f"Got {len(df)} pitchers with {MIN_IP}+ IP")
    
    alias_map = build_alias_map()
    
    pitchers = {}
    starters = 0
    relievers = 0
    
    for _, row in df.iterrows():
        name = str(row.get('Name', ''))
        
        # Normalize name via alias map
        canonical_name = alias_map.get(name, name)
        
        team_raw = str(row.get('Team', ''))
        team = TEAM_NORMALIZE.get(team_raw, team_raw)
        
        gs = int(row.get('GS', 0)) if row.get('GS') else 0
        ip = float(row.get('IP', 0)) if row.get('IP') else 0
        
        entry = {
            'team': team,
            'ip': ip,
            'siera': safe_float(row.get('SIERA')),
            'fip': safe_float(row.get('FIP')),
            'xfip': safe_float(row.get('xFIP')),
            'k_pct': safe_float(row.get('K%')),
            'bb_pct': safe_float(row.get('BB%')),
            'gb_pct': safe_float(row.get('GB%')),
            'hr9': safe_float(row.get('HR/9')),
            'gs': gs,
            'era': safe_float(row.get('ERA')),
            'war': safe_float(row.get('WAR')),
            'g': int(row.get('G', 0)) if row.get('G') else 0,
        }
        
        pitchers[canonical_name] = entry
        
        if gs > 0:
            starters += 1
        else:
            relievers += 1
    
    print(f"Parsed: {starters} starters (GS>0), {relievers} relievers (GS=0)")
    
    return pitchers


def safe_float(val):
    """Safely convert to float, handling None/NaN."""
    if val is None:
        return None
    try:
        f = float(val)
        if f != f:  # NaN check
            return None
        return round(f, 3)
    except (ValueError, TypeError):
        return None


def main():
    now = datetime.now(timezone.utc)
    print(f"Daily SIERA Scraper — {now.strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 50)
    
    pitchers = scrape_live_stats()
    
    if pitchers is None:
        print("\nNo data to save. Exiting.")
        sys.exit(1)
    
    output = {
        'last_updated': now.isoformat(),
        'season': SEASON,
        'total_pitchers': len(pitchers),
        'starters': sum(1 for p in pitchers.values() if p['gs'] > 0),
        'pitchers': pitchers,
    }
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2)
    
    file_size = os.path.getsize(OUTPUT_FILE) / 1024
    print(f"\nSaved to {OUTPUT_FILE}")
    print(f"File size: {file_size:.0f}KB")
    print(f"Total pitchers: {len(pitchers)}")
    print(f"Starters: {output['starters']}")
    
    # Quick validation: top 5 by IP
    top_ip = sorted(pitchers.items(), key=lambda x: x[1]['ip'], reverse=True)[:5]
    print(f"\nTop 5 by IP:")
    for name, stats in top_ip:
        print(f"  {name} ({stats['team']}): {stats['ip']}IP, SIERA={stats['siera']}, FIP={stats['fip']}, {stats['gs']}GS")


if __name__ == '__main__':
    main()
