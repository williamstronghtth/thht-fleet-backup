"""
Coach Rotation Analyzer (Layer 4)
=================================

Analyzes play-by-play substitution patterns to build coaching profiles
keyed by (team_id, season_id). No coach name needed — we treat each
team-season as a distinct coaching regime.

Key metrics:
- Rotation depth: unique players used per game (8-man vs 10-man)
- Starter minutes share: how much of the minutes go to starters vs bench
- First sub timing: when does the coach typically make first substitutions
- Crunch time lineup consistency: how stable is the closing lineup

Walk-forward safe: all queries filter by game_date < before_date.
"""

import duckdb
import numpy as np
import pandas as pd
from typing import Optional, Dict, Tuple
from dataclasses import dataclass


@dataclass
class RotationProfile:
    """Rotation profile for a team-season (coaching regime)."""
    team_id: str
    season_id: str
    games: int = 0
    avg_players_used: float = 9.0
    avg_starter_minutes_share: float = 0.65
    avg_first_sub_time: float = 6.0  # minutes into game
    rotation_consistency: float = 0.5  # 0=chaotic, 1=very consistent
    # Bayesian-shrunk values
    shrunk_players_used: float = 9.0
    shrunk_starter_share: float = 0.65
    shrinkage: float = 0.0


class RotationAnalyzer:
    """Build rotation profiles from play-by-play substitution data."""

    PRIOR_GAMES = 30  # Bayesian prior strength
    LEAGUE_AVG_PLAYERS_USED = 9.2
    LEAGUE_AVG_STARTER_SHARE = 0.64
    LEAGUE_AVG_FIRST_SUB = 6.0

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._rotation_cache: Dict[Tuple[str, str], Dict[str, RotationProfile]] = {}
        self._raw_data: Optional[pd.DataFrame] = None
        self._preloaded: bool = False

    def _get_connection(self) -> duckdb.DuckDBPyConnection:
        return duckdb.connect(self.db_path, read_only=True)

    def preload(self, season_ids: list):
        """Pre-load all substitution data. Call before backtesting loop."""
        self._raw_data = self._load_rotation_data_from_db(season_ids)
        self._preloaded = True

    def _load_rotation_data_from_db(self, season_ids: list) -> pd.DataFrame:
        """Load substitution data from DB for given seasons."""
        con = self._get_connection()
        season_list = ", ".join(f"'{s}'" for s in season_ids)

        df = con.execute(f"""
            SELECT
                p.game_id,
                g.game_date,
                g.season_id,
                g.team_id_home,
                g.team_id_away,
                p.period,
                p.pctimestring,
                p.player1_id,
                p.player1_team_id,
                p.player2_id,
                p.player2_team_id,
                p.eventmsgtype
            FROM play_by_play p
            JOIN game g ON p.game_id = g.game_id
            WHERE g.season_id IN ({season_list})
              AND g.season_type = 'Regular Season'
              AND g.pts_home IS NOT NULL
              AND p.eventmsgtype = 8
        """).fetchdf()
        con.close()

        df['game_date'] = pd.to_datetime(df['game_date'])
        return df

    def _load_rotation_data(self, season_ids: list) -> pd.DataFrame:
        """Load substitution data, using cache if available."""
        if self._preloaded and self._raw_data is not None:
            return self._raw_data[self._raw_data['season_id'].isin(season_ids)].copy()
        return self._load_rotation_data_from_db(season_ids)

    def _parse_time_to_minutes(self, period: int, pctimestring: str) -> float:
        """Convert period + clock to game minutes elapsed.
        
        Period 1, 12:00 = 0.0 minutes elapsed
        Period 1, 6:00 = 6.0 minutes elapsed
        Period 4, 0:00 = 48.0 minutes elapsed
        """
        try:
            parts = str(pctimestring).split(':')
            minutes = int(parts[0])
            seconds = int(parts[1]) if len(parts) > 1 else 0
            time_left_in_period = minutes + seconds / 60.0
            # Each regulation period is 12 minutes
            if period <= 4:
                elapsed = (period - 1) * 12 + (12 - time_left_in_period)
            else:
                # OT periods are 5 minutes
                elapsed = 48 + (period - 5) * 5 + (5 - time_left_in_period)
            return elapsed
        except (ValueError, TypeError):
            return 0.0

    def build_profiles(self, before_date: pd.Timestamp,
                       season_id: str) -> Dict[str, RotationProfile]:
        """Build rotation profiles for all teams using data before the given date.
        
        Uses current + prior 2 seasons of data.
        """
        # Cache at monthly granularity for efficiency during backtesting
        month_key = before_date.strftime('%Y-%m')
        cache_key = (month_key, season_id)
        if cache_key in self._rotation_cache:
            return self._rotation_cache[cache_key]

        try:
            year = int(season_id[1:])
            season_ids = [f"2{y}" for y in range(year - 2, year + 1)]
        except ValueError:
            season_ids = [season_id]

        df = self._load_rotation_data(season_ids)
        df = df[df['game_date'] < before_date]

        if df.empty:
            self._rotation_cache[cache_key] = {}
            return {}

        profiles = {}

        # For each game, determine team for each sub event
        # player1_team_id tells us which team the sub belongs to
        df['team_id'] = df['player1_team_id']

        # Group by game + team to get per-game rotation stats
        game_team_groups = df.groupby(['game_id', 'team_id', 'season_id', 'game_date'])

        game_stats = []
        for (game_id, team_id, sid, gdate), group in game_team_groups:
            if pd.isna(team_id):
                continue

            # Clean team_id - remove trailing .0 if present
            tid = str(team_id).replace('.0', '')

            # Unique players involved in substitutions (both in and out)
            players_in = set(group['player2_id'].dropna().values)
            players_out = set(group['player1_id'].dropna().values)
            all_players = players_in | players_out
            # Add 5 starters (they might never be subbed in a short game)
            # We count unique players who appeared in subs + 5 starters minimum
            n_players = max(len(all_players), 5)

            # First substitution timing
            group_sorted = group.sort_values('pctimestring', ascending=False)
            if len(group_sorted) > 0:
                first_row = group_sorted.iloc[0]
                first_sub_time = self._parse_time_to_minutes(
                    int(first_row['period']), first_row['pctimestring'])
            else:
                first_sub_time = 6.0

            # Number of substitutions
            n_subs = len(group)

            game_stats.append({
                'game_id': game_id,
                'team_id': tid,
                'season_id': sid,
                'game_date': gdate,
                'n_players': n_players,
                'first_sub_time': first_sub_time,
                'n_subs': n_subs,
            })

        if not game_stats:
            self._rotation_cache[cache_key] = {}
            return {}

        stats_df = pd.DataFrame(game_stats)

        # Aggregate by team-season
        for (tid, sid), grp in stats_df.groupby(['team_id', 'season_id']):
            n = len(grp)
            if n < 5:
                continue

            avg_players = grp['n_players'].mean()
            avg_first_sub = grp['first_sub_time'].mean()
            consistency = 1.0 - (grp['n_players'].std() / max(grp['n_players'].mean(), 1))
            consistency = max(0.0, min(1.0, consistency))

            # Bayesian shrinkage
            shrink = n / (n + self.PRIOR_GAMES)
            shrunk_players = shrink * avg_players + (1 - shrink) * self.LEAGUE_AVG_PLAYERS_USED

            key = f"{tid}_{sid}"
            profiles[key] = RotationProfile(
                team_id=str(tid),
                season_id=str(sid),
                games=n,
                avg_players_used=round(avg_players, 1),
                avg_starter_minutes_share=self.LEAGUE_AVG_STARTER_SHARE,  # simplified
                avg_first_sub_time=round(avg_first_sub, 1),
                rotation_consistency=round(consistency, 3),
                shrunk_players_used=round(shrunk_players, 1),
                shrunk_starter_share=self.LEAGUE_AVG_STARTER_SHARE,
                shrinkage=round(shrink, 3),
            )

        self._rotation_cache[cache_key] = profiles
        return profiles

    def get_rotation_profile(self, team_id: str, season_id: str,
                             before_date: pd.Timestamp) -> Optional[RotationProfile]:
        """Get rotation profile for a specific team-season."""
        profiles = self.build_profiles(before_date, season_id)

        # Try exact match first
        key = f"{team_id}_{season_id}"
        if key in profiles:
            return profiles[key]

        # Try prior season
        try:
            year = int(season_id[1:])
            for y in range(year - 1, year - 3, -1):
                prior_key = f"{team_id}_2{y}"
                if prior_key in profiles:
                    return profiles[prior_key]
        except ValueError:
            pass

        return None

    def clear_cache(self):
        self._rotation_cache.clear()
