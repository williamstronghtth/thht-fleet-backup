#!/usr/bin/env python3
"""
Spring Training Stats for Eno Sarris
=====================================
Pulls Spring Training batting and pitching stats from Statcast.

Usage:
    python3 spring-training-stats.py batting
    python3 spring-training-stats.py pitching  
    python3 spring-training-stats.py both
    python3 spring-training-stats.py both 21   # Last 21 days
"""

import sys
from pybaseball import statcast, playerid_reverse_lookup
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

pd.set_option('display.max_rows', 100)
pd.set_option('display.width', 140)

def get_batter_names(batter_ids):
    """Look up batter names from MLB IDs."""
    try:
        # Lookup in batches to avoid timeouts
        all_names = {}
        ids_list = list(batter_ids)
        
        for i in range(0, len(ids_list), 100):
            batch = ids_list[i:i+100]
            try:
                lookup = playerid_reverse_lookup(batch, key_type='mlbam')
                for _, row in lookup.iterrows():
                    name = f"{row['name_first']} {row['name_last']}"
                    all_names[row['key_mlbam']] = name
            except:
                pass
                
        return all_names
    except Exception as e:
        print(f"Name lookup error: {e}")
        return {}

def get_spring_training_batting(days_back=14):
    """Get Spring Training batting stats from Statcast data."""
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    
    print(f"📊 Fetching Statcast data ({start_date} to {end_date})...")
    
    try:
        df = statcast(start_date, end_date)
        if df is None or len(df) == 0:
            print("No data found for this date range")
            return None
        
        print(f"   Got {len(df):,} pitch events")
        print(f"   Looking up batter names...")
        
        # Get batter names
        batter_ids = df['batter'].dropna().unique()
        name_map = get_batter_names(batter_ids)
        print(f"   Found names for {len(name_map)} batters")
        
        # Aggregate batting stats by batter ID
        results = []
        for batter_id, group in df.groupby('batter'):
            events = group['events'].dropna()
            
            # Count actual plate appearances (unique at-bats with outcomes)
            pa = len(events)
            if pa < 5:  # Skip players with very few PA
                continue
            
            hits = events.isin(['single', 'double', 'triple', 'home_run']).sum()
            ab = events.isin(['single', 'double', 'triple', 'home_run', 
                            'field_out', 'strikeout', 'double_play',
                            'grounded_into_double_play', 'force_out',
                            'fielders_choice', 'fielders_choice_out']).sum()
            hr = (events == 'home_run').sum()
            doubles = (events == 'double').sum()
            triples = (events == 'triple').sum()
            bb = (events == 'walk').sum()
            k = (events == 'strikeout').sum()
            hbp = (events == 'hit_by_pitch').sum()
            
            # Exit velo for batted balls
            batted = group[group['launch_speed'].notna()]
            ev = batted['launch_speed'].mean() if len(batted) > 0 else np.nan
            la = batted['launch_angle'].mean() if len(batted) > 0 else np.nan
            max_ev = batted['launch_speed'].max() if len(batted) > 0 else np.nan
            
            avg = hits / ab if ab > 0 else 0
            obp = (hits + bb + hbp) / (ab + bb + hbp) if (ab + bb + hbp) > 0 else 0
            slg = (hits + doubles + 2*triples + 3*hr) / ab if ab > 0 else 0
            
            name = name_map.get(int(batter_id), f"ID:{int(batter_id)}")
            
            results.append({
                'Name': name,
                'PA': int(pa),
                'AB': int(ab),
                'H': int(hits),
                '2B': int(doubles),
                '3B': int(triples),
                'HR': int(hr),
                'BB': int(bb),
                'K': int(k),
                'AVG': round(avg, 3),
                'OBP': round(obp, 3),
                'SLG': round(slg, 3),
                'EV': round(ev, 1) if pd.notna(ev) else np.nan,
                'LA': round(la, 1) if pd.notna(la) else np.nan,
                'maxEV': round(max_ev, 1) if pd.notna(max_ev) else np.nan,
            })
        
        batting = pd.DataFrame(results)
        batting = batting.sort_values('PA', ascending=False)
        
        return batting
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_spring_training_pitching(days_back=14):
    """Get Spring Training pitching stats from Statcast data."""
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    
    print(f"📊 Fetching Statcast pitching data ({start_date} to {end_date})...")
    
    try:
        df = statcast(start_date, end_date)
        if df is None or len(df) == 0:
            print("No data found for this date range")
            return None
        
        print(f"   Got {len(df):,} pitch events")
        
        # player_name in statcast IS the pitcher name
        results = []
        for (pitcher_id, name), group in df.groupby(['pitcher', 'player_name']):
            events = group['events'].dropna()
            bf = len(events)  # Batters faced
            if bf < 10:
                continue
            
            k = (events == 'strikeout').sum()
            bb = (events == 'walk').sum()
            hits = events.isin(['single', 'double', 'triple', 'home_run']).sum()
            hr = (events == 'home_run').sum()
            
            # Velocity and spin
            velo = group['release_speed'].mean()
            spin = group['release_spin_rate'].mean()
            
            # Whiff rate
            desc = group['description']
            swings = desc.isin(['swinging_strike', 'swinging_strike_blocked', 'foul', 
                               'foul_tip', 'hit_into_play']).sum()
            whiffs = desc.isin(['swinging_strike', 'swinging_strike_blocked']).sum()
            whiff_pct = (whiffs / swings * 100) if swings > 0 else 0
            
            # Called strike rate
            called = (desc == 'called_strike').sum()
            total_pitches = len(group)
            csw = ((whiffs + called) / total_pitches * 100) if total_pitches > 0 else 0
            
            k_pct = (k / bf * 100) if bf > 0 else 0
            bb_pct = (bb / bf * 100) if bf > 0 else 0
            
            results.append({
                'Name': str(name),
                'BF': int(bf),
                'K': int(k),
                'BB': int(bb),
                'H': int(hits),
                'HR': int(hr),
                'K%': round(k_pct, 1),
                'BB%': round(bb_pct, 1),
                'Whiff%': round(whiff_pct, 1),
                'CSW%': round(csw, 1),
                'Velo': round(velo, 1) if pd.notna(velo) else np.nan,
                'Spin': int(spin) if pd.notna(spin) else 0,
            })
        
        pitching = pd.DataFrame(results)
        pitching = pitching.sort_values('BF', ascending=False)
        
        return pitching
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def display_batting(df, top_n=25):
    """Display batting leaderboard."""
    if df is None or len(df) == 0:
        print("No batting data available")
        return
    
    # Filter to known players (not ID: prefix)
    known = df[~df['Name'].str.startswith('ID:')]
    unknown_count = len(df) - len(known)
        
    print("\n" + "="*90)
    print("⚾ SPRING TRAINING BATTING LEADERS (Known MLB Players)")
    print("="*90)
    
    if unknown_count > 0:
        print(f"   ({unknown_count} minor leaguers/prospects not shown)")
    
    # Volume leaders
    print(f"\n📊 MOST PLATE APPEARANCES:")
    cols = ['Name', 'PA', 'AB', 'H', 'HR', 'BB', 'K', 'AVG', 'OBP', 'SLG']
    print(known[cols].head(top_n).to_string(index=False))
    
    # Exit velo leaders
    print("\n🚀 BEST EXIT VELOCITY (min 10 PA):")
    ev = known[(known['PA'] >= 10) & (known['EV'].notna())].sort_values('EV', ascending=False)
    cols = ['Name', 'PA', 'EV', 'maxEV', 'LA', 'HR', 'AVG']
    print(ev[cols].head(15).to_string(index=False))
    
    # HR leaders
    if known['HR'].max() > 0:
        print("\n💣 HOME RUN LEADERS:")
        hr = known[known['HR'] > 0].sort_values('HR', ascending=False)
        cols = ['Name', 'PA', 'HR', 'H', 'EV', 'AVG']
        print(hr[cols].head(15).to_string(index=False))

def display_pitching(df, top_n=25):
    """Display pitching leaderboard."""
    if df is None or len(df) == 0:
        print("No pitching data available")
        return
        
    print("\n" + "="*90)
    print("⚾ SPRING TRAINING PITCHING LEADERS")
    print("="*90)
    
    # Volume leaders
    print(f"\n📊 MOST BATTERS FACED:")
    cols = ['Name', 'BF', 'K', 'BB', 'H', 'HR', 'K%', 'BB%', 'Whiff%']
    print(df[cols].head(top_n).to_string(index=False))
    
    # Strikeout leaders
    print("\n🔥 STRIKEOUT RATE LEADERS (min 15 BF):")
    k = df[df['BF'] >= 15].sort_values('K%', ascending=False)
    cols = ['Name', 'BF', 'K', 'K%', 'Whiff%', 'CSW%', 'Velo']
    print(k[cols].head(15).to_string(index=False))
    
    # Velo leaders
    print("\n💨 VELOCITY LEADERS (min 15 BF):")
    v = df[(df['BF'] >= 15) & (df['Velo'].notna())].sort_values('Velo', ascending=False)
    cols = ['Name', 'BF', 'Velo', 'Spin', 'K%', 'Whiff%']
    print(v[cols].head(15).to_string(index=False))
    
    # Best Whiff%
    print("\n😵 BEST WHIFF RATE (min 15 BF):")
    w = df[df['BF'] >= 15].sort_values('Whiff%', ascending=False)
    cols = ['Name', 'BF', 'Whiff%', 'K%', 'Velo', 'BB%']
    print(w[cols].head(15).to_string(index=False))

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'both'
    days = int(sys.argv[2]) if len(sys.argv) > 2 else 14
    
    print("="*90)
    print(f"🌴 SPRING TRAINING STATS (Last {days} days)")
    print(f"   Data: Baseball Savant (Statcast)")
    print(f"   Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*90)
    print()
    
    if mode in ['batting', 'bat', 'b', 'both']:
        batting = get_spring_training_batting(days)
        display_batting(batting)
        
    if mode in ['pitching', 'pitch', 'p', 'both']:
        pitching = get_spring_training_pitching(days)
        display_pitching(pitching)
    
    print("\n" + "="*90)
    print("💡 Usage:")
    print("   python3 spring-training-stats.py batting      # Batting only")
    print("   python3 spring-training-stats.py pitching     # Pitching only")
    print("   python3 spring-training-stats.py both 21      # Both, last 21 days")
    print()
    print("📝 Notes:")
    print("   • Minor leaguers without MLB IDs shown as 'ID:######'")
    print("   • EV = avg exit velocity, maxEV = hardest hit ball")
    print("   • Whiff% = swinging strikes / swings")
    print("   • CSW% = called strikes + whiffs / total pitches")
    print("="*90)

if __name__ == '__main__':
    main()
