"""
analysis/ats_backtest.py — Against The Spread Backtester
=========================================================

The moment of truth: does our model beat Vegas?

For each game where we have model predictions AND betting lines,
compares our predicted spread/total to the closing line and determines
whether we'd have been profitable betting the disagreements.

Key concepts:
- Walk-forward: only uses data available before each game
- Only bets when model disagrees with the line (no bet on agreement)
- Standard vig: -110 (bet $110 to win $100, i.e., need >52.4% to profit)
- Push = no action
- Spread convention: negative = home favored (both model and lines)

Uses the full-stack predictor (baseline + players + refs + coach).
"""

import os
import sys
import logging
from typing import Optional

import duckdb
import numpy as np
import pandas as pd

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.team.backtest import Backtester

logger = logging.getLogger(__name__)

# ── Team abbreviation mapping: betting_lines (lower) → game table (upper) ──
BETTING_TO_NBA = {
    'atl': 'ATL', 'bkn': 'BKN', 'bos': 'BOS', 'cha': 'CHA',
    'chi': 'CHI', 'cle': 'CLE', 'dal': 'DAL', 'den': 'DEN',
    'det': 'DET', 'gs':  'GSW', 'hou': 'HOU', 'ind': 'IND',
    'lac': 'LAC', 'lal': 'LAL', 'mem': 'MEM', 'mia': 'MIA',
    'mil': 'MIL', 'min': 'MIN', 'no':  'NOP', 'ny':  'NYK',
    'okc': 'OKC', 'orl': 'ORL', 'phi': 'PHI', 'phx': 'PHX',
    'por': 'POR', 'sa':  'SAS', 'sac': 'SAC', 'tor': 'TOR',
    'utah': 'UTA', 'wsh': 'WAS',
    # Historical variants
    'nj': 'NJN', 'sea': 'SEA', 'cha': 'CHA',
}

# betting_lines season (ending year) → game table season_id
# Season 2018 = 2017-18 season = season_id "22017"
def season_to_season_id(season_year: int) -> str:
    """Convert betting_lines season year to game table season_id."""
    return f"2{season_year - 1}"


def load_betting_lines(db_path: str, seasons: list[int],
                       regular_only: bool = True) -> pd.DataFrame:
    """Load betting lines for specified seasons."""
    con = duckdb.connect(db_path, read_only=True)
    placeholders = ','.join(['?' for _ in seasons])
    query = f"""
        SELECT season, date, away, home, whos_favored, spread, total,
               moneyline_away, moneyline_home, score_away, score_home,
               regular, playoffs
        FROM betting_lines
        WHERE season IN ({placeholders})
          AND spread IS NOT NULL
    """
    if regular_only:
        query += " AND regular = true"
    query += " ORDER BY date"

    df = con.execute(query, seasons).fetchdf()
    con.close()

    # Convert spread to home perspective (negative = home favored)
    df['line_spread'] = df.apply(
        lambda r: -r['spread'] if r['whos_favored'] == 'home' else r['spread'],
        axis=1
    )
    # Map team abbreviations to NBA format
    df['home_abbr'] = df['home'].map(BETTING_TO_NBA)
    df['away_abbr'] = df['away'].map(BETTING_TO_NBA)
    df['date'] = pd.to_datetime(df['date'])

    return df


def match_games(betting_df: pd.DataFrame, games_df: pd.DataFrame) -> pd.DataFrame:
    """Match betting lines to game table rows by date + team abbreviations.
    
    Returns merged DataFrame with both betting line and game data.
    """
    # Normalize both DataFrames for matching
    betting = betting_df.copy()
    games = games_df.copy()
    games['game_date_str'] = games['game_date'].dt.strftime('%Y-%m-%d')
    betting['date_str'] = betting['date'].dt.strftime('%Y-%m-%d')

    merged = betting.merge(
        games,
        left_on=['date_str', 'home_abbr', 'away_abbr'],
        right_on=['game_date_str', 'home_team', 'away_team'],
        how='inner',
    )
    return merged


def run_ats_backtest(db_path: str,
                     seasons: list[int] = None,
                     use_all_layers: bool = True,
                     use_streaks: bool = False,
                     verbose: bool = True) -> pd.DataFrame:
    """Run the full ATS backtest.
    
    Args:
        db_path: Path to the DuckDB database
        seasons: List of betting_lines season years (e.g., [2018, 2019, ...])
                 Default: 2018-2023 (6 seasons)
        use_all_layers: Use all model layers (players, refs, coach)
        verbose: Print progress
        
    Returns:
        DataFrame with one row per bet, including model predictions,
        betting lines, and ATS results.
    """
    if seasons is None:
        seasons = [2018, 2019, 2020, 2021, 2022, 2023]

    season_ids = [season_to_season_id(s) for s in seasons]

    if verbose:
        print(f"ATS Backtest: seasons {seasons}")
        print(f"  → season_ids: {season_ids}")
        print(f"  → All layers: {use_all_layers}")
        print(f"  → Streaks: {use_streaks}")
        print()

    # ── Step 1: Run the walk-forward model backtest ──
    if verbose:
        print("Step 1: Running walk-forward model predictions...")
    bt = Backtester(db_path)
    model_results = bt.run(
        season_ids=season_ids,
        verbose=verbose,
        use_player_availability=use_all_layers,
        use_referee=use_all_layers,
        use_coach=use_all_layers,
        use_streaks=use_streaks,
    )

    if model_results.empty:
        print("ERROR: No model predictions generated!")
        return pd.DataFrame()

    if verbose:
        print(f"\n  Model produced {len(model_results)} predictions")

    # ── Step 2: Load betting lines ──
    if verbose:
        print("\nStep 2: Loading betting lines...")
    betting = load_betting_lines(db_path, seasons)
    if verbose:
        print(f"  Loaded {len(betting)} betting lines")

    # ── Step 3: Match games ──
    if verbose:
        print("\nStep 3: Matching model predictions to betting lines...")

    # Create date strings for matching
    betting['date_str'] = betting['date'].dt.strftime('%Y-%m-%d')
    model_results['date_str'] = model_results['game_date'].dt.strftime('%Y-%m-%d')

    # model_results has home_team/away_team as abbreviations
    matched = model_results.merge(
        betting[['date_str', 'home_abbr', 'away_abbr', 'line_spread', 'total',
                 'moneyline_away', 'moneyline_home', 'whos_favored', 'spread',
                 'season']].rename(columns={'total': 'line_total'}),
        left_on=['date_str', 'home_team', 'away_team'],
        right_on=['date_str', 'home_abbr', 'away_abbr'],
        how='inner',
    )

    if verbose:
        print(f"  Matched {len(matched)} games with both predictions and lines")
        print(f"  Unmatched model games: {len(model_results) - len(matched)}")

    if matched.empty:
        print("ERROR: No games matched between model and betting lines!")
        return pd.DataFrame()

    # ── Step 4: Determine the best model spread/total to use ──
    # Use the most advanced layer available
    if use_all_layers and 'final_spread' in matched.columns:
        matched['model_spread'] = matched['final_spread']
        matched['model_total'] = matched['final_total']
        spread_col = 'final_spread'
    elif 'ref_adj_spread' in matched.columns:
        matched['model_spread'] = matched['ref_adj_spread']
        matched['model_total'] = matched['ref_adj_total']
        spread_col = 'ref_adj_spread'
    elif 'adj_spread' in matched.columns:
        matched['model_spread'] = matched['adj_spread']
        matched['model_total'] = matched['adj_total']
        spread_col = 'adj_spread'
    else:
        matched['model_spread'] = matched['pred_spread']
        matched['model_total'] = matched['pred_total']
        spread_col = 'pred_spread'

    if verbose:
        print(f"  Using model spread from: {spread_col}")

    # ── Step 5: Calculate edges and ATS results ──
    if verbose:
        print("\nStep 4: Calculating ATS results...")

    # Spread edge: how much our model disagrees with the line
    # Both model_spread and line_spread are: away - home (negative = home favored)
    # edge = line_spread - model_spread
    # Positive edge → we think home is better than line → bet home
    # Negative edge → we think away is better than line → bet away
    matched['spread_edge'] = matched['line_spread'] - matched['model_spread']
    matched['abs_spread_edge'] = matched['spread_edge'].abs()

    # Actual spread (away - home, negative = home won by more)
    matched['actual_spread'] = matched['actual_away_pts'] - matched['actual_home_pts']

    # Determine if our side covered
    # If edge > 0: bet home → home covers if actual_spread < line_spread
    # If edge < 0: bet away → away covers if actual_spread > line_spread
    def spread_result(row):
        if row['spread_edge'] == 0:
            return 'no_bet'  # no disagreement
        if row['spread_edge'] > 0:
            # Bet home to cover
            diff = row['line_spread'] - row['actual_spread']
            if diff > 0:
                return 'win'
            elif diff < 0:
                return 'loss'
            else:
                return 'push'
        else:
            # Bet away to cover
            diff = row['actual_spread'] - row['line_spread']
            if diff > 0:
                return 'win'
            elif diff < 0:
                return 'loss'
            else:
                return 'push'

    matched['spread_result'] = matched.apply(spread_result, axis=1)

    # Totals edge
    matched['total_edge'] = matched['model_total'] - matched['line_total']
    matched['abs_total_edge'] = matched['total_edge'].abs()
    matched['actual_total'] = matched['actual_home_pts'] + matched['actual_away_pts']

    def total_result(row):
        if row['total_edge'] == 0:
            return 'no_bet'
        actual = row['actual_total']
        line = row['line_total']
        if row['total_edge'] > 0:
            # Bet over
            if actual > line:
                return 'win'
            elif actual < line:
                return 'loss'
            else:
                return 'push'
        else:
            # Bet under
            if actual < line:
                return 'win'
            elif actual > line:
                return 'loss'
            else:
                return 'push'

    matched['total_result'] = matched.apply(total_result, axis=1)

    # Edge bucket categorization
    def edge_bucket(edge):
        e = abs(edge)
        if e < 1:
            return '0-1'
        elif e < 2:
            return '1-2'
        elif e < 3:
            return '2-3'
        elif e < 5:
            return '3-5'
        else:
            return '5+'

    matched['spread_edge_bucket'] = matched['abs_spread_edge'].apply(edge_bucket)
    matched['total_edge_bucket'] = matched['abs_total_edge'].apply(edge_bucket)

    # ROI calculation: flat $100 bets at -110
    # Win: profit $90.91 (100/1.1)
    # Loss: lose $100
    # Push: $0
    def flat_bet_profit(result):
        if result == 'win':
            return 100 / 1.1  # ~$90.91
        elif result == 'loss':
            return -100.0
        else:
            return 0.0

    matched['spread_profit'] = matched['spread_result'].apply(flat_bet_profit)
    matched['total_profit'] = matched['total_result'].apply(flat_bet_profit)

    # Bet side description
    matched['spread_bet_side'] = matched['spread_edge'].apply(
        lambda e: 'HOME' if e > 0 else ('AWAY' if e < 0 else 'NO_BET'))
    matched['total_bet_side'] = matched['total_edge'].apply(
        lambda e: 'OVER' if e > 0 else ('UNDER' if e < 0 else 'NO_BET'))

    if verbose:
        # Quick summary
        spread_bets = matched[matched['spread_result'].isin(['win', 'loss', 'push'])]
        wins = (spread_bets['spread_result'] == 'win').sum()
        losses = (spread_bets['spread_result'] == 'loss').sum()
        pushes = (spread_bets['spread_result'] == 'push').sum()
        pct = wins / (wins + losses) if (wins + losses) > 0 else 0
        print(f"\n  Spread ATS: {wins}-{losses}-{pushes} ({pct:.1%})")
        print(f"  Spread ROI: {spread_bets['spread_profit'].sum() / (len(spread_bets[spread_bets['spread_result'] != 'push']) * 100) * 100:.2f}%" if len(spread_bets[spread_bets['spread_result'] != 'push']) > 0 else "  No decided spread bets")

    return matched


def compute_ats_metrics(df: pd.DataFrame, min_edge: float = 0.0) -> dict:
    """Compute ATS metrics from backtest results.
    
    Args:
        df: Backtest results DataFrame
        min_edge: Minimum absolute edge to include (0 = all bets with disagreement)
    
    Returns:
        dict with comprehensive ATS metrics
    """
    # Filter by minimum edge
    spread_bets = df[
        (df['spread_result'].isin(['win', 'loss', 'push'])) &
        (df['abs_spread_edge'] > min_edge)
    ].copy()

    total_bets = df[
        (df['total_result'].isin(['win', 'loss', 'push'])) &
        (df['abs_total_edge'] > min_edge)
    ].copy()

    metrics = {'min_edge': min_edge}

    # ── Spread ATS ──
    sw = (spread_bets['spread_result'] == 'win').sum()
    sl = (spread_bets['spread_result'] == 'loss').sum()
    sp = (spread_bets['spread_result'] == 'push').sum()
    decided = sw + sl
    metrics['spread_wins'] = sw
    metrics['spread_losses'] = sl
    metrics['spread_pushes'] = sp
    metrics['spread_record'] = f"{sw}-{sl}-{sp}"
    metrics['spread_pct'] = sw / decided if decided > 0 else 0
    metrics['spread_profit'] = spread_bets['spread_profit'].sum()
    wagered = decided * 100
    metrics['spread_wagered'] = wagered
    metrics['spread_roi'] = metrics['spread_profit'] / wagered if wagered > 0 else 0

    # ── Totals ATS ──
    tw = (total_bets['total_result'] == 'win').sum()
    tl = (total_bets['total_result'] == 'loss').sum()
    tp = (total_bets['total_result'] == 'push').sum()
    td = tw + tl
    metrics['total_wins'] = tw
    metrics['total_losses'] = tl
    metrics['total_pushes'] = tp
    metrics['total_record'] = f"{tw}-{tl}-{tp}"
    metrics['total_pct'] = tw / td if td > 0 else 0
    metrics['total_profit'] = total_bets['total_profit'].sum()
    twag = td * 100
    metrics['total_wagered'] = twag
    metrics['total_roi'] = metrics['total_profit'] / twag if twag > 0 else 0

    # ── Edge buckets (spread) ──
    buckets = {}
    for bucket in ['0-1', '1-2', '2-3', '3-5', '5+']:
        b = spread_bets[spread_bets['spread_edge_bucket'] == bucket]
        bw = (b['spread_result'] == 'win').sum()
        bl = (b['spread_result'] == 'loss').sum()
        bp = (b['spread_result'] == 'push').sum()
        bd = bw + bl
        buckets[bucket] = {
            'record': f"{bw}-{bl}-{bp}",
            'wins': bw, 'losses': bl, 'pushes': bp,
            'pct': bw / bd if bd > 0 else 0,
            'profit': b['spread_profit'].sum(),
            'roi': b['spread_profit'].sum() / (bd * 100) if bd > 0 else 0,
            'n_bets': len(b),
        }
    metrics['spread_edge_buckets'] = buckets

    # ── Edge buckets (totals) ──
    total_buckets = {}
    for bucket in ['0-1', '1-2', '2-3', '3-5', '5+']:
        b = total_bets[total_bets['total_edge_bucket'] == bucket]
        bw = (b['total_result'] == 'win').sum()
        bl = (b['total_result'] == 'loss').sum()
        bp = (b['total_result'] == 'push').sum()
        bd = bw + bl
        total_buckets[bucket] = {
            'record': f"{bw}-{bl}-{bp}",
            'wins': bw, 'losses': bl, 'pushes': bp,
            'pct': bw / bd if bd > 0 else 0,
            'profit': b['total_profit'].sum(),
            'roi': b['total_profit'].sum() / (bd * 100) if bd > 0 else 0,
            'n_bets': len(b),
        }
    metrics['total_edge_buckets'] = total_buckets

    # ── By season ──
    season_metrics = {}
    for season in sorted(spread_bets['season'].unique()):
        sb = spread_bets[spread_bets['season'] == season]
        ssw = (sb['spread_result'] == 'win').sum()
        ssl = (sb['spread_result'] == 'loss').sum()
        ssp = (sb['spread_result'] == 'push').sum()
        ssd = ssw + ssl
        season_metrics[season] = {
            'spread_record': f"{ssw}-{ssl}-{ssp}",
            'spread_pct': ssw / ssd if ssd > 0 else 0,
            'spread_roi': sb['spread_profit'].sum() / (ssd * 100) if ssd > 0 else 0,
            'n_bets': len(sb),
        }
        # Add totals for this season
        tb = total_bets[total_bets['season'] == season]
        tsw = (tb['total_result'] == 'win').sum()
        tsl = (tb['total_result'] == 'loss').sum()
        tsp = (tb['total_result'] == 'push').sum()
        tsd = tsw + tsl
        season_metrics[season]['total_record'] = f"{tsw}-{tsl}-{tsp}"
        season_metrics[season]['total_pct'] = tsw / tsd if tsd > 0 else 0
        season_metrics[season]['total_roi'] = tb['total_profit'].sum() / (tsd * 100) if tsd > 0 else 0

    metrics['by_season'] = season_metrics

    return metrics


def get_top_results(df: pd.DataFrame, n: int = 10) -> dict:
    """Get the top N biggest wins and losses by actual margin vs line."""
    spread_bets = df[df['spread_result'].isin(['win', 'loss'])].copy()
    spread_bets['cover_margin'] = spread_bets.apply(
        lambda r: (r['line_spread'] - r['actual_spread']) if r['spread_edge'] > 0
                   else (r['actual_spread'] - r['line_spread']),
        axis=1
    )

    biggest_wins = spread_bets.nlargest(n, 'cover_margin')[
        ['game_date', 'away_team', 'home_team', 'spread_bet_side',
         'line_spread', 'model_spread', 'actual_spread',
         'cover_margin', 'spread_edge', 'spread_profit']
    ]

    biggest_losses = spread_bets.nsmallest(n, 'cover_margin')[
        ['game_date', 'away_team', 'home_team', 'spread_bet_side',
         'line_spread', 'model_spread', 'actual_spread',
         'cover_margin', 'spread_edge', 'spread_profit']
    ]

    return {
        'biggest_wins': biggest_wins,
        'biggest_losses': biggest_losses,
    }


if __name__ == '__main__':
    import config as cfg
    db_path = os.path.join(cfg.DATA_DIR, 'nbadb', 'nba.duckdb')

    results = run_ats_backtest(db_path, verbose=True)

    if not results.empty:
        metrics = compute_ats_metrics(results)
        print(f"\nOverall Spread ATS: {metrics['spread_record']} ({metrics['spread_pct']:.1%})")
        print(f"Overall Spread ROI: {metrics['spread_roi']:.2%}")
        print(f"\nOverall Total ATS: {metrics['total_record']} ({metrics['total_pct']:.1%})")
        print(f"Overall Total ROI: {metrics['total_roi']:.2%}")
