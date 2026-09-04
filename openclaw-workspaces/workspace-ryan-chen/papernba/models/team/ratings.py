"""
Team Ratings Engine
===================

Calculates per-season and rolling team ratings from the game table:
- Offensive Rating (points scored per 100 possessions)
- Defensive Rating (points allowed per 100 possessions)
- Pace (possessions per game)

Possession estimation: FGA - OREB + TOV + 0.44 * FTA
"""

import duckdb
import pandas as pd
import numpy as np
from typing import Optional


def estimate_possessions(fga: float, oreb: float, tov: float, fta: float) -> float:
    """Estimate possessions using the standard NBA formula."""
    return fga - oreb + tov + 0.44 * fta


class TeamRatings:
    """Calculate and cache team ratings from game data."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._game_log: Optional[pd.DataFrame] = None

    def _get_connection(self) -> duckdb.DuckDBPyConnection:
        return duckdb.connect(self.db_path, read_only=True)

    def _load_game_log(self) -> pd.DataFrame:
        """Load all regular season games into a normalized long-format DataFrame.
        
        Each row = one team's performance in one game, with columns:
        team_id, opp_id, game_date, season_id, is_home, pts, opp_pts,
        fga, oreb, tov, fta, opp_fga, opp_oreb, opp_tov, opp_fta
        """
        if self._game_log is not None:
            return self._game_log

        con = self._get_connection()
        df = con.execute("""
            SELECT game_id, game_date, season_id,
                   team_id_home, team_id_away,
                   pts_home, pts_away,
                   fga_home, oreb_home, tov_home, fta_home,
                   fga_away, oreb_away, tov_away, fta_away
            FROM game
            WHERE season_type = 'Regular Season'
              AND pts_home IS NOT NULL AND pts_away IS NOT NULL
            ORDER BY game_date
        """).fetchdf()
        con.close()

        # Build home rows
        home = pd.DataFrame({
            'game_id': df['game_id'],
            'team_id': df['team_id_home'],
            'opp_id': df['team_id_away'],
            'game_date': pd.to_datetime(df['game_date']),
            'season_id': df['season_id'],
            'is_home': True,
            'pts': df['pts_home'],
            'opp_pts': df['pts_away'],
            'fga': df['fga_home'],
            'oreb': df['oreb_home'],
            'tov': df['tov_home'],
            'fta': df['fta_home'],
            'opp_fga': df['fga_away'],
            'opp_oreb': df['oreb_away'],
            'opp_tov': df['tov_away'],
            'opp_fta': df['fta_away'],
        })

        # Build away rows
        away = pd.DataFrame({
            'game_id': df['game_id'],
            'team_id': df['team_id_away'],
            'opp_id': df['team_id_home'],
            'game_date': pd.to_datetime(df['game_date']),
            'season_id': df['season_id'],
            'is_home': False,
            'pts': df['pts_away'],
            'opp_pts': df['pts_home'],
            'fga': df['fga_away'],
            'oreb': df['oreb_away'],
            'tov': df['tov_away'],
            'fta': df['fta_away'],
            'opp_fga': df['fga_home'],
            'opp_oreb': df['oreb_home'],
            'opp_tov': df['tov_home'],
            'opp_fta': df['fta_home'],
        })

        game_log = pd.concat([home, away], ignore_index=True).sort_values('game_date').reset_index(drop=True)
        self._game_log = game_log
        return game_log

    def season_ratings(self, season_id: str) -> pd.DataFrame:
        """Calculate full-season ratings for all teams in a given season.
        
        Returns DataFrame with columns:
        team_id, off_rtg, def_rtg, net_rtg, pace, games
        """
        gl = self._load_game_log()
        sg = gl[gl['season_id'] == season_id].copy()

        if sg.empty:
            return pd.DataFrame(columns=['team_id', 'off_rtg', 'def_rtg', 'net_rtg', 'pace', 'games'])

        sg['poss'] = sg.apply(lambda r: estimate_possessions(r['fga'], r['oreb'], r['tov'], r['fta']), axis=1)
        sg['opp_poss'] = sg.apply(lambda r: estimate_possessions(r['opp_fga'], r['opp_oreb'], r['opp_tov'], r['opp_fta']), axis=1)

        grouped = sg.groupby('team_id').agg(
            pts=('pts', 'sum'),
            opp_pts=('opp_pts', 'sum'),
            poss=('poss', 'sum'),
            opp_poss=('opp_poss', 'sum'),
            games=('game_id', 'count'),
        ).reset_index()

        grouped['off_rtg'] = grouped['pts'] / grouped['poss'] * 100
        grouped['def_rtg'] = grouped['opp_pts'] / grouped['opp_poss'] * 100
        grouped['net_rtg'] = grouped['off_rtg'] - grouped['def_rtg']
        grouped['pace'] = (grouped['poss'] + grouped['opp_poss']) / 2 / grouped['games']

        return grouped[['team_id', 'off_rtg', 'def_rtg', 'net_rtg', 'pace', 'games']]

    def league_average(self, season_id: str) -> dict:
        """Calculate league-average offensive rating and pace for a season."""
        ratings = self.season_ratings(season_id)
        if ratings.empty:
            return {'off_rtg': 110.0, 'def_rtg': 110.0, 'pace': 98.0}
        return {
            'off_rtg': ratings['off_rtg'].mean(),
            'def_rtg': ratings['def_rtg'].mean(),
            'pace': ratings['pace'].mean(),
        }

    def rolling_ratings(self, team_id: str, before_date: pd.Timestamp,
                        n_games: int = 20, decay: float = 0.95) -> Optional[dict]:
        """Calculate rolling ratings for a team using exponential decay weighting.
        
        Uses the last `n_games` before `before_date` with exponential decay
        so recent games are weighted more heavily.
        
        Args:
            team_id: NBA team ID
            before_date: Only use games strictly before this date
            n_games: Number of recent games to consider
            decay: Exponential decay factor (0.95 = most recent game weight 1.0,
                   previous game 0.95, etc.)
        
        Returns:
            dict with off_rtg, def_rtg, pace, games_used or None if insufficient data
        """
        gl = self._load_game_log()
        team_games = gl[(gl['team_id'] == team_id) & (gl['game_date'] < before_date)].copy()
        team_games = team_games.sort_values('game_date', ascending=False).head(n_games)

        if len(team_games) < 5:
            return None

        team_games['poss'] = team_games.apply(
            lambda r: estimate_possessions(r['fga'], r['oreb'], r['tov'], r['fta']), axis=1)
        team_games['opp_poss'] = team_games.apply(
            lambda r: estimate_possessions(r['opp_fga'], r['opp_oreb'], r['opp_tov'], r['opp_fta']), axis=1)

        # Exponential decay weights: most recent game = 1.0
        n = len(team_games)
        weights = np.array([decay ** i for i in range(n)])
        weights /= weights.sum()

        off_rtg = np.average(team_games['pts'].values / team_games['poss'].values * 100, weights=weights)
        def_rtg = np.average(team_games['opp_pts'].values / team_games['opp_poss'].values * 100, weights=weights)
        pace = np.average(
            (team_games['poss'].values + team_games['opp_poss'].values) / 2,
            weights=weights
        )

        return {
            'off_rtg': off_rtg,
            'def_rtg': def_rtg,
            'net_rtg': off_rtg - def_rtg,
            'pace': pace,
            'games_used': n,
        }

    def get_team_rating_before_date(self, team_id: str, before_date: pd.Timestamp,
                                     season_id: str, blend_weight: float = 0.6) -> Optional[dict]:
        """Get blended team rating using rolling + season-to-date data.
        
        Blends rolling (recent form) with season-to-date (full sample) ratings.
        blend_weight controls how much weight goes to rolling (default 0.6 = 60% rolling).
        
        Falls back to season-to-date only, or prior season if early in season.
        """
        # Rolling rating (recent form)
        rolling = self.rolling_ratings(team_id, before_date, n_games=20, decay=0.95)

        # Season-to-date rating
        gl = self._load_game_log()
        season_games = gl[
            (gl['team_id'] == team_id) &
            (gl['season_id'] == season_id) &
            (gl['game_date'] < before_date)
        ].copy()

        std_rating = None
        if len(season_games) >= 5:
            season_games['poss'] = season_games.apply(
                lambda r: estimate_possessions(r['fga'], r['oreb'], r['tov'], r['fta']), axis=1)
            season_games['opp_poss'] = season_games.apply(
                lambda r: estimate_possessions(r['opp_fga'], r['opp_oreb'], r['opp_tov'], r['opp_fta']), axis=1)
            total_pts = season_games['pts'].sum()
            total_opp = season_games['opp_pts'].sum()
            total_poss = season_games['poss'].sum()
            total_opp_poss = season_games['opp_poss'].sum()
            n = len(season_games)
            std_rating = {
                'off_rtg': total_pts / total_poss * 100,
                'def_rtg': total_opp / total_opp_poss * 100,
                'pace': (total_poss + total_opp_poss) / 2 / n,
                'games_used': n,
            }

        if rolling and std_rating:
            w = blend_weight
            return {
                'off_rtg': w * rolling['off_rtg'] + (1 - w) * std_rating['off_rtg'],
                'def_rtg': w * rolling['def_rtg'] + (1 - w) * std_rating['def_rtg'],
                'pace': w * rolling['pace'] + (1 - w) * std_rating['pace'],
                'games_used': rolling['games_used'],
            }
        elif std_rating:
            return std_rating
        elif rolling:
            return rolling
        else:
            # Fall back to prior season
            # Season IDs are like "22022" -> prior is "22021"
            try:
                year = int(season_id[1:])
                prior_season = f"2{year - 1}"
                prior = self.season_ratings(prior_season)
                team_row = prior[prior['team_id'] == team_id]
                if not team_row.empty:
                    row = team_row.iloc[0]
                    return {
                        'off_rtg': row['off_rtg'],
                        'def_rtg': row['def_rtg'],
                        'pace': row['pace'],
                        'games_used': 0,
                    }
            except (ValueError, IndexError):
                pass
            return None

    def league_average_before_date(self, season_id: str, before_date: pd.Timestamp) -> dict:
        """Calculate league-average ratings using only games before a given date."""
        gl = self._load_game_log()
        sg = gl[(gl['season_id'] == season_id) & (gl['game_date'] < before_date)].copy()

        if len(sg) < 30:
            # Not enough data, use prior season
            try:
                year = int(season_id[1:])
                return self.league_average(f"2{year - 1}")
            except (ValueError, KeyError):
                return {'off_rtg': 110.0, 'def_rtg': 110.0, 'pace': 98.0}

        sg['poss'] = sg.apply(lambda r: estimate_possessions(r['fga'], r['oreb'], r['tov'], r['fta']), axis=1)
        total_pts = sg['pts'].sum()
        total_poss = sg['poss'].sum()
        n_games_total = sg['game_id'].nunique()

        off_rtg = total_pts / total_poss * 100
        pace = total_poss / len(sg)  # per team-game

        return {'off_rtg': off_rtg, 'def_rtg': off_rtg, 'pace': pace}
