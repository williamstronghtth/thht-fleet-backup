"""
Player Impact Estimator v2
==========================

Estimates scoring impact when players are absent using individual game log data.

Approach:
1. Build rolling player profiles from game logs (via PlayerProfileEngine)
2. Estimate production loss = player's rolling PPG × (1 - replacement_factor)
3. Weight by minutes share — stars matter more than bench players
4. Multi-player absence compounds (team gets worse faster)
5. Blend stats-based estimate with observed team differential (Bayesian)
6. Cap adjustments at reasonable bounds

Key insight: when a player is out, ~40-60% of their production is replaced
by teammates who see increased minutes/usage. The NET loss is smaller
than the raw PPG suggests.
"""

import duckdb
import pandas as pd
import numpy as np
from typing import Optional, Dict, Tuple, List
from .profile import PlayerProfileEngine, PlayerProfile


class PlayerImpactModel:
    """Estimate game adjustments based on player availability using individual stats."""

    # Replacement factor: fraction of missing player's production that gets replaced
    # by teammates stepping up. 1.0 = fully replaced (no impact), 0.0 = total loss.
    REPLACEMENT_FACTOR = 0.5

    # Maximum impact for a single player (points)
    MAX_SINGLE_IMPACT = 8.0
    # Maximum total team adjustment (points)
    MAX_TEAM_IMPACT = 12.0

    # Bayesian shrinkage for observed differential
    SHRINKAGE_K = 15  # games needed before observed diff gets full weight
    # Blend weight for stats-based vs observed (at full shrinkage)
    STATS_WEIGHT = 0.6  # 60% stats-based, 40% observed

    # Multi-player compounding factor
    # When N players are out, total impact = sum of individual × (1 + COMPOUND * (N-1))
    COMPOUND_FACTOR = 0.05

    # Minimum minutes per game to consider a player impactful
    # Only starters and key rotation players — having bench guys inactive is normal
    MIN_MPG = 20.0

    # Residual discount: baseline team ratings already partly capture absences
    # (because absences affect team performance which feeds into rolling ratings).
    # This factor scales down our adjustment to only capture the RESIDUAL signal.
    RESIDUAL_DISCOUNT = 0.10

    def __init__(self, db_path: str, replacement_factor: float = 0.5):
        self.db_path = db_path
        self.REPLACEMENT_FACTOR = replacement_factor
        self.profile_engine = PlayerProfileEngine(db_path)
        self._game_data: Optional[pd.DataFrame] = None
        self._inactive_data: Optional[pd.DataFrame] = None
        # Cache: (player_id, team_id, date_str) -> impact_score
        self._impact_cache: Dict[Tuple, float] = {}
        # Cache: (player_id, team_id, date_str) -> observed_diff
        self._observed_cache: Dict[Tuple, Tuple[float, int]] = {}

    def _load_data(self):
        """Load game and inactive data for observed differential calculations."""
        if self._game_data is not None:
            return
        con = duckdb.connect(self.db_path, read_only=True)

        df = con.execute("""
            SELECT game_id, game_date, season_id,
                   team_id_home, team_id_away,
                   pts_home, pts_away
            FROM game
            WHERE season_type = 'Regular Season'
              AND pts_home IS NOT NULL
            ORDER BY game_date
        """).fetchdf()
        df['game_date'] = pd.to_datetime(df['game_date'])

        # Long format: one row per team per game
        home = pd.DataFrame({
            'game_id': df['game_id'], 'team_id': df['team_id_home'].astype(str),
            'game_date': df['game_date'], 'season_id': df['season_id'],
            'margin': df['pts_home'] - df['pts_away'],
        })
        away = pd.DataFrame({
            'game_id': df['game_id'], 'team_id': df['team_id_away'].astype(str),
            'game_date': df['game_date'], 'season_id': df['season_id'],
            'margin': df['pts_away'] - df['pts_home'],
        })
        self._game_data = pd.concat([home, away], ignore_index=True)

        # Inactive players
        inactive = con.execute("""
            SELECT i.game_id, i.player_id, i.team_id,
                   g.game_date, g.season_id
            FROM inactive_players i
            JOIN game g ON i.game_id = g.game_id
            WHERE g.season_type = 'Regular Season'
              AND g.pts_home IS NOT NULL
        """).fetchdf()
        inactive['game_date'] = pd.to_datetime(inactive['game_date'])
        self._inactive_data = inactive
        con.close()

    def _compute_observed_differential(self, player_id: str, team_id: str,
                                        before_date: pd.Timestamp) -> Tuple[float, int]:
        """Compare team margin with vs without this player.

        Returns (margin_differential, n_games_absent).
        Negative differential = team worse without this player.
        """
        cache_key = (player_id, team_id, before_date.strftime('%Y-%m-%d'))
        if cache_key in self._observed_cache:
            return self._observed_cache[cache_key]

        self._load_data()
        gd = self._game_data
        inactive = self._inactive_data

        # Team games before date
        team_games = gd[
            (gd['team_id'] == team_id) &
            (gd['game_date'] < before_date)
        ]
        # Last 2 seasons of data
        if len(team_games) > 164:  # ~2 seasons
            team_games = team_games.sort_values('game_date', ascending=False).head(164)

        if len(team_games) < 20:
            self._observed_cache[cache_key] = (0.0, 0)
            return (0.0, 0)

        # Games where player was absent
        absent_game_ids = set(
            inactive[
                (inactive['player_id'] == player_id) &
                (inactive['team_id'] == team_id) &
                (inactive['game_date'] < before_date)
            ]['game_id'].values
        )

        games_without = team_games[team_games['game_id'].isin(absent_game_ids)]
        games_with = team_games[~team_games['game_id'].isin(absent_game_ids)]

        n_without = len(games_without)
        if n_without < 3 or len(games_with) < 10:
            self._observed_cache[cache_key] = (0.0, 0)
            return (0.0, 0)

        diff = games_without['margin'].mean() - games_with['margin'].mean()
        self._observed_cache[cache_key] = (diff, n_without)
        return (diff, n_without)

    def estimate_player_impact(self, player_id_str: str, team_id_str: str,
                                before_date: pd.Timestamp) -> float:
        """Estimate points impact of a single player being absent.

        Returns a negative number (team scores fewer points without this player).
        Blends stats-based estimate with observed team differential.
        """
        cache_key = (player_id_str, team_id_str, before_date.strftime('%Y-%m-%d'))
        if cache_key in self._impact_cache:
            return self._impact_cache[cache_key]

        # Get player profile
        try:
            pid = int(player_id_str)
            tid = int(team_id_str)
        except (ValueError, TypeError):
            self._impact_cache[cache_key] = 0.0
            return 0.0

        profile = self.profile_engine.get_profile(pid, tid, before_date)

        if profile is None or profile.mpg < self.MIN_MPG:
            # Below rotation threshold — negligible impact
            self._impact_cache[cache_key] = 0.0
            return 0.0

        # Stats-based estimate
        # Base production loss = PPG × (1 - replacement_factor)
        base_loss = profile.ppg * (1 - self.REPLACEMENT_FACTOR)

        # Scale by minutes importance: players with higher minutes share
        # are harder to replace (bench is deeper than starters)
        # minutes_share ranges from ~0.05 (bench) to ~0.15 (star)
        # Scale factor: 1.0 at 30 MPG, higher for 35+, lower for 15
        minutes_scale = min(profile.mpg / 30.0, 1.5)

        # Efficiency adjustment: inefficient players' absence hurts less
        # TS% league avg ~0.56. Below avg = less damaging to lose
        ts_factor = 1.0
        if profile.ts_pct > 0:
            ts_factor = min(max(profile.ts_pct / 0.56, 0.7), 1.3)

        stats_impact = -base_loss * minutes_scale * ts_factor

        # Observed team differential (Bayesian blend)
        observed_diff, n_absent = self._compute_observed_differential(
            player_id_str, team_id_str, before_date
        )

        if n_absent >= 3:
            # Shrinkage: observed diff only gets full weight with enough data
            shrinkage = n_absent / (n_absent + self.SHRINKAGE_K)
            # Blend: stats-based + observed (weighted by shrinkage)
            blend_obs_weight = (1 - self.STATS_WEIGHT) * shrinkage
            blend_stats_weight = 1 - blend_obs_weight
            # Observed diff is margin diff (negative = team worse without)
            # Convert to scoring impact: roughly half the margin change
            # comes from scoring (rest from defense/pace changes)
            obs_scoring_impact = observed_diff * 0.5
            impact = blend_stats_weight * stats_impact + blend_obs_weight * obs_scoring_impact
        else:
            impact = stats_impact

        # Apply residual discount: baseline already captures some absence effect
        impact *= self.RESIDUAL_DISCOUNT

        # Cap single player impact
        impact = max(impact, -self.MAX_SINGLE_IMPACT)
        impact = min(impact, 0.0)  # absence shouldn't help the team

        self._impact_cache[cache_key] = impact
        return impact

    def get_team_adjustment(self, team_id: str, inactive_player_ids: List[str],
                            before_date: pd.Timestamp) -> float:
        """Get total scoring adjustment for a team with multiple players out.

        Returns negative number = team expected to score fewer points.
        Accounts for compounding effect when multiple players are out.
        """
        if not inactive_player_ids:
            return 0.0

        individual_impacts = []
        for pid in inactive_player_ids:
            impact = self.estimate_player_impact(pid, team_id, before_date)
            if impact < 0:
                individual_impacts.append(impact)

        if not individual_impacts:
            return 0.0

        # Sort by magnitude (biggest impact first)
        individual_impacts.sort()  # most negative first

        # Sum with compounding: each additional absence multiplies effect
        n = len(individual_impacts)
        base_total = sum(individual_impacts)

        if n > 1:
            compound = 1.0 + self.COMPOUND_FACTOR * (n - 1)
            total = base_total * compound
        else:
            total = base_total

        # Cap total team adjustment
        total = max(total, -self.MAX_TEAM_IMPACT)

        return total

    def get_count_based_adjustment(self, home_inactive_count: int,
                                    away_inactive_count: int,
                                    game_date: pd.Timestamp,
                                    season_id: str) -> float:
        """Legacy API: count-based adjustment for backward compatibility.

        In v2, this is replaced by per-player impact estimation,
        but we keep this for the predictor's existing call path.
        """
        # Simple fallback: ~-0.35 per inactive differential
        inactive_diff = home_inactive_count - away_inactive_count
        return -0.35 * inactive_diff

    def get_player_value_ranking(self, before_date: pd.Timestamp,
                                  min_games: int = 20,
                                  top_n: int = 50) -> pd.DataFrame:
        """Rank players by estimated impact of their absence.

        Combines stats-based impact with observed team differential.
        Returns DataFrame with player rankings.
        """
        self._load_data()
        self.profile_engine._load_game_logs()

        gl = self.profile_engine._game_logs
        # Find active players (played in last 90 days before the date)
        cutoff = before_date - pd.Timedelta(days=90)
        recent = gl[
            (gl['game_date'] < before_date) &
            (gl['game_date'] >= cutoff) &
            (gl['min'] > 0)
        ]

        # Get unique player-team combos with enough games
        player_teams = recent.groupby(['player_id', 'team_id']).agg(
            games=('game_id', 'count'),
            player_name=('player_name', 'first'),
        ).reset_index()
        player_teams = player_teams[player_teams['games'] >= min_games]

        rows = []
        for _, pt in player_teams.iterrows():
            pid = int(pt['player_id'])
            tid = int(pt['team_id'])
            pid_str = str(pid)
            tid_str = str(tid)

            profile = self.profile_engine.get_profile(pid, tid, before_date)
            if profile is None or profile.mpg < 10:
                continue

            impact = self.estimate_player_impact(pid_str, tid_str, before_date)
            obs_diff, n_absent = self._compute_observed_differential(
                pid_str, tid_str, before_date
            )

            # Tier classification by MPG
            if profile.mpg >= 32:
                tier = 'Star'
            elif profile.mpg >= 24:
                tier = 'Starter'
            elif profile.mpg >= 15:
                tier = 'Rotation'
            else:
                tier = 'Bench'

            rows.append({
                'player_id': pid,
                'player_name': profile.player_name,
                'team_id': tid,
                'ppg': round(profile.ppg, 1),
                'mpg': round(profile.mpg, 1),
                'ts_pct': round(profile.ts_pct, 3),
                'usage_rate': round(profile.usage_rate, 3),
                'impact_pts': round(impact, 2),
                'observed_diff': round(obs_diff, 2) if n_absent >= 3 else None,
                'n_games_absent': n_absent,
                'tier': tier,
                'games_played': pt['games'],
            })

        df = pd.DataFrame(rows)
        if df.empty:
            return df
        return df.sort_values('impact_pts').head(top_n).reset_index(drop=True)

    def clear_cache(self):
        self._impact_cache.clear()
        self._observed_cache.clear()
        self.profile_engine.clear_cache()
