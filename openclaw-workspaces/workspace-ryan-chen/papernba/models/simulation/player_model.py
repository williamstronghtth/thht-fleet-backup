"""
Player Possession Model
========================

For each player, calculates per-possession tendencies from game logs.
Everything is denominated in possessions — not minutes, not games.

Two-layer approach:
  1. Career baseline (Bayesian prior) — all games for this player
  2. Recent form (20-game rolling window with exponential decay)
  3. Blend via Bayesian shrinkage: more recent data = more weight on recent,
     less data = lean on career baseline. Rookies with no career data
     get shrunk toward league averages.

Walk-forward safe: only uses data before the game date.
"""

import duckdb
import pandas as pd
import numpy as np
from typing import Optional, Dict, Tuple, List
from dataclasses import dataclass, field


# ================================================================
# League-wide averages (2022-23 season) used as ultimate prior
# for players with insufficient career data
# ================================================================
LEAGUE_AVG = {
    'fg2_pct': 0.552,
    'fg3_pct': 0.366,
    'ft_pct': 0.783,
    'turnover_rate': 0.137,
    'foul_drawn_rate': 0.12,
    'two_pt_rate': 0.61,
    'three_pt_rate': 0.39,
    'possession_share': 0.20,
    'oreb_rate': 0.228,
    'pf_per_poss': 0.04,
    'assist_rate': 0.29,
    # Counting stat rates
    'stl_per_poss': 0.015,
    'blk_per_poss': 0.012,
    'dreb_rate': 0.15,
    'ast_pct': 0.15,
    # Defensive averages (what opponents shoot against league avg defense)
    'def_fg2_pct_allowed': 0.552,
    'def_fg3_pct_allowed': 0.366,
    'def_tov_forced_rate': 0.137,
    'def_foul_rate': 0.04,
    'def_oreb_allowed_rate': 0.228,
}


@dataclass
class PossessionProfile:
    """Per-possession tendency profile for a single player.
    
    All rates are per-possession, not per-minute or per-game.
    """
    player_id: int
    player_name: str
    team_id: int
    games_used: int = 0
    career_games: int = 0
    mpg: float = 0.0

    # Position slot(s) this player can fill
    position_slots: tuple = ('W',)

    # Possession share (normalized among 5 on-court at sim time)
    possession_share: float = 0.20

    # Outcome tree: Turnover? → Shooting foul? → Shot (2pt or 3pt)
    turnover_rate: float = 0.137
    foul_drawn_rate: float = 0.12
    two_pt_rate: float = 0.61
    three_pt_rate: float = 0.39
    assist_rate: float = 0.29  # tracking only

    # Make probabilities
    fg2_pct: float = 0.552
    fg3_pct: float = 0.366
    ft_pct: float = 0.783

    # OREB rate per missed shot (averaged across lineup at sim time)
    oreb_rate: float = 0.228

    # Fouls per possession
    pf_per_poss: float = 0.04

    # Assist target weight
    assist_target_weight: float = 1.0

    # And-1 rate: % of made FGs that result in and-1 free throw
    and1_rate: float = 0.05        # league avg ~5-6%, Giannis ~13%

    # 3-point foul rate: % of shooting fouls that are 3-shot fouls
    three_pt_foul_rate: float = 0.15  # based on player's 3PA share

    # Possession tempo: average seconds this player uses per possession
    poss_tempo_seconds: float = 13.0  # league avg ~13s, Embiid ~15, Adams ~11

    # ============================================================
    # COUNTING STAT RATES (per-minute for rebounds, per-possession for others)
    # ============================================================
    stl_per_poss: float = 0.015          # steals per defensive possession
    blk_per_poss: float = 0.012          # blocks per opponent FGA
    dreb_rate: float = 0.15              # share of available defensive rebounds
    ast_pct: float = 0.15                # % of teammate FGM assisted by this player

    # ============================================================
    # DEFENSIVE PROFILE
    # What opponents produce when this player is on the court.
    # Averaged across the 5-man lineup at sim time, then blended
    # with the offensive player's profile to get effective rates.
    # ============================================================
    def_fg2_pct_allowed: float = 0.552    # opponent 2pt% when this player plays
    def_fg3_pct_allowed: float = 0.366    # opponent 3pt% when this player plays
    def_tov_forced_rate: float = 0.137    # opponent TOV rate when this player plays
    def_foul_rate: float = 0.04           # fouls this player commits per possession
    def_oreb_allowed_rate: float = 0.228  # opponent OREB rate when this player plays

    @property
    def usage_per_min(self):
        return self.possession_share

    @property
    def pf_per_min(self):
        return self.pf_per_poss


class PlayerPossessionModel:
    """Build per-possession profiles with Bayesian career priors."""

    # All tunable params imported from settings.py
    from . import settings as _s
    DECAY = _s.DECAY
    WINDOW = _s.WINDOW
    MIN_GAMES = _s.MIN_GAMES
    PRIOR_FGA = _s.PRIOR_FGA
    PRIOR_FTA = _s.PRIOR_FTA
    PRIOR_POSS = _s.PRIOR_POSS

    POSITION_MAP = {
        'Guard':           ('G',),
        'Forward':         ('W',),
        'Center':          ('C',),
        'Guard-Forward':   ('G', 'W'),
        'Forward-Guard':   ('G', 'W'),
        'Forward-Center':  ('W', 'C'),
        'Center-Forward':  ('W', 'C'),
    }

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._game_logs: Optional[pd.DataFrame] = None
        self._team_poss: Optional[pd.DataFrame] = None
        self._positions: Optional[Dict[int, tuple]] = None
        self._cache: Dict[Tuple[int, int, str], Optional[PossessionProfile]] = {}

    def _load_data(self):
        """Load player game logs and team-level possession estimates."""
        if self._game_logs is not None:
            return

        con = duckdb.connect(self.db_path, read_only=True)

        df = con.execute("""
            SELECT
                p.player_id, p.player_name, p.team_id,
                p.game_id, p.game_date, p.season,
                p.min, p.fgm, p.fga, p.fg3m, p.fg3a,
                p.ftm, p.fta, p.pts, p.oreb, p.dreb, p.reb,
                p.ast, p.stl, p.blk, p.tov, p.pf
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

        # Player positions
        pos_df = con.execute("""
            SELECT person_id as player_id, position
            FROM common_player_info
            WHERE position IS NOT NULL AND position != ''
        """).fetchdf()
        self._positions = {}
        for _, row in pos_df.iterrows():
            self._positions[int(row['player_id'])] = self.POSITION_MAP.get(
                row['position'], ('W',))
        del pos_df

        # And-1 counts per player (from PBP "Free Throw 1 of 1")
        and1_df = con.execute("""
            SELECT player1_id as player_id, COUNT(*) as and1_count
            FROM play_by_play
            WHERE eventmsgtype = 3
            AND (homedescription LIKE '%1 of 1%' OR visitordescription LIKE '%1 of 1%')
            AND game_id IN (SELECT game_id FROM game WHERE season_type = 'Regular Season')
            AND player1_id IS NOT NULL
            GROUP BY player1_id
        """).fetchdf()
        self._and1_counts = dict(zip(
            and1_df['player_id'].astype(int),
            and1_df['and1_count'].astype(int)
        ))
        del and1_df

        # 3-shot foul counts per player (from PBP "X of 3" FTs)
        three_shot_df = con.execute("""
            SELECT player1_id as player_id, COUNT(*) as three_shot_count
            FROM play_by_play
            WHERE eventmsgtype = 3
            AND (homedescription LIKE '%of 3%' OR visitordescription LIKE '%of 3%')
            AND game_id IN (SELECT game_id FROM game WHERE season_type = 'Regular Season')
            AND player1_id IS NOT NULL
            GROUP BY player1_id
        """).fetchdf()
        self._three_shot_counts = dict(zip(
            three_shot_df['player_id'].astype(int),
            three_shot_df['three_shot_count'].astype(int)
        ))
        del three_shot_df

        # 2-shot foul counts per player
        two_shot_df = con.execute("""
            SELECT player1_id as player_id, COUNT(*) as two_shot_count
            FROM play_by_play
            WHERE eventmsgtype = 3
            AND (homedescription LIKE '%of 2%' OR visitordescription LIKE '%of 2%')
            AND game_id IN (SELECT game_id FROM game WHERE season_type = 'Regular Season')
            AND player1_id IS NOT NULL
            GROUP BY player1_id
        """).fetchdf()
        self._two_shot_counts = dict(zip(
            two_shot_df['player_id'].astype(int),
            two_shot_df['two_shot_count'].astype(int)
        ))
        del two_shot_df

        # Per-player possession tempo from PBP clock data
        poss_tempo_df = con.execute("""
            WITH poss_events AS (
                SELECT game_id, period, eventnum, player1_id,
                    CAST(SPLIT_PART(pctimestring, ':', 1) AS INT) * 60 + 
                    CAST(SPLIT_PART(pctimestring, ':', 2) AS INT) as clock_seconds
                FROM play_by_play
                WHERE eventmsgtype IN (1, 2, 5)
                AND game_id IN (SELECT game_id FROM game WHERE season_type = 'Regular Season')
                AND pctimestring IS NOT NULL AND player1_id IS NOT NULL
            ),
            with_prev AS (
                SELECT *, LAG(clock_seconds) OVER (
                    PARTITION BY game_id, period ORDER BY eventnum
                ) as prev_clock
                FROM poss_events
            )
            SELECT player1_id as player_id,
                   AVG(prev_clock - clock_seconds) as avg_seconds,
                   COUNT(*) as n_poss
            FROM with_prev
            WHERE prev_clock IS NOT NULL
            AND prev_clock - clock_seconds BETWEEN 3 AND 24
            GROUP BY player1_id
            HAVING COUNT(*) > 50
        """).fetchdf()
        self._poss_tempo = dict(zip(
            poss_tempo_df['player_id'].astype(int),
            poss_tempo_df['avg_seconds'].astype(float)
        ))
        del poss_tempo_df

        # Opponent stats per game (for defensive profiles)
        # For each game+team, get what the opponent did offensively
        opp_stats = con.execute("""
            SELECT
                g.game_id,
                g.team_id_home as team_id,
                -- Opponent (away team) offensive stats
                g.fgm_away as opp_fgm, g.fga_away as opp_fga,
                g.fg3m_away as opp_fg3m, g.fg3a_away as opp_fg3a,
                g.tov_away as opp_tov, g.oreb_away as opp_oreb,
                g.fta_away as opp_fta,
                (g.fga_away - g.oreb_away + g.tov_away + 0.44 * g.fta_away) as opp_poss
            FROM game g
            WHERE g.season_type = 'Regular Season'
              AND g.fga_home IS NOT NULL AND g.pts_home IS NOT NULL
            UNION ALL
            SELECT
                g.game_id,
                g.team_id_away as team_id,
                g.fgm_home as opp_fgm, g.fga_home as opp_fga,
                g.fg3m_home as opp_fg3m, g.fg3a_home as opp_fg3a,
                g.tov_home as opp_tov, g.oreb_home as opp_oreb,
                g.fta_home as opp_fta,
                (g.fga_home - g.oreb_home + g.tov_home + 0.44 * g.fta_home) as opp_poss
            FROM game g
            WHERE g.season_type = 'Regular Season'
              AND g.fga_home IS NOT NULL AND g.pts_home IS NOT NULL
        """).fetchdf()
        opp_stats['team_id'] = opp_stats['team_id'].astype(int)
        self._opp_stats = opp_stats

        # Team-level possessions per game
        team_poss = con.execute("""
            SELECT
                game_id, team_id_home, team_id_away,
                (fga_home - oreb_home + tov_home + 0.44 * fta_home) as poss_home,
                (fga_away - oreb_away + tov_away + 0.44 * fta_away) as poss_away
            FROM game
            WHERE season_type = 'Regular Season'
              AND fga_home IS NOT NULL AND pts_home IS NOT NULL
        """).fetchdf()

        home = team_poss[['game_id', 'team_id_home', 'poss_home']].rename(
            columns={'team_id_home': 'team_id', 'poss_home': 'team_poss'})
        away = team_poss[['game_id', 'team_id_away', 'poss_away']].rename(
            columns={'team_id_away': 'team_id', 'poss_away': 'team_poss'})
        self._team_poss = pd.concat([home, away], ignore_index=True)
        self._team_poss['team_id'] = self._team_poss['team_id'].astype(int)

        con.close()

    def _compute_career_baseline(self, player_all: pd.DataFrame) -> Dict[str, float]:
        """Compute career baseline stats from ALL games for a player.
        
        Returns raw totals and counts needed for Bayesian blending.
        """
        total_fga = player_all['fga'].sum()
        total_fgm = player_all['fgm'].sum()
        total_fg3a = player_all['fg3a'].sum()
        total_fg3m = player_all['fg3m'].sum()
        total_fg2a = total_fga - total_fg3a
        total_fg2m = total_fgm - total_fg3m
        total_fta = player_all['fta'].sum()
        total_ftm = player_all['ftm'].sum()
        total_oreb = player_all['oreb'].sum()
        total_ast = player_all['ast'].sum()
        total_tov = player_all['tov'].sum()
        total_pf = player_all['pf'].sum()
        total_min = player_all['min'].sum()
        n_games = len(player_all)

        # Player possessions used
        total_player_poss = total_fga + 0.44 * total_fta + total_tov
        total_non_tov = total_player_poss - total_tov

        return {
            'n_games': n_games,
            'total_fga': total_fga,
            'total_fg2a': total_fg2a,
            'total_fg2m': total_fg2m,
            'total_fg3a': total_fg3a,
            'total_fg3m': total_fg3m,
            'total_fta': total_fta,
            'total_ftm': total_ftm,
            'total_oreb': total_oreb,
            'total_ast': total_ast,
            'total_tov': total_tov,
            'total_pf': total_pf,
            'total_min': total_min,
            'total_player_poss': total_player_poss,
            'total_non_tov': total_non_tov,
            'missed_fga': total_fga - total_fgm,
        }

    def _bayesian_rate(self, recent_makes: float, recent_attempts: float,
                       career_makes: float, career_attempts: float,
                       league_avg: float, prior_strength: float) -> float:
        """Bayesian shrinkage for a rate (e.g., FG%).
        
        Blends three levels:
          1. Recent form (exponential-decay weighted)
          2. Career baseline (all games)
          3. League average (ultimate prior)
        
        The career baseline itself is shrunk toward league average,
        then recent form is blended with the career-shrunk estimate.
        """
        # Step 1: Career estimate shrunk toward league average
        if career_attempts > 0:
            career_rate = career_makes / career_attempts
            career_weight = career_attempts
            # Shrink career toward league avg
            career_shrunk = (
                (career_rate * career_weight + league_avg * prior_strength) /
                (career_weight + prior_strength)
            )
        else:
            career_shrunk = league_avg
            career_weight = 0

        # Step 2: Blend recent form with career-shrunk estimate
        if recent_attempts > 0:
            recent_rate = recent_makes / recent_attempts
            # Weight recent more heavily for larger samples
            # But career acts as a stabilizing anchor
            blend_weight = min(recent_attempts / prior_strength, 1.0)
            blended = career_shrunk * (1.0 - blend_weight) + recent_rate * blend_weight
        else:
            blended = career_shrunk

        return float(blended)

    def get_profile(self, player_id: int, team_id: int,
                    before_date: pd.Timestamp) -> Optional[PossessionProfile]:
        """Get a player's per-possession profile with Bayesian career priors."""
        date_key = before_date.strftime('%Y-%m-%d')
        cache_key = (player_id, team_id, date_key)
        if cache_key in self._cache:
            return self._cache[cache_key]

        self._load_data()
        gl = self._game_logs

        # All games for this player before the date
        player_all = gl[
            (gl['player_id'] == player_id) &
            (gl['game_date'] < before_date)
        ]

        if len(player_all) < self.MIN_GAMES:
            self._cache[cache_key] = None
            return None

        # ============================================================
        # Layer 1: Career baseline (all games before date)
        # ============================================================
        career = self._compute_career_baseline(player_all)

        # ============================================================
        # Layer 2: Recent form (20-game rolling window, decay-weighted)
        # ============================================================
        player_team = player_all[player_all['team_id'] == team_id]

        if len(player_team) >= 10:
            games = player_team.sort_values('game_date', ascending=False).head(self.WINDOW)
        elif len(player_team) >= self.MIN_GAMES:
            team_games = player_team.sort_values('game_date', ascending=False)
            remaining = self.WINDOW - len(team_games)
            career_games = player_all[
                player_all['team_id'] != team_id
            ].sort_values('game_date', ascending=False).head(remaining)
            games = pd.concat([team_games, career_games]).sort_values(
                'game_date', ascending=False
            ).head(self.WINDOW)
        else:
            games = player_all.sort_values('game_date', ascending=False).head(self.WINDOW)

        n = len(games)
        if n < self.MIN_GAMES:
            self._cache[cache_key] = None
            return None

        # Join with team possessions
        games = games.merge(self._team_poss, on=['game_id', 'team_id'], how='left')
        games['team_poss'] = games['team_poss'].fillna(100.0).clip(lower=50.0)

        # Exponential decay weights
        weights = np.array([self.DECAY ** i for i in range(n)])
        weights /= weights.sum()

        # Extract arrays
        mins = games['min'].values.astype(float)
        fga = games['fga'].values.astype(float)
        fgm = games['fgm'].values.astype(float)
        fg3a = games['fg3a'].values.astype(float)
        fg3m = games['fg3m'].values.astype(float)
        fta = games['fta'].values.astype(float)
        ftm = games['ftm'].values.astype(float)
        oreb = games['oreb'].values.astype(float)
        dreb = games['dreb'].values.astype(float) if 'dreb' in games.columns else np.zeros(n)
        ast = games['ast'].values.astype(float)
        stl = games['stl'].values.astype(float) if 'stl' in games.columns else np.zeros(n)
        blk = games['blk'].values.astype(float) if 'blk' in games.columns else np.zeros(n)
        tov = games['tov'].values.astype(float)
        pf = games['pf'].values.astype(float)
        team_poss = games['team_poss'].values.astype(float)

        # Weighted recent stats
        w_min = np.dot(weights, mins)
        w_fga = np.dot(weights, fga)
        w_fgm = np.dot(weights, fgm)
        w_fg3a = np.dot(weights, fg3a)
        w_fg3m = np.dot(weights, fg3m)
        w_fta = np.dot(weights, fta)
        w_ftm = np.dot(weights, ftm)
        w_oreb = np.dot(weights, oreb)
        w_dreb = np.dot(weights, dreb)
        w_ast = np.dot(weights, ast)
        w_stl = np.dot(weights, stl)
        w_blk = np.dot(weights, blk)
        w_tov = np.dot(weights, tov)
        w_pf = np.dot(weights, pf)
        w_team_poss = np.dot(weights, team_poss)

        fg2a = fga - fg3a
        fg2m = fgm - fg3m
        w_fg2a = np.dot(weights, fg2a)
        w_fg2m = np.dot(weights, fg2m)

        player_poss_used = fga + 0.44 * fta + tov
        w_player_poss = np.dot(weights, player_poss_used)

        # Possession share (recent only — this is context-dependent)
        poss_share_raw = np.where(
            (team_poss > 0) & (mins > 0),
            player_poss_used / team_poss * (48.0 / mins),
            0.20
        )
        poss_share_raw = np.clip(poss_share_raw, 0.05, 0.50)
        w_poss_share = np.dot(weights, poss_share_raw)

        # Position
        pos_slots = self._positions.get(player_id, ('W',)) if self._positions else ('W',)

        profile = PossessionProfile(
            player_id=player_id,
            player_name=games.iloc[0]['player_name'],
            team_id=team_id,
            games_used=n,
            career_games=career['n_games'],
            mpg=w_min,
            possession_share=float(w_poss_share),
            position_slots=pos_slots,
        )

        # ============================================================
        # Layer 3: Bayesian blending (career prior + recent form)
        # ============================================================

        # Shooting percentages — blend career and recent
        # Recent "attempts" scaled by window: weighted FGA * n gives effective sample
        recent_fg2a_eff = w_fg2a * n
        recent_fg3a_eff = w_fg3a * n
        recent_fta_eff = w_fta * n

        profile.fg2_pct = self._bayesian_rate(
            w_fg2m * n, recent_fg2a_eff,
            career['total_fg2m'], career['total_fg2a'],
            LEAGUE_AVG['fg2_pct'], self.PRIOR_FGA
        )
        profile.fg3_pct = self._bayesian_rate(
            w_fg3m * n, recent_fg3a_eff,
            career['total_fg3m'], career['total_fg3a'],
            LEAGUE_AVG['fg3_pct'], self.PRIOR_FGA * 0.5  # less prior for 3pt (more variable)
        )
        profile.ft_pct = self._bayesian_rate(
            w_ftm * n, recent_fta_eff,
            career['total_ftm'], career['total_fta'],
            LEAGUE_AVG['ft_pct'], self.PRIOR_FTA
        )

        # Clamp to reasonable bounds
        profile.fg2_pct = np.clip(profile.fg2_pct, 0.30, 0.80)
        profile.fg3_pct = np.clip(profile.fg3_pct, 0.20, 0.55)
        profile.ft_pct = np.clip(profile.ft_pct, 0.40, 0.98)

        # ============================================================
        # Outcome rates — blend career and recent
        # ============================================================
        if w_player_poss > 0:
            # Recent rates
            recent_tov_rate = w_tov / w_player_poss
            non_tov = w_player_poss - w_tov
            if non_tov > 0:
                recent_foul_rate = min((w_fta / 2.2), non_tov * 0.25) / non_tov
                total_recent_fga = w_fg2a + w_fg3a
                recent_two_rate = w_fg2a / total_recent_fga if total_recent_fga > 0 else 0.61
                recent_three_rate = w_fg3a / total_recent_fga if total_recent_fga > 0 else 0.39
                recent_ast_rate = w_ast / non_tov
            else:
                recent_foul_rate = LEAGUE_AVG['foul_drawn_rate']
                recent_two_rate = LEAGUE_AVG['two_pt_rate']
                recent_three_rate = LEAGUE_AVG['three_pt_rate']
                recent_ast_rate = LEAGUE_AVG['assist_rate']

            # Career rates
            if career['total_player_poss'] > 0:
                career_tov_rate = career['total_tov'] / career['total_player_poss']
                career_non_tov = career['total_non_tov']
                if career_non_tov > 0:
                    career_foul_rate = min(
                        (career['total_fta'] / 2.2), career_non_tov * 0.25
                    ) / career_non_tov
                    career_total_fga = career['total_fg2a'] + career['total_fg3a']
                    career_two_rate = career['total_fg2a'] / career_total_fga if career_total_fga > 0 else 0.61
                    career_three_rate = career['total_fg3a'] / career_total_fga if career_total_fga > 0 else 0.39
                    career_ast_rate = career['total_ast'] / career_non_tov
                else:
                    career_foul_rate = LEAGUE_AVG['foul_drawn_rate']
                    career_two_rate = LEAGUE_AVG['two_pt_rate']
                    career_three_rate = LEAGUE_AVG['three_pt_rate']
                    career_ast_rate = LEAGUE_AVG['assist_rate']
            else:
                career_tov_rate = LEAGUE_AVG['turnover_rate']
                career_foul_rate = LEAGUE_AVG['foul_drawn_rate']
                career_two_rate = LEAGUE_AVG['two_pt_rate']
                career_three_rate = LEAGUE_AVG['three_pt_rate']
                career_ast_rate = LEAGUE_AVG['assist_rate']

            # Blend: weight recent by effective sample vs prior strength
            recent_poss_eff = w_player_poss * n
            career_poss = career['total_player_poss']
            blend = min(recent_poss_eff / self.PRIOR_POSS, 1.0)

            # Career shrunk toward league avg first
            career_shrink = min(career_poss / (career_poss + self.PRIOR_POSS), 0.95)

            def blend_rate(recent, career_r, league):
                shrunk_career = career_r * career_shrink + league * (1.0 - career_shrink)
                return shrunk_career * (1.0 - blend) + recent * blend

            profile.turnover_rate = blend_rate(recent_tov_rate, career_tov_rate,
                                               LEAGUE_AVG['turnover_rate'])
            profile.foul_drawn_rate = blend_rate(recent_foul_rate, career_foul_rate,
                                                  LEAGUE_AVG['foul_drawn_rate'])
            profile.two_pt_rate = blend_rate(recent_two_rate, career_two_rate,
                                              LEAGUE_AVG['two_pt_rate'])
            profile.three_pt_rate = blend_rate(recent_three_rate, career_three_rate,
                                                LEAGUE_AVG['three_pt_rate'])
            profile.assist_rate = blend_rate(recent_ast_rate, career_ast_rate,
                                              LEAGUE_AVG['assist_rate'])
        else:
            profile.turnover_rate = LEAGUE_AVG['turnover_rate']
            profile.foul_drawn_rate = LEAGUE_AVG['foul_drawn_rate']
            profile.two_pt_rate = LEAGUE_AVG['two_pt_rate']
            profile.three_pt_rate = LEAGUE_AVG['three_pt_rate']
            profile.assist_rate = LEAGUE_AVG['assist_rate']

        # ============================================================
        # OREB rate — blend career and recent
        # ============================================================
        recent_missed = w_fga - w_fgm
        if recent_missed > 0:
            recent_oreb_rate = w_oreb / recent_missed
        else:
            recent_oreb_rate = LEAGUE_AVG['oreb_rate']

        if career['missed_fga'] > 0:
            career_oreb_rate = career['total_oreb'] / career['missed_fga']
        else:
            career_oreb_rate = LEAGUE_AVG['oreb_rate']

        # OREB is very position-dependent, so less shrinkage to league avg
        oreb_blend = min(n / 15.0, 1.0)  # 15 games to fully trust recent
        profile.oreb_rate = career_oreb_rate * (1.0 - oreb_blend) + recent_oreb_rate * oreb_blend
        profile.oreb_rate = np.clip(profile.oreb_rate, 0.0, 0.50)

        # ============================================================
        # Steals, blocks, DREB, assist% rates
        # ============================================================
        # Steals per defensive possession
        if w_team_poss > 0 and w_min > 0:
            def_poss_on_court = w_team_poss * (w_min / 48.0)
            profile.stl_per_poss = float(np.clip(w_stl / max(def_poss_on_court, 1.0), 0.0, 0.06))
            profile.blk_per_poss = float(np.clip(w_blk / max(def_poss_on_court, 1.0), 0.0, 0.08))
        else:
            profile.stl_per_poss = LEAGUE_AVG['stl_per_poss']
            profile.blk_per_poss = LEAGUE_AVG['blk_per_poss']

        # DREB rate: share of team DREBs this player grabs
        # Approximate: player_dreb / (team_poss * dreb_opportunity_rate)
        # Simpler: per-minute DREB rate, will be normalized at sim time
        if w_min > 0:
            profile.dreb_rate = float(np.clip(w_dreb / w_min, 0.0, 0.60))
        else:
            profile.dreb_rate = LEAGUE_AVG['dreb_rate']

        # Assist%: fraction of teammate FGM this player assists
        # Approximate from ast / (team_fgm * min/48)
        if w_team_poss > 0 and w_min > 0:
            # est team FGM per game from possessions (~0.45 FG% * ~0.88 non-TOV = ~40 FGM)
            est_team_fgm = w_team_poss * 0.40
            on_court_share = w_min / 48.0
            if est_team_fgm > 0 and on_court_share > 0:
                profile.ast_pct = float(np.clip(w_ast / (est_team_fgm * on_court_share), 0.0, 0.60))
            else:
                profile.ast_pct = LEAGUE_AVG['ast_pct']
        else:
            profile.ast_pct = LEAGUE_AVG['ast_pct']

        # ============================================================
        # Fouls per possession
        # ============================================================
        if w_team_poss > 0 and w_min > 0:
            player_poss_on_court = w_team_poss * (w_min / 48.0)
            if player_poss_on_court > 0:
                profile.pf_per_poss = w_pf / player_poss_on_court
            else:
                profile.pf_per_poss = LEAGUE_AVG['pf_per_poss']
        else:
            profile.pf_per_poss = LEAGUE_AVG['pf_per_poss']

        # ============================================================
        # Assist target weight
        # ============================================================
        if w_team_poss > 0 and w_min > 0:
            player_poss_on_court = w_team_poss * (w_min / 48.0)
            profile.assist_target_weight = max(
                w_fga / max(player_poss_on_court, 1.0) * 100, 1.0)
        else:
            profile.assist_target_weight = max(w_fga, 1.0)

        # ============================================================
        # And-1 rate: % of made FGs resulting in and-1
        # ============================================================
        career_fgm = career['total_fg2m'] + career['total_fg3m']
        career_and1 = self._and1_counts.get(player_id, 0) if self._and1_counts else 0
        if career_fgm > 0 and career_and1 > 0:
            profile.and1_rate = float(np.clip(career_and1 / career_fgm, 0.01, 0.20))
        else:
            profile.and1_rate = 0.05  # league average

        # ============================================================
        # 3-point foul rate: % of shooting fouls that are 3-shot fouls
        # Based on player's 3PA share (more 3s = more 3-shot fouls)
        # ============================================================
        three_shot = self._three_shot_counts.get(player_id, 0) if self._three_shot_counts else 0
        two_shot = self._two_shot_counts.get(player_id, 0) if self._two_shot_counts else 0
        total_shooting_fouls = three_shot + two_shot
        if total_shooting_fouls > 20:
            # Divide by 3 for 3-shot fouls (each has 3 FT rows) and 2 for 2-shot
            three_trips = three_shot / 3.0
            two_trips = two_shot / 2.0
            total_trips = three_trips + two_trips
            if total_trips > 0:
                profile.three_pt_foul_rate = float(np.clip(three_trips / total_trips, 0.02, 0.50))
            else:
                profile.three_pt_foul_rate = 0.15
        else:
            # Not enough data — estimate from 3pt shot share
            profile.three_pt_foul_rate = float(profile.three_pt_rate * 0.4)  # rough proxy

        # ============================================================
        # Possession tempo: avg seconds per possession for this player
        # ============================================================
        tempo = self._poss_tempo.get(player_id, None) if self._poss_tempo else None
        if tempo is not None:
            profile.poss_tempo_seconds = float(np.clip(tempo, 6.0, 20.0))
        else:
            profile.poss_tempo_seconds = 13.0  # league average

        # Build defensive profile
        self._build_defensive_profile(profile, games, weights, player_all, career, n)

        self._cache[cache_key] = profile
        return profile

    def _compute_career_defense(self, player_all: pd.DataFrame) -> Dict[str, float]:
        """Compute career defensive averages from opponent stats."""
        merged = player_all.merge(self._opp_stats, on=['game_id', 'team_id'], how='left')
        merged = merged.dropna(subset=['opp_fga'])

        if len(merged) < 3:
            return {
                'fg2_allowed': LEAGUE_AVG['def_fg2_pct_allowed'],
                'fg3_allowed': LEAGUE_AVG['def_fg3_pct_allowed'],
                'tov_forced': LEAGUE_AVG['def_tov_forced_rate'],
                'oreb_allowed': LEAGUE_AVG['def_oreb_allowed_rate'],
            }

        opp_fga = merged['opp_fga'].sum()
        opp_fgm = merged['opp_fgm'].sum()
        opp_fg3a = merged['opp_fg3a'].sum()
        opp_fg3m = merged['opp_fg3m'].sum()
        opp_tov = merged['opp_tov'].sum()
        opp_oreb = merged['opp_oreb'].sum()
        opp_poss = merged['opp_poss'].sum()

        opp_fg2a = opp_fga - opp_fg3a
        opp_fg2m = opp_fgm - opp_fg3m

        return {
            'fg2_allowed': opp_fg2m / opp_fg2a if opp_fg2a > 0 else LEAGUE_AVG['def_fg2_pct_allowed'],
            'fg3_allowed': opp_fg3m / opp_fg3a if opp_fg3a > 0 else LEAGUE_AVG['def_fg3_pct_allowed'],
            'tov_forced': opp_tov / opp_poss if opp_poss > 0 else LEAGUE_AVG['def_tov_forced_rate'],
            'oreb_allowed': opp_oreb / max(opp_fga - opp_fgm, 1) if opp_fga > opp_fgm else LEAGUE_AVG['def_oreb_allowed_rate'],
        }

    def _build_defensive_profile(self, profile: PossessionProfile,
                                  games: pd.DataFrame, weights: np.ndarray,
                                  player_all: pd.DataFrame, career: Dict,
                                  n: int):
        """Build defensive profile: what opponents produce when this player plays."""
        def_games = games.merge(self._opp_stats, on=['game_id', 'team_id'], how='left')

        if def_games['opp_fga'].isna().all():
            return

        dg = def_games.dropna(subset=['opp_fga'])
        if len(dg) < self.MIN_GAMES:
            return

        d_weights = weights[:len(dg)]
        d_weights = d_weights / d_weights.sum()

        w_opp_fga = np.dot(d_weights, dg['opp_fga'].values.astype(float))
        w_opp_fgm = np.dot(d_weights, dg['opp_fgm'].values.astype(float))
        w_opp_fg3a = np.dot(d_weights, dg['opp_fg3a'].values.astype(float))
        w_opp_fg3m = np.dot(d_weights, dg['opp_fg3m'].values.astype(float))
        w_opp_tov = np.dot(d_weights, dg['opp_tov'].values.astype(float))
        w_opp_oreb = np.dot(d_weights, dg['opp_oreb'].values.astype(float))
        w_opp_poss = np.dot(d_weights, dg['opp_poss'].values.astype(float))

        opp_fg2a = w_opp_fga - w_opp_fg3a
        opp_fg2m = w_opp_fgm - w_opp_fg3m

        recent_def_fg2 = opp_fg2m / opp_fg2a if opp_fg2a > 0 else LEAGUE_AVG['def_fg2_pct_allowed']
        recent_def_fg3 = w_opp_fg3m / w_opp_fg3a if w_opp_fg3a > 0 else LEAGUE_AVG['def_fg3_pct_allowed']
        recent_def_tov = w_opp_tov / w_opp_poss if w_opp_poss > 0 else LEAGUE_AVG['def_tov_forced_rate']
        opp_missed = w_opp_fga - w_opp_fgm
        recent_def_oreb = w_opp_oreb / opp_missed if opp_missed > 0 else LEAGUE_AVG['def_oreb_allowed_rate']

        # Bayesian blend: career + recent + league avg
        career_def = self._compute_career_defense(player_all)
        def_blend = min(n / 8.0, 1.0)   # trust recent defense faster
        career_def_wt = min(career['n_games'] / 40.0, 0.9)  # trust career defense more

        def bdef(recent_v, career_v, league_v):
            shrunk = career_v * career_def_wt + league_v * (1.0 - career_def_wt)
            return shrunk * (1.0 - def_blend) + recent_v * def_blend

        profile.def_fg2_pct_allowed = float(np.clip(bdef(recent_def_fg2, career_def['fg2_allowed'], LEAGUE_AVG['def_fg2_pct_allowed']), 0.35, 0.70))
        profile.def_fg3_pct_allowed = float(np.clip(bdef(recent_def_fg3, career_def['fg3_allowed'], LEAGUE_AVG['def_fg3_pct_allowed']), 0.25, 0.45))
        profile.def_tov_forced_rate = float(np.clip(bdef(recent_def_tov, career_def['tov_forced'], LEAGUE_AVG['def_tov_forced_rate']), 0.05, 0.25))
        profile.def_oreb_allowed_rate = float(np.clip(bdef(recent_def_oreb, career_def['oreb_allowed'], LEAGUE_AVG['def_oreb_allowed_rate']), 0.10, 0.40))
        profile.def_foul_rate = profile.pf_per_poss

    def get_team_profiles(self, team_id: int, before_date: pd.Timestamp,
                          top_n: int = 13) -> List[PossessionProfile]:
        """Get per-possession profiles for a team's rotation players."""
        self._load_data()
        gl = self._game_logs

        cutoff = before_date - pd.Timedelta(days=60)
        recent = gl[
            (gl['team_id'] == team_id) &
            (gl['game_date'] < before_date) &
            (gl['game_date'] >= cutoff)
        ]

        if recent.empty:
            return []

        player_mins = recent.groupby('player_id')['min'].sum().sort_values(ascending=False)
        top_players = player_mins.head(top_n).index.tolist()

        profiles = []
        for pid in top_players:
            p = self.get_profile(pid, team_id, before_date)
            if p is not None:
                profiles.append(p)

        profiles.sort(key=lambda p: p.mpg, reverse=True)
        return profiles

    def clear_cache(self):
        self._cache.clear()
