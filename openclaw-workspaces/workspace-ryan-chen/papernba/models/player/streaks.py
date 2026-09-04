"""
Player Hot Streak Detector
==========================

Detects players who are performing significantly above or below their
rolling baseline, and computes team-level streak adjustments.

Walk-forward safe: only uses games strictly before the prediction date.

Streak score = (last_5_avg - season_avg) / season_avg
- Hot: streak_score > 0.15  (15%+ above average)
- Cold: streak_score < -0.15 (15%+ below average)

Team adjustment is a weighted sum of player streak scores,
scaled conservatively (0.5–1.5 pts max per team).
"""

import duckdb
import pandas as pd
import numpy as np
from typing import Optional, Dict, Tuple, List


class PlayerStreakScore:
    """Streak metrics for a single player at a point in time."""
    __slots__ = [
        'player_id', 'player_name', 'team_id',
        'ppg_last5', 'ppg_baseline', 'pts_streak_score',
        'fg_pct_last5', 'fg_pct_baseline', 'fg_pct_streak_score',
        'pm_last5', 'pm_baseline', 'pm_streak_score',
        'composite_streak', 'mpg_last5',
        'is_hot', 'is_cold', 'games_used',
    ]

    def __init__(self):
        for s in self.__slots__:
            setattr(self, s, 0.0)
        self.player_id = 0
        self.player_name = ''
        self.team_id = 0
        self.is_hot = False
        self.is_cold = False
        self.games_used = 0


class StreakDetector:
    """Detect hot/cold streaks for players and compute team adjustments."""

    STREAK_WINDOW = 5       # last N games for streak calculation
    BASELINE_WINDOW = 20    # rolling baseline window
    MIN_BASELINE_GAMES = 8  # need at least this many games for a baseline
    MIN_MPG = 15.0          # only track streaks for rotation+ players
    HOT_THRESHOLD = 0.15    # 15% above average = hot
    COLD_THRESHOLD = -0.15  # 15% below average = cold

    # Team adjustment parameters
    MAX_TEAM_ADJ = 1.5      # max points adjustment per team
    STREAK_WEIGHT = 0.6     # how aggressively to translate streak → points

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._game_logs: Optional[pd.DataFrame] = None
        # Cache: (player_id, team_id, date_str) -> PlayerStreakScore
        self._cache: Dict[Tuple[int, int, str], Optional[PlayerStreakScore]] = {}

    def _load_game_logs(self):
        """Load all player game logs, sorted by date."""
        if self._game_logs is not None:
            return
        con = duckdb.connect(self.db_path, read_only=True)
        df = con.execute("""
            SELECT
                p.player_id, p.player_name, p.team_id,
                p.game_id, p.game_date, p.season,
                p.min, p.pts, p.fgm, p.fga, p.fg_pct,
                p.fg3m, p.fg3a, p.plus_minus
            FROM player_game_log p
            WHERE p.min IS NOT NULL AND p.min > 0
            ORDER BY p.player_id, p.game_date, p.game_id
        """).fetchdf()
        df['game_date'] = pd.to_datetime(df['game_date'])
        df['player_id'] = df['player_id'].astype(int)
        df['team_id'] = df['team_id'].astype(int)
        self._game_logs = df
        con.close()

    def get_streak(self, player_id: int, team_id: int,
                   before_date: pd.Timestamp) -> Optional[PlayerStreakScore]:
        """Compute streak score for a player using only games before the given date.

        Uses last 5 games vs rolling 20-game baseline.
        """
        date_key = before_date.strftime('%Y-%m-%d')
        cache_key = (player_id, team_id, date_key)
        if cache_key in self._cache:
            return self._cache[cache_key]

        self._load_game_logs()
        gl = self._game_logs

        # All games for this player before the date
        player_games = gl[
            (gl['player_id'] == player_id) &
            (gl['game_date'] < before_date)
        ].sort_values('game_date', ascending=False)

        # Need at least BASELINE_WINDOW games (so we have 5 recent + enough baseline)
        if len(player_games) < self.MIN_BASELINE_GAMES:
            self._cache[cache_key] = None
            return None

        # Last 5 games
        last5 = player_games.head(self.STREAK_WINDOW)
        if len(last5) < self.STREAK_WINDOW:
            self._cache[cache_key] = None
            return None

        # Check minutes threshold on recent play
        avg_min_last5 = last5['min'].mean()
        if avg_min_last5 < self.MIN_MPG:
            self._cache[cache_key] = None
            return None

        # Baseline: rolling 20-game window (includes the last 5)
        baseline = player_games.head(self.BASELINE_WINDOW)

        streak = PlayerStreakScore()
        streak.player_id = player_id
        streak.player_name = last5.iloc[0]['player_name']
        streak.team_id = team_id
        streak.games_used = len(baseline)
        streak.mpg_last5 = avg_min_last5

        # PPG streak
        streak.ppg_last5 = last5['pts'].mean()
        streak.ppg_baseline = baseline['pts'].mean()
        if streak.ppg_baseline > 2.0:  # avoid division by tiny numbers
            streak.pts_streak_score = (
                (streak.ppg_last5 - streak.ppg_baseline) / streak.ppg_baseline
            )
        else:
            streak.pts_streak_score = 0.0

        # FG% streak (use raw makes/attempts for accuracy)
        fgm_last5 = last5['fgm'].sum()
        fga_last5 = last5['fga'].sum()
        fgm_base = baseline['fgm'].sum()
        fga_base = baseline['fga'].sum()

        streak.fg_pct_last5 = fgm_last5 / fga_last5 if fga_last5 > 0 else 0.0
        streak.fg_pct_baseline = fgm_base / fga_base if fga_base > 0 else 0.0
        if streak.fg_pct_baseline > 0.1:
            streak.fg_pct_streak_score = (
                (streak.fg_pct_last5 - streak.fg_pct_baseline) / streak.fg_pct_baseline
            )
        else:
            streak.fg_pct_streak_score = 0.0

        # Plus/minus streak
        streak.pm_last5 = last5['plus_minus'].mean()
        streak.pm_baseline = baseline['plus_minus'].mean()
        # Plus/minus can be negative, so use absolute baseline for scaling
        pm_scale = max(abs(streak.pm_baseline), 2.0)
        streak.pm_streak_score = (streak.pm_last5 - streak.pm_baseline) / pm_scale

        # Composite streak: weighted combination
        # PPG is the primary signal, FG% and +/- are supporting
        streak.composite_streak = (
            0.60 * streak.pts_streak_score +
            0.25 * streak.fg_pct_streak_score +
            0.15 * streak.pm_streak_score
        )

        # Hot/cold classification
        streak.is_hot = streak.composite_streak > self.HOT_THRESHOLD
        streak.is_cold = streak.composite_streak < self.COLD_THRESHOLD

        self._cache[cache_key] = streak
        return streak

    def get_team_streak_adjustment(self, team_id: int,
                                    active_player_ids: List[int],
                                    before_date: pd.Timestamp) -> dict:
        """Compute team-level streak adjustment based on active players.

        Weights each player's streak score by their recent minutes.
        Returns a conservative scoring adjustment (positive = team trending up).

        Args:
            team_id: Team NBA ID
            active_player_ids: List of player IDs who ARE playing (not inactive)
            before_date: Game date

        Returns:
            dict with adjustment info
        """
        streaks = []
        for pid in active_player_ids:
            s = self.get_streak(pid, team_id, before_date)
            if s is not None:
                streaks.append(s)

        if not streaks:
            return {
                'streak_adj': 0.0,
                'n_players_with_streaks': 0,
                'n_hot': 0,
                'n_cold': 0,
                'weighted_streak': 0.0,
            }

        # Weight by minutes (starters matter more)
        total_min = sum(s.mpg_last5 for s in streaks)
        if total_min <= 0:
            return {
                'streak_adj': 0.0,
                'n_players_with_streaks': len(streaks),
                'n_hot': sum(1 for s in streaks if s.is_hot),
                'n_cold': sum(1 for s in streaks if s.is_cold),
                'weighted_streak': 0.0,
            }

        weighted_streak = sum(
            s.composite_streak * (s.mpg_last5 / total_min)
            for s in streaks
        )

        # Convert to points adjustment
        # A weighted_streak of 0.10 means the team's players are ~10% above average
        # For a team scoring ~110 PPG, that's ~11 pts raw — but we want conservative
        # Scale: weighted_streak * STREAK_WEIGHT * base_ppg_factor
        # With max cap of MAX_TEAM_ADJ
        raw_adj = weighted_streak * self.STREAK_WEIGHT * 10.0  # ~10 pts scale factor
        adj = np.clip(raw_adj, -self.MAX_TEAM_ADJ, self.MAX_TEAM_ADJ)

        return {
            'streak_adj': round(adj, 3),
            'n_players_with_streaks': len(streaks),
            'n_hot': sum(1 for s in streaks if s.is_hot),
            'n_cold': sum(1 for s in streaks if s.is_cold),
            'weighted_streak': round(weighted_streak, 4),
        }

    def get_team_active_players(self, team_id: int,
                                 before_date: pd.Timestamp,
                                 inactive_ids: Optional[List[int]] = None,
                                 top_n: int = 12) -> List[int]:
        """Get the active roster for a team before a given date.

        Returns player IDs who played recently and are NOT in the inactive list.
        """
        self._load_game_logs()
        gl = self._game_logs

        # Players who played for this team in last 30 days
        cutoff = before_date - pd.Timedelta(days=45)
        recent = gl[
            (gl['team_id'] == team_id) &
            (gl['game_date'] < before_date) &
            (gl['game_date'] >= cutoff)
        ]

        if recent.empty:
            return []

        # Top players by total minutes
        player_mins = recent.groupby('player_id')['min'].sum().sort_values(ascending=False)
        candidates = player_mins.head(top_n).index.tolist()

        # Remove inactive players
        if inactive_ids:
            inactive_set = set(int(p) for p in inactive_ids)
            candidates = [p for p in candidates if int(p) not in inactive_set]

        return [int(p) for p in candidates]

    def clear_cache(self):
        self._cache.clear()
