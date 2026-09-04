#!/usr/bin/env python3
"""
Backtest a single day: sim all games, find picks, log to Google Sheet.

Usage:
    python backtest_day.py 2026-03-14
    python backtest_day.py 2026-03-14 --dry-run  (don't write to sheet)
"""

import sys
import argparse
import numpy as np
import pandas as pd
import duckdb
import gspread
from google.oauth2.service_account import Credentials

sys.path.insert(0, '.')
from models.simulation.predictor import SimulationPredictor

DB_PATH = 'data/nbadb/nba.duckdb'
CREDS_PATH = 'google-service-account.json'
SHEET_NAME = 'Paper NBA'

SU_RATES = {'Small (0-3)': '50.5%', 'Medium (3-6)': '41.8%', 'Big (6-10)': '38.3%', 'Huge (10+)': '25%'}
ABBR_MAP = {'ny':'NYK','no':'NOP','sa':'SAS','wsh':'WAS','utah':'UTA','bkn':'BKN',
            'okc':'OKC','min':'MIN','bos':'BOS','cle':'CLE','hou':'HOU','den':'DEN',
            'gsw':'GSW','mil':'MIL','lal':'LAL','lac':'LAC','phx':'PHX','mem':'MEM',
            'dal':'DAL','mia':'MIA','ind':'IND','atl':'ATL','phi':'PHI','sac':'SAC',
            'orl':'ORL','chi':'CHI','det':'DET','tor':'TOR','cha':'CHA','por':'POR'}


def spread_to_ml(spread):
    if spread <= 0.5: return 105
    elif spread <= 1.5: return 115
    elif spread <= 2.5: return 130
    elif spread <= 3.5: return 145
    elif spread <= 4.5: return 165
    elif spread <= 5.5: return 190
    elif spread <= 6.5: return 220
    elif spread <= 7.5: return 260
    elif spread <= 8.5: return 300
    elif spread <= 9.5: return 350
    elif spread <= 11: return 425
    elif spread <= 13: return 550
    else: return 700


def get_sheet():
    scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_file(CREDS_PATH, scopes=scopes)
    gc = gspread.authorize(creds)
    return gc.open(SHEET_NAME).sheet1


def get_last_bankrolls(ws):
    """Read the last row's bankroll values to continue from."""
    all_data = ws.get_all_values()
    if len(all_data) <= 1:
        return 1000.0, 1000.0, 1000.0
    
    # Find the last row with actual bankroll data (not TBD)
    for row in reversed(all_data[1:]):
        try:
            flat = float(row[13].replace('$', '').replace(',', ''))
            two = float(row[14].replace('$', '').replace(',', ''))
            five = float(row[15].replace('$', '').replace(',', ''))
            # Only use if this row has actual results (not TBD)
            if row[11] != 'TBD':
                return flat, two, five
        except (ValueError, IndexError):
            continue
    return 1000.0, 1000.0, 1000.0


def backtest_date(date_str, dry_run=False):
    game_date = pd.Timestamp(date_str)
    
    con = duckdb.connect(DB_PATH, read_only=True)
    games = con.execute("""
        SELECT game_id, game_date, team_id_home, team_id_away,
               team_abbreviation_home as home, team_abbreviation_away as away,
               pts_home, pts_away
        FROM game WHERE season_id = '22025' AND game_date = ?
        AND pts_home IS NOT NULL
        ORDER BY game_id
    """, [date_str]).fetchdf()
    
    vegas = con.execute("""
        SELECT away, home, whos_favored, spread FROM betting_lines
        WHERE season = 2026 AND date = ? AND spread IS NOT NULL
    """, [date_str]).fetchdf()
    con.close()
    
    if games.empty:
        print(f'No games on {date_str}')
        return []
    
    vegas['home_u'] = vegas['home'].map(ABBR_MAP)
    vegas['away_u'] = vegas['away'].map(ABBR_MAP)
    vegas['veg_home'] = np.where(vegas['whos_favored']=='home', vegas['spread'], -vegas['spread'])
    
    print(f'{date_str}: {len(games)} games, {len(vegas)} with lines')
    
    pred = SimulationPredictor(DB_PATH)
    picks = []
    
    for _, g in games.iterrows():
        vrow = vegas[(vegas['home_u'] == g['home']) & (vegas['away_u'] == g['away'])]
        if vrow.empty:
            continue
        veg = float(vrow.iloc[0]['veg_home'])
        
        inactive = pred._get_inactive_players(g['game_id'])
        r = pred.predict(str(g['team_id_home']), str(g['team_id_away']),
                          game_date, '22025', inactive_player_ids=inactive,
                          n_sims=100, seed=hash(g['away']+g['home']) % 9999)
        us = r.mean_spread
        actual_spread = g['pts_home'] - g['pts_away']
        actual_winner = g['home'] if actual_spread > 0 else g['away']
        score_str = f'{g["away"]} @ {g["home"]} [{int(g["pts_away"])}-{int(g["pts_home"])}]'
        
        vegas_fav = g['home'] if veg > 0 else g['away']
        model_fav = g['home'] if us > 0 else g['away']
        vegas_dog = g['away'] if veg > 0 else g['home']
        dog_spread = abs(veg)
        is_flip = vegas_fav != model_fav
        ats_edge = abs(veg) - abs(us)
        swing = abs(us - veg)
        pick_win_pct = r.home_win_pct if model_fav == g['home'] else (1 - r.home_win_pct)
        
        ml = spread_to_ml(dog_spread)
        if dog_spread <= 3: cat = 'Small (0-3)'
        elif dog_spread <= 6: cat = 'Medium (3-6)'
        elif dog_spread <= 10: cat = 'Big (6-10)'
        else: cat = 'Huge (10+)'
        
        if is_flip:
            conf = '🔥 High' if pick_win_pct > 0.55 or swing > 8 else '⚡ Medium'
            su_rate = SU_RATES.get(cat, '?')
            
            ml_won = actual_winner == model_fav
            dog_covered = (actual_spread < veg) if veg > 0 else (actual_spread > veg)
            
            picks.append(dict(
                date=date_str, game=score_str,
                vegas_spread=f'{vegas_fav} -{dog_spread}', model_spread=f'{model_fav} -{abs(us):.1f}',
                pick=f'{model_fav} ML', pick_type='ML Flip', dog_cat=cat, ml_str=f'+{ml}', ml_val=ml,
                confidence=conf, actual_winner=actual_winner, actual_spread=int(actual_spread),
                pick_won=ml_won, ats_cover=None,
                notes=f"Model: {model_fav} wins {pick_win_pct:.0%}. Vegas: {vegas_fav}. {swing:.1f}pt swing. {su_rate} SU rate."))
            
            picks.append(dict(
                date=date_str, game=score_str,
                vegas_spread=f'{vegas_fav} -{dog_spread}', model_spread=f'{model_fav} -{abs(us):.1f}',
                pick=f'{vegas_dog} +{dog_spread}', pick_type='ATS Flip', dog_cat=cat, ml_str='-110', ml_val=-110,
                confidence=conf, actual_winner=actual_winner, actual_spread=int(actual_spread),
                pick_won=dog_covered, ats_cover=dog_covered,
                notes=f"Model: {model_fav} -{abs(us):.1f} vs Vegas {vegas_fav} -{dog_spread}. Flips cover 55.8% ATS."))
        
        elif ats_edge >= 5:
            conf = '⚡ Medium' if ats_edge >= 8 else '📊 Low'
            dog_covered = (actual_spread < veg) if veg > 0 else (actual_spread > veg)
            
            picks.append(dict(
                date=date_str, game=score_str,
                vegas_spread=f'{vegas_fav} -{dog_spread}', model_spread=f'{vegas_fav} -{abs(us):.1f}',
                pick=f'{vegas_dog} +{dog_spread}', pick_type='ATS Value', dog_cat=cat, ml_str='-110', ml_val=-110,
                confidence=conf, actual_winner=actual_winner, actual_spread=int(actual_spread),
                pick_won=dog_covered, ats_cover=dog_covered,
                notes=f"Model: {vegas_fav} -{abs(us):.1f} vs Vegas -{dog_spread}. {ats_edge:.1f}pts cushion."))
        
        pred.clear_cache()
    
    if not picks:
        print(f'  No picks for {date_str}')
        return picks
    
    # Print summary
    wins = sum(1 for p in picks if p['pick_won'])
    print(f'  {len(picks)} picks: {wins}W-{len(picks)-wins}L')
    for p in picks:
        emoji = '✅' if p['pick_won'] else '❌'
        print(f'    {emoji} {p["pick"]} ({p["pick_type"]}) {p["confidence"]}')
    
    if dry_run:
        print('  (dry run — not writing to sheet)')
        return picks
    
    # Write to sheet — APPEND ONLY (never clear existing data)
    ws = get_sheet()
    existing = ws.get_all_values()
    next_row = len(existing) + 1
    
    rows = []
    for p in picks:
        won = p['pick_won']
        ml_val = p['ml_val']
        
        # Calculate P/L for $50 flat bet
        if p['pick_type'] == 'ML Flip':
            pl_flat = (50 * ml_val / 100) if won else -50
        else:
            pl_flat = (50 * 100 / 110) if won else -50
        
        rows.append([
            p['date'], p['game'], p['vegas_spread'], p['model_spread'], p['pick'],
            p['pick_type'], p['dog_cat'], p['ml_str'], p['confidence'],
            p['actual_winner'], str(p['actual_spread']),
            'Y' if p['pick_won'] else 'N',
            'Y' if p.get('ats_cover') else ('N' if p.get('ats_cover') is not None else 'N/A'),
            round(pl_flat, 2),  # P/L flat — plain number, no + prefix
            '',  # P/L 2% — formula will handle
            '',  # P/L 5% — formula will handle
            '',  # Bankroll flat — formula will handle
            '',  # Bankroll 2% — formula will handle
            '',  # Bankroll 5% — formula will handle
            p['notes'],
        ])
    
    # Append rows
    ws.update(values=rows, range_name=f'A{next_row}:T{next_row + len(rows) - 1}')
    
    # Add formulas for the new rows
    import time
    formulas_o, formulas_p, formulas_q, formulas_r, formulas_s = [], [], [], [], []
    for i, _ in enumerate(rows):
        r = next_row + i
        prev = r - 1
        
        if r == 2:  # first data row
            b2, b5 = '1000', '1000'
            formulas_q.append([f'=1000+IF(ISNUMBER(N{r}),N{r},0)'])
            formulas_r.append([f'=1000+IF(ISNUMBER(O{r}),O{r},0)'])
            formulas_s.append([f'=1000+IF(ISNUMBER(P{r}),P{r},0)'])
        else:
            b2, b5 = f'R{prev}', f'S{prev}'
            formulas_q.append([f'=Q{prev}+IF(ISNUMBER(N{r}),N{r},0)'])
            formulas_r.append([f'=R{prev}+IF(ISNUMBER(O{r}),O{r},0)'])
            formulas_s.append([f'=S{prev}+IF(ISNUMBER(P{r}),P{r},0)'])
        
        formulas_o.append([f'=IF(L{r}="TBD","TBD",IF(L{r}="Y",IF(ISNUMBER(SEARCH("ML",F{r})),{b2}*0.02*VALUE(SUBSTITUTE(H{r},"+",""))/100,{b2}*0.02*100/110),-{b2}*0.02))'])
        formulas_p.append([f'=IF(L{r}="TBD","TBD",IF(L{r}="Y",IF(ISNUMBER(SEARCH("ML",F{r})),{b5}*0.05*VALUE(SUBSTITUTE(H{r},"+",""))/100,{b5}*0.05*100/110),-{b5}*0.05))'])
    
    end = next_row + len(rows) - 1
    ws.update(values=formulas_o, range_name=f'O{next_row}:O{end}', value_input_option='USER_ENTERED')
    time.sleep(2)
    ws.update(values=formulas_p, range_name=f'P{next_row}:P{end}', value_input_option='USER_ENTERED')
    time.sleep(2)
    ws.update(values=formulas_q, range_name=f'Q{next_row}:Q{end}', value_input_option='USER_ENTERED')
    time.sleep(2)
    ws.update(values=formulas_r, range_name=f'R{next_row}:R{end}', value_input_option='USER_ENTERED')
    time.sleep(2)
    ws.update(values=formulas_s, range_name=f'S{next_row}:S{end}', value_input_option='USER_ENTERED')
    
    print(f'  Appended {len(rows)} rows (rows {next_row}-{end})')
    return picks


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('date', help='Date to backtest (YYYY-MM-DD)')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    backtest_date(args.date, dry_run=args.dry_run)
