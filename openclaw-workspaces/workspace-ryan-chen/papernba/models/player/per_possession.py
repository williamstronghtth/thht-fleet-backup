"""
models/player/per_possession.py — Per-possession player performance model.

Traditional box score stats (PPG, RPG) are noisy because they don't account
for pace or context. Per-possession stats normalize for pace and let us
compare players fairly across different team systems.

Key metrics to compute:
- Points per 100 possessions (individual offensive output)
- Usage rate in context (how does usage change with different lineups?)
- True shooting % by game state (blowout vs close, home vs away)
- Assist-to-turnover ratio under pressure (close games, late clock)
- Defensive impact per possession (DPM-style)
- Fatigue curves (performance vs minutes played in game)

This feeds directly into the lineup chemistry model and game simulator.
"""

import logging
from dataclasses import dataclass

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class PlayerPossessionProfile:
    """Per-possession performance profile for a single player."""
    player_id: int = 0
    player_name: str = ""
    # Offensive
    pts_per_100: float = 0.0
    ts_pct: float = 0.0       # true shooting %
    usage_rate: float = 0.0
    ast_rate: float = 0.0
    tov_rate: float = 0.0
    # Defensive
    def_rating: float = 0.0   # points allowed per 100 possessions
    stl_rate: float = 0.0
    blk_rate: float = 0.0
    # Context splits
    home_pts_per_100: float = 0.0
    away_pts_per_100: float = 0.0
    close_game_ts_pct: float = 0.0  # TS% in games within 5 pts
    # Fatigue
    first_half_pts_per_100: float = 0.0
    second_half_pts_per_100: float = 0.0
    fatigue_dropoff: float = 0.0  # % decline after 30+ minutes


class PerPossessionModel:
    """
    Build per-possession performance profiles for all players.

    Usage:
        model = PerPossessionModel()
        model.fit(player_logs_df, team_pace_df)
        profile = model.get_profile(player_id=203999)
    """

    def __init__(self):
        self.profiles: dict[int, PlayerPossessionProfile] = {}

    def fit(self, player_logs: pd.DataFrame, team_stats: pd.DataFrame,
            season: str = "") -> int:
        """
        Build per-possession profiles from game log data.

        TODO:
        1. Estimate possessions per game using the four-factor formula:
           POSS ≈ FGA - OREB + TOV + 0.44 * FTA
        2. Normalize all counting stats to per-100-possession rates
        3. Calculate true shooting %: PTS / (2 * (FGA + 0.44 * FTA))
        4. Compute usage rate: 100 * (FGA + 0.44*FTA + TOV) * (TmMIN/5) / (MIN * TmPOSS)
        5. Build context splits (home/away, close/blowout)
        6. Detect fatigue curves by comparing 1st half vs 2nd half stats
        7. Calculate rolling averages (last 10, 20, full season)

        Parameters
        ----------
        player_logs : pd.DataFrame
            Individual game log data with box score stats.
        team_stats : pd.DataFrame
            Team-level stats for pace normalization.
        season : str
            Season label.

        Returns
        -------
        int
            Number of player profiles built.
        """
        logger.info("Fitting per-possession model for %d player games", len(player_logs))

        # TODO: Implement per-possession calculations
        # Key columns expected: player_id, min, fgm, fga, fg3m, fg3a,
        # ftm, fta, oreb, dreb, reb, ast, stl, blk, tov, pf, pts,
        # plus_minus, game_id, matchup (for home/away)

        return len(self.profiles)

    def get_profile(self, player_id: int) -> PlayerPossessionProfile | None:
        """Get a player's per-possession profile."""
        return self.profiles.get(player_id)

    def get_rolling_stats(self, player_id: int, window: int = 10) -> dict:
        """
        Get rolling per-possession stats for recent games.

        TODO: More recent games should be weighted more heavily.
        Return dict with rolling averages for key metrics.
        """
        # TODO: Implement rolling window calculations
        return {}

    def compare_players(self, player_ids: list[int]) -> pd.DataFrame:
        """
        Compare per-possession profiles for multiple players.

        Useful for evaluating replacement-level impact when a player
        is injured or in foul trouble.
        """
        rows = []
        for pid in player_ids:
            p = self.profiles.get(pid)
            if p:
                rows.append({
                    "player_id": p.player_id,
                    "player_name": p.player_name,
                    "pts_per_100": p.pts_per_100,
                    "ts_pct": p.ts_pct,
                    "usage_rate": p.usage_rate,
                    "def_rating": p.def_rating,
                })
        return pd.DataFrame(rows)
