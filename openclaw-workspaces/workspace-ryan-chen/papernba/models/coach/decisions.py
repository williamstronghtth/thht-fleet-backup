"""
Coach Decisions Model (Layer 4)
================================

Analyzes coaching decision patterns from play-by-play data:
- 4th quarter clutch performance (team over/underperformance relative to rating)
- Pace management in close games (speed up or slow down?)
- Timeout patterns (frequency, timing)

All metrics use Bayesian shrinkage and are walk-forward safe.
Coach = team_id + season_id (no name needed).
"""

import duckdb
import numpy as np
import pandas as pd
from typing import Optional, Dict, Tuple
from dataclasses import dataclass


@dataclass
class CoachDecisionProfile:
    """Decision profile for a team-season coaching regime."""
    team_id: str
    season_id: str
    games: int = 0

    # 4th quarter clutch performance
    q4_close_games: int = 0  # games within 10 pts entering Q4
    q4_margin_vs_expected: float = 0.0  # how much better/worse than expected in Q4
    q4_win_rate_close: float = 0.5  # win rate in close games

    # Pace management
    pace_q4_close_ratio: float = 1.0  # Q4 close-game pace / overall pace
    # <1 means coach slows down, >1 means speeds up

    # Timeout patterns
    timeouts_per_game: float = 4.5
    timeouts_q4: float = 1.5  # timeouts specifically in Q4

    # Shrunk values
    shrunk_q4_margin: float = 0.0
    shrunk_pace_ratio: float = 1.0
    shrinkage: float = 0.0


class CoachDecisionAnalyzer:
    """Analyze coaching decision patterns from play-by-play."""

    PRIOR_GAMES = 30
    LEAGUE_AVG_Q4_MARGIN = 0.0  # by definition, average is zero
    LEAGUE_AVG_PACE_RATIO = 1.0
    LEAGUE_AVG_TIMEOUTS = 4.5

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._decision_cache: Dict[Tuple[str, str], Dict[str, CoachDecisionProfile]] = {}
        self._q4_data: Optional[pd.DataFrame] = None
        self._timeout_data: Optional[pd.DataFrame] = None

    def _get_connection(self) -> duckdb.DuckDBPyConnection:
        return duckdb.connect(self.db_path, read_only=True)

    def preload(self, season_ids: list):
        """Pre-load all Q4 and timeout data once. Call before backtesting loop."""
        self._q4_data = self._load_q4_data_all(season_ids)
        self._timeout_data = self._load_timeout_data_all(season_ids)

    def _load_q4_data_all(self, season_ids: list) -> pd.DataFrame:
        """Load ALL Q4 data for given seasons (no date filter). Filter later."""
        con = self._get_connection()
        season_list = ", ".join(f"'{s}'" for s in season_ids)

        df = con.execute(f"""
            WITH q3_end AS (
                SELECT
                    p.game_id,
                    LAST(p.score ORDER BY p.eventnum) as q3_score
                FROM play_by_play p
                JOIN game g ON p.game_id = g.game_id
                WHERE g.season_id IN ({season_list})
                  AND g.season_type = 'Regular Season'
                  AND g.pts_home IS NOT NULL
                  AND p.period = 3
                  AND p.score IS NOT NULL
                GROUP BY p.game_id
            ),
            q4_scoring AS (
                SELECT
                    p.game_id,
                    g.game_date,
                    g.season_id,
                    g.team_id_home,
                    g.team_id_away,
                    g.pts_home,
                    g.pts_away,
                    COUNT(CASE WHEN p.eventmsgtype IN (1, 2, 3, 5) THEN 1 END) as q4_possessions_proxy
                FROM play_by_play p
                JOIN game g ON p.game_id = g.game_id
                WHERE g.season_id IN ({season_list})
                  AND g.season_type = 'Regular Season'
                  AND g.pts_home IS NOT NULL
                  AND p.period = 4
                GROUP BY p.game_id, g.game_date, g.season_id,
                         g.team_id_home, g.team_id_away, g.pts_home, g.pts_away
            )
            SELECT
                q4.game_id, q4.game_date, q4.season_id,
                q4.team_id_home, q4.team_id_away,
                q4.pts_home, q4.pts_away,
                q4.q4_possessions_proxy,
                q3.q3_score
            FROM q4_scoring q4
            LEFT JOIN q3_end q3 ON q4.game_id = q3.game_id
        """).fetchdf()
        con.close()
        df['game_date'] = pd.to_datetime(df['game_date'])
        return df

    def _load_timeout_data_all(self, season_ids: list) -> pd.DataFrame:
        """Load ALL timeout data for given seasons (no date filter)."""
        con = self._get_connection()
        season_list = ", ".join(f"'{s}'" for s in season_ids)

        df = con.execute(f"""
            SELECT
                p.game_id,
                g.game_date,
                g.season_id,
                g.team_id_home,
                g.team_id_away,
                p.player1_id as team_calling,
                p.period,
                COUNT(*) as n_timeouts
            FROM play_by_play p
            JOIN game g ON p.game_id = g.game_id
            WHERE g.season_id IN ({season_list})
              AND g.season_type = 'Regular Season'
              AND g.pts_home IS NOT NULL
              AND p.eventmsgtype = 9
            GROUP BY p.game_id, g.game_date, g.season_id,
                     g.team_id_home, g.team_id_away, p.player1_id, p.period
        """).fetchdf()
        con.close()
        df['game_date'] = pd.to_datetime(df['game_date'])
        return df

    def _load_q4_data(self, season_ids: list, before_date: pd.Timestamp) -> pd.DataFrame:
        """Load 4th quarter scoring data, using cache if available."""
        if self._q4_data is not None:
            # Filter from pre-loaded data
            mask = (self._q4_data['game_date'] < before_date) & \
                   (self._q4_data['season_id'].isin(season_ids))
            return self._q4_data[mask].copy()

        # Fall back to loading from DB
        df = self._load_q4_data_all(season_ids)
        return df[df['game_date'] < before_date].copy()

    def _load_timeout_data(self, season_ids: list, before_date: pd.Timestamp) -> pd.DataFrame:
        """Load timeout event counts, using cache if available."""
        if self._timeout_data is not None:
            mask = (self._timeout_data['game_date'] < before_date) & \
                   (self._timeout_data['season_id'].isin(season_ids))
            return self._timeout_data[mask].copy()

        # Fall back to loading from DB
        df = self._load_timeout_data_all(season_ids)
        return df[df['game_date'] < before_date].copy()

    def _parse_score_margin(self, score_str: str) -> Optional[int]:
        """Parse score string like '89 - 94' to margin (home - away)."""
        if pd.isna(score_str) or not score_str:
            return None
        try:
            parts = str(score_str).split('-')
            if len(parts) == 2:
                away = int(parts[0].strip())
                home = int(parts[1].strip())
                return home - away
        except (ValueError, TypeError):
            pass
        return None

    def build_profiles(self, before_date: pd.Timestamp,
                       season_id: str) -> Dict[str, CoachDecisionProfile]:
        """Build decision profiles for all teams."""
        # Cache at monthly granularity for efficiency during backtesting
        month_key = before_date.strftime('%Y-%m')
        cache_key = (month_key, season_id)
        if cache_key in self._decision_cache:
            return self._decision_cache[cache_key]

        try:
            year = int(season_id[1:])
            season_ids = [f"2{y}" for y in range(year - 2, year + 1)]
        except ValueError:
            season_ids = [season_id]

        # Load Q4 data
        q4_df = self._load_q4_data(season_ids, before_date)

        # Load timeout data
        to_df = self._load_timeout_data(season_ids, before_date)

        profiles = {}

        if q4_df.empty:
            self._decision_cache[cache_key] = {}
            return {}

        # Parse Q3 scores to identify close games
        q4_df['q3_margin'] = q4_df['q3_score'].apply(self._parse_score_margin)
        q4_df['is_close'] = q4_df['q3_margin'].apply(
            lambda m: abs(m) <= 10 if m is not None else False)

        # Calculate game-level stats
        q4_df['home_margin'] = q4_df['pts_home'] - q4_df['pts_away']

        # Process for both home and away teams
        for is_home in [True, False]:
            if is_home:
                team_col = 'team_id_home'
                margin_sign = 1
            else:
                team_col = 'team_id_away'
                margin_sign = -1

            for (tid, sid), grp in q4_df.groupby([team_col, 'season_id']):
                tid_str = str(tid)
                key = f"{tid_str}_{sid}"

                if key not in profiles:
                    profiles[key] = {
                        'team_id': tid_str,
                        'season_id': str(sid),
                        'games': 0,
                        'close_games': 0,
                        'close_margins': [],
                        'all_margins': [],
                        'q4_poss_proxy': [],
                        'close_q4_poss': [],
                    }

                p = profiles[key]
                p['games'] += len(grp)
                p['all_margins'].extend((grp['home_margin'] * margin_sign).tolist())

                close = grp[grp['is_close']]
                p['close_games'] += len(close)
                p['close_margins'].extend((close['home_margin'] * margin_sign).tolist())
                p['q4_poss_proxy'].extend(grp['q4_possessions_proxy'].tolist())
                if len(close) > 0:
                    p['close_q4_poss'].extend(close['q4_possessions_proxy'].tolist())

        # Process timeouts
        timeout_stats = {}
        if not to_df.empty:
            # Aggregate timeouts per game per team
            for _, row in to_df.iterrows():
                team_calling = str(row['team_calling']).replace('.0', '')
                sid = row['season_id']
                key = f"{team_calling}_{sid}"

                if key not in timeout_stats:
                    timeout_stats[key] = {'total_to': 0, 'q4_to': 0, 'games_with_to': set()}

                timeout_stats[key]['total_to'] += row['n_timeouts']
                timeout_stats[key]['games_with_to'].add(row['game_id'])
                if row['period'] == 4:
                    timeout_stats[key]['q4_to'] += row['n_timeouts']

        # Build final profiles
        result = {}
        for key, p in profiles.items():
            n = p['games']
            if n < 5:
                continue

            # Overall margin
            avg_margin = np.mean(p['all_margins']) if p['all_margins'] else 0.0

            # Close game Q4 performance
            q4_close_games = p['close_games']
            if q4_close_games >= 3:
                q4_margin = np.mean(p['close_margins'])
                # Q4 margin vs expected = how much they over/underperform
                # Expected is roughly proportional to overall margin
                q4_margin_vs_expected = q4_margin - avg_margin * 0.25  # Q4 is 1/4 of game
            else:
                q4_margin_vs_expected = 0.0

            # Pace ratio (close Q4 vs all Q4)
            if p['close_q4_poss'] and p['q4_poss_proxy']:
                avg_close_poss = np.mean(p['close_q4_poss'])
                avg_all_poss = np.mean(p['q4_poss_proxy'])
                pace_ratio = avg_close_poss / max(avg_all_poss, 1) if avg_all_poss > 0 else 1.0
            else:
                pace_ratio = 1.0

            # Timeout stats
            to_info = timeout_stats.get(key, {'total_to': 0, 'q4_to': 0, 'games_with_to': set()})
            n_to_games = max(len(to_info['games_with_to']), 1)
            to_per_game = to_info['total_to'] / max(n_to_games, 1)
            to_q4 = to_info['q4_to'] / max(n_to_games, 1)

            # Close game win rate
            if p['close_margins']:
                close_wins = sum(1 for m in p['close_margins'] if m > 0)
                q4_win_rate = close_wins / len(p['close_margins'])
            else:
                q4_win_rate = 0.5

            # Bayesian shrinkage
            shrink = n / (n + self.PRIOR_GAMES)
            shrunk_q4 = shrink * q4_margin_vs_expected + (1 - shrink) * self.LEAGUE_AVG_Q4_MARGIN
            shrunk_pace = shrink * pace_ratio + (1 - shrink) * self.LEAGUE_AVG_PACE_RATIO

            result[key] = CoachDecisionProfile(
                team_id=p['team_id'],
                season_id=p['season_id'],
                games=n,
                q4_close_games=q4_close_games,
                q4_margin_vs_expected=round(q4_margin_vs_expected, 2),
                q4_win_rate_close=round(q4_win_rate, 3),
                pace_q4_close_ratio=round(pace_ratio, 3),
                timeouts_per_game=round(to_per_game, 1),
                timeouts_q4=round(to_q4, 1),
                shrunk_q4_margin=round(shrunk_q4, 2),
                shrunk_pace_ratio=round(shrunk_pace, 3),
                shrinkage=round(shrink, 3),
            )

        self._decision_cache[cache_key] = result
        return result

    def get_decision_profile(self, team_id: str, season_id: str,
                             before_date: pd.Timestamp) -> Optional[CoachDecisionProfile]:
        """Get decision profile for a specific team-season."""
        profiles = self.build_profiles(before_date, season_id)

        key = f"{team_id}_{season_id}"
        if key in profiles:
            return profiles[key]

        # Fallback to prior season
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
        self._decision_cache.clear()
