"""
Player Profile Model
====================

Builds rolling statistical profiles for each player using individual game logs.
Walk-forward safe: only uses games strictly before the prediction date.

Key metrics:
- Rolling per-game averages (exponentially decayed, last 20 games)
- Usage rate proxy: (FGA + 0.44*FTA + TOV) per minute
- Efficiency: TS%, points per possession used
- Minutes share: % of team's total minutes
"""

import duckdb
import pandas as pd
import numpy as np
from typing import Optional, Dict, Tuple


class PlayerProfile:
    """Rolling statistical profile for a single player at a point in time."""
    __slots__ = [
        'player_id', 'player_name', 'team_id', 'games_used',
        'ppg', 'rpg', 'apg', 'spg', 'bpg', 'mpg',
        'fga_pg', 'fta_pg', 'tov_pg', 'plus_minus_pg',
        'usage_rate', 'ts_pct', 'pts_per_poss',
        'minutes_share', 'fg3a_pg',
    ]

    def __init__(self):
        for s in self.__slots__:
            setattr(self, s, 0.0)
        self.player_id = 0
        self.player_name = ''
        self.team_id = 0
        self.games_used = 0


class PlayerProfileEngine:
    """Build and cache player profiles from game log data."""

    DECAY = 0.93          # exponential decay per game (recent games weighted more)
    WINDOW = 20           # rolling window size
    MIN_GAMES = 3         # minimum games to build a profile
    TEAM_MINUTES = 240.0  # 5 players × 48 min

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._game_logs: Optional[pd.DataFrame] = None
        # Cache: (player_id, team_id, date_str) -> PlayerProfile
        self._cache: Dict[Tuple[int, int, str], Optional[PlayerProfile]] = {}

    def _load_game_logs(self):
        """Load all player game logs, sorted by date."""
        if self._game_logs is not None:
            return
        con = duckdb.connect(self.db_path, read_only=True)
        df = con.execute("""
            SELECT
                p.player_id, p.player_name, p.team_id,
                p.game_id, p.game_date, p.season,
                p.min, p.fgm, p.fga, p.fg3m, p.fg3a,
                p.ftm, p.fta, p.pts, p.reb, p.ast,
                p.stl, p.blk, p.tov, p.pf, p.plus_minus
            FROM player_game_log p
            JOIN game g ON p.game_id = g.game_id
            WHERE g.season_type = 'Regular Season'
              AND p.min IS NOT NULL AND p.min > 0
            ORDER BY p.game_date, p.game_id
        """).fetchdf()
        df['game_date'] = pd.to_datetime(df['game_date'])
        df['player_id'] = df['player_id'].astype(int)
        df['team_id'] = df['team_id'].astype(int)
        self._game_logs = df
        con.close()

    def get_profile(self, player_id: int, team_id: int,
                    before_date: pd.Timestamp) -> Optional[PlayerProfile]:
        """Get a player's rolling profile using only games before the given date.

        Handles trade scenarios: if player has < 10 games with current team,
        blends current-team stats with career stats as a prior.
        """
        date_key = before_date.strftime('%Y-%m-%d')
        cache_key = (player_id, team_id, date_key)
        if cache_key in self._cache:
            return self._cache[cache_key]

        self._load_game_logs()
        gl = self._game_logs

        # All games for this player before the date
        player_all = gl[
            (gl['player_id'] == player_id) &
            (gl['game_date'] < before_date)
        ]

        if len(player_all) < self.MIN_GAMES:
            self._cache[cache_key] = None
            return None

        # Games with current team
        player_team = player_all[player_all['team_id'] == team_id]

        # Trade handling: blend with career if < 10 games with team
        if len(player_team) >= 10:
            games = player_team.sort_values('game_date', ascending=False).head(self.WINDOW)
        elif len(player_team) >= self.MIN_GAMES:
            # Use team games + fill remaining window from career
            team_games = player_team.sort_values('game_date', ascending=False)
            remaining = self.WINDOW - len(team_games)
            career_games = player_all[
                player_all['team_id'] != team_id
            ].sort_values('game_date', ascending=False).head(remaining)
            games = pd.concat([team_games, career_games]).sort_values(
                'game_date', ascending=False
            ).head(self.WINDOW)
        else:
            # Not enough with this team — use all career games
            games = player_all.sort_values('game_date', ascending=False).head(self.WINDOW)

        n = len(games)
        if n < self.MIN_GAMES:
            self._cache[cache_key] = None
            return None

        # Exponential decay weights (index 0 = most recent)
        weights = np.array([self.DECAY ** i for i in range(n)])
        weights /= weights.sum()

        vals = games[['min', 'pts', 'reb', 'ast', 'stl', 'blk',
                       'fga', 'fta', 'tov', 'plus_minus', 'fgm', 'ftm',
                       'fg3a', 'fg3m']].values.astype(float)

        mins = vals[:, 0]
        pts = vals[:, 1]
        reb = vals[:, 2]
        ast = vals[:, 3]
        stl = vals[:, 4]
        blk = vals[:, 5]
        fga = vals[:, 6]
        fta = vals[:, 7]
        tov_arr = vals[:, 8]
        pm = vals[:, 9]
        fgm = vals[:, 10]
        ftm = vals[:, 11]
        fg3a = vals[:, 12]

        profile = PlayerProfile()
        profile.player_id = player_id
        profile.player_name = games.iloc[0]['player_name']
        profile.team_id = team_id
        profile.games_used = n

        profile.ppg = np.dot(weights, pts)
        profile.rpg = np.dot(weights, reb)
        profile.apg = np.dot(weights, ast)
        profile.spg = np.dot(weights, stl)
        profile.bpg = np.dot(weights, blk)
        profile.mpg = np.dot(weights, mins)
        profile.fga_pg = np.dot(weights, fga)
        profile.fta_pg = np.dot(weights, fta)
        profile.tov_pg = np.dot(weights, tov_arr)
        profile.plus_minus_pg = np.dot(weights, pm)
        profile.fg3a_pg = np.dot(weights, fg3a)

        # Usage rate proxy: (FGA + 0.44*FTA + TOV) per minute
        poss_used = fga + 0.44 * fta + tov_arr
        total_min = np.dot(weights, mins)
        if total_min > 0:
            profile.usage_rate = np.dot(weights, poss_used) / total_min
        else:
            profile.usage_rate = 0.0

        # True Shooting %: PTS / (2 * (FGA + 0.44 * FTA))
        total_pts = np.dot(weights, pts)
        total_tsa = np.dot(weights, 2 * (fga + 0.44 * fta))
        profile.ts_pct = total_pts / total_tsa if total_tsa > 0 else 0.0

        # Points per possession used
        total_poss_used = np.dot(weights, poss_used)
        profile.pts_per_poss = total_pts / total_poss_used if total_poss_used > 0 else 0.0

        # Minutes share (% of team total of 240)
        profile.minutes_share = profile.mpg / self.TEAM_MINUTES

        self._cache[cache_key] = profile
        return profile

    def get_team_profiles(self, team_id: int, before_date: pd.Timestamp,
                          top_n: int = 15) -> list:
        """Get profiles for a team's recent rotation players.

        Returns list of PlayerProfile for the top_n players by minutes
        who have played for this team recently.
        """
        self._load_game_logs()
        gl = self._game_logs

        # Find players who played for this team in last 30 days
        cutoff = before_date - pd.Timedelta(days=60)
        recent = gl[
            (gl['team_id'] == team_id) &
            (gl['game_date'] < before_date) &
            (gl['game_date'] >= cutoff)
        ]

        if recent.empty:
            return []

        # Get unique players sorted by total minutes
        player_mins = recent.groupby('player_id')['min'].sum().sort_values(ascending=False)
        top_players = player_mins.head(top_n).index.tolist()

        profiles = []
        for pid in top_players:
            p = self.get_profile(pid, team_id, before_date)
            if p is not None:
                profiles.append(p)

        return profiles

    def clear_cache(self):
        self._cache.clear()
