"""
Home Court Advantage Model
==========================

Quantifies home court advantage from historical NBA data:
- Average home margin
- Home win percentage
- Home/away offensive and defensive splits
- Season-by-season trends
"""

import duckdb
import pandas as pd
import numpy as np
from typing import Optional


class HomeCourtModel:
    """Analyzes and quantifies NBA home court advantage."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._cache: Optional[pd.DataFrame] = None

    def _load_games(self) -> pd.DataFrame:
        if self._cache is not None:
            return self._cache
        con = duckdb.connect(self.db_path, read_only=True)
        df = con.execute("""
            SELECT game_id, game_date, season_id,
                   pts_home, pts_away,
                   fga_home, oreb_home, tov_home, fta_home,
                   fga_away, oreb_away, tov_away, fta_away
            FROM game
            WHERE season_type = 'Regular Season'
              AND pts_home IS NOT NULL AND pts_away IS NOT NULL
        """).fetchdf()
        con.close()
        df['game_date'] = pd.to_datetime(df['game_date'])
        df['home_margin'] = df['pts_home'] - df['pts_away']
        df['home_win'] = (df['pts_home'] > df['pts_away']).astype(int)
        self._cache = df
        return df

    def overall_stats(self) -> dict:
        """Calculate overall home court advantage across all seasons."""
        df = self._load_games()
        return {
            'avg_home_margin': df['home_margin'].mean(),
            'home_win_pct': df['home_win'].mean(),
            'avg_home_pts': df['pts_home'].mean(),
            'avg_away_pts': df['pts_away'].mean(),
            'total_games': len(df),
        }

    def by_season(self) -> pd.DataFrame:
        """Calculate home court advantage by season.
        
        Returns DataFrame with season_id, avg_margin, home_win_pct, games.
        Useful for seeing trends (home court advantage has been declining).
        """
        df = self._load_games()
        result = df.groupby('season_id').agg(
            avg_margin=('home_margin', 'mean'),
            home_win_pct=('home_win', 'mean'),
            avg_home_pts=('pts_home', 'mean'),
            avg_away_pts=('pts_away', 'mean'),
            games=('game_id', 'count'),
        ).reset_index()
        return result.sort_values('season_id')

    def get_home_advantage(self, season_id: str, before_date: Optional[pd.Timestamp] = None) -> dict:
        """Get home court advantage parameters for prediction.
        
        Uses a blend of recent seasons (last 3) to estimate current home advantage.
        If before_date is provided, only uses data before that date.
        
        Returns:
            dict with 'margin' (expected home advantage in points) and 
            'off_boost' / 'def_boost' (multipliers for rating adjustments)
        """
        df = self._load_games()
        
        if before_date is not None:
            df = df[df['game_date'] < before_date]

        # Use last 3 seasons of data for stability
        try:
            year = int(season_id[1:])
            recent_seasons = [f"2{year}", f"2{year-1}", f"2{year-2}"]
        except ValueError:
            recent_seasons = df['season_id'].unique()[-3:]

        recent = df[df['season_id'].isin(recent_seasons)]
        
        if len(recent) < 100:
            recent = df  # fallback to all data

        avg_margin = recent['home_margin'].mean()
        
        # Calculate offensive/defensive splits for home/away
        # Home teams score more and allow less
        home_pts_avg = recent['pts_home'].mean()
        away_pts_avg = recent['pts_away'].mean()
        overall_avg = (home_pts_avg + away_pts_avg) / 2

        # Express as multiplicative factors
        off_boost = home_pts_avg / overall_avg  # typically ~1.015
        def_boost = away_pts_avg / overall_avg  # typically ~0.985

        return {
            'margin': avg_margin,
            'off_boost': off_boost,
            'def_boost': def_boost,
            'home_win_pct': recent['home_win'].mean(),
            'games_used': len(recent),
        }

    def print_trends(self):
        """Print home court advantage trends by season."""
        by_season = self.by_season()
        # Only show recent seasons (2000+)
        recent = by_season[by_season['season_id'] >= '22000']
        print("\n=== Home Court Advantage by Season ===")
        print(f"{'Season':<10} {'Margin':>8} {'Win%':>8} {'Home Pts':>10} {'Away Pts':>10} {'Games':>6}")
        print("-" * 55)
        for _, row in recent.iterrows():
            season_year = row['season_id'][1:]
            print(f"{season_year:<10} {row['avg_margin']:>8.2f} {row['home_win_pct']:>8.3f} "
                  f"{row['avg_home_pts']:>10.1f} {row['avg_away_pts']:>10.1f} {int(row['games']):>6}")
