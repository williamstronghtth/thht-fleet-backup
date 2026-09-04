"""
Game Simulator Engine v2
=========================

Simulates a full NBA game possession by possession.

Core philosophy:
  The 5 players on the court ARE the offense. No team-level efficiency
  multiplier — each possession outcome is determined entirely by the
  player who uses it (their shooting %, turnover rate, etc.)

  Each possession consumes real seconds off the game clock based on
  the player's style. High-usage iso players burn more clock.
  Transition possessions are faster.

  Game state (score differential) affects:
  - Pace: trailing teams play faster, leading teams slow down
  - Shot selection: trailing teams shoot more 3s
  - Lineups: blowouts trigger garbage time (bench players)
  - Late-game fouls: trailing teams intentionally foul

Rotation philosophy:
  Two things drive substitutions: minutes played and fouls.
  Each player has a minutes budget (their real-world MPG).
  Positional constraints ensure at least 1G, 1W, 1C.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple

from .player_model import PossessionProfile


@dataclass
class GameConfig:
    """Configuration for a single game simulation."""
    home_roster: List[PossessionProfile] = field(default_factory=list)
    away_roster: List[PossessionProfile] = field(default_factory=list)

    # Ref impact
    ref_foul_modifier: float = 1.0
    ref_home_bias: float = 0.0

    # Team pace (possessions per 48 min) — used for base clock speed
    home_pace: float = 98.0
    away_pace: float = 98.0
    league_avg_pace: float = 98.0

    # Coach rotation settings
    home_players_used: int = 9
    away_players_used: int = 9

    # Home court advantage (data-driven from 2022-23 actuals)
    # Applied as: home gets +bonus, away gets -bonus (split the diff)
    home_court_fg2_bonus: float = 0.0037   # +/- 0.37% each side (total 0.74% gap)
    home_court_fg3_bonus: float = 0.0056   # +/- 0.56% each side (total 1.12% gap)
    home_court_foul_bonus: float = 0.003   # home draws ~0.6 more FTA/game ≈ +0.3% foul draw rate


@dataclass
class PlayerBoxScore:
    """Per-player box score from a simulation."""
    player_id: str = ""
    player_name: str = ""
    team: str = ""  # 'home' or 'away'
    minutes: float = 0.0
    points: int = 0
    fg2a: int = 0
    fg2m: int = 0
    fg3a: int = 0
    fg3m: int = 0
    fta: int = 0
    ftm: int = 0
    turnovers: int = 0
    fouls: int = 0
    oreb: int = 0
    dreb: int = 0
    assists: int = 0
    steals: int = 0
    blocks: int = 0
    # Derived
    @property
    def fga(self) -> int: return self.fg2a + self.fg3a
    @property
    def fgm(self) -> int: return self.fg2m + self.fg3m
    @property
    def rebounds(self) -> int: return self.oreb + self.dreb


@dataclass
class GameResult:
    """Result of a single game simulation."""
    home_score: int = 0
    away_score: int = 0
    home_q_scores: List[int] = field(default_factory=list)
    away_q_scores: List[int] = field(default_factory=list)
    overtime_periods: int = 0
    home_possessions: int = 0
    away_possessions: int = 0
    player_box_scores: List[PlayerBoxScore] = field(default_factory=list)


# Constants
QUARTER_SECONDS = 720.0    # 12 minutes
OT_SECONDS = 300.0         # 5 minutes
REGULATION_QUARTERS = 4
MAX_OT = 5
FOUL_OUT = 6

# Average possession length in seconds (NBA average ~14-15 seconds)
BASE_POSS_SECONDS = 14.5
# Variance in possession length (standard deviation)
POSS_SECONDS_STD = 4.0

# Score differential thresholds for game-state behavior
BLOWOUT_THRESHOLD = 25       # garbage time
TRAILING_BIG_THRESHOLD = 15  # desperate mode: more 3s, faster pace
CLOSE_GAME_THRESHOLD = 5     # normal competitive play

# Foul trouble thresholds
FOUL_TROUBLE_THRESHOLDS = {0: 2, 1: 3, 2: 4, 3: 5}

# Base non-shooting foul rate
BASE_FOUL_RATE = 0.20


class GameSimulator:
    """Possession-by-possession NBA game simulator.

    The 5 players on the court determine everything:
    - Who uses the possession (weighted by possession share)
    - What they do (their personal rates)
    - Whether they make it (their personal percentages)
    - How long it takes (pace-adjusted clock usage)

    No team-level OffRtg/DefRtg multiplier. The lineup IS the rating.
    """

    def __init__(self, config: GameConfig, rng: Optional[np.random.Generator] = None):
        self.config = config
        self.rng = rng or np.random.default_rng()

        self._home_arrays = self._build_player_arrays(config.home_roster)
        self._away_arrays = self._build_player_arrays(config.away_roster)

        # Base seconds per possession (pace-adjusted)
        # Faster teams = shorter possessions
        avg_pace = (config.home_pace + config.away_pace) / 2.0
        # 48 min = 2880 seconds, split between ~avg_pace possessions per team
        # Each team's possession = 2880 / (avg_pace * 2) seconds on average
        if avg_pace > 0:
            self._base_poss_seconds = 2880.0 / (avg_pace * 2.0)
        else:
            self._base_poss_seconds = BASE_POSS_SECONDS

        # Per-team pace adjustment factor
        if config.league_avg_pace > 0:
            self._home_pace_factor = config.home_pace / config.league_avg_pace
            self._away_pace_factor = config.away_pace / config.league_avg_pace
        else:
            self._home_pace_factor = 1.0
            self._away_pace_factor = 1.0

    def _build_player_arrays(self, roster: List[PossessionProfile]) -> Dict:
        """Pre-compute numpy arrays from player profiles."""
        n = len(roster)
        if n == 0:
            return self._default_arrays()

        return {
            'n': n,
            'player_ids': np.array([p.player_id for p in roster]),
            'names': [p.player_name for p in roster],
            'position_slots': [p.position_slots for p in roster],
            'mpg': np.array([p.mpg for p in roster], dtype=np.float64),
            'possession_share': np.array([p.possession_share for p in roster], dtype=np.float64),
            'turnover_rate': np.array([p.turnover_rate for p in roster], dtype=np.float64),
            'two_pt_rate': np.array([p.two_pt_rate for p in roster], dtype=np.float64),
            'three_pt_rate': np.array([p.three_pt_rate for p in roster], dtype=np.float64),
            'foul_drawn_rate': np.array([p.foul_drawn_rate for p in roster], dtype=np.float64),
            'assist_rate': np.array([p.assist_rate for p in roster], dtype=np.float64),
            'fg2_pct': np.array([p.fg2_pct for p in roster], dtype=np.float64),
            'fg3_pct': np.array([p.fg3_pct for p in roster], dtype=np.float64),
            'ft_pct': np.array([p.ft_pct for p in roster], dtype=np.float64),
            'oreb_rate': np.array([p.oreb_rate for p in roster], dtype=np.float64),
            'pf_per_poss': np.array([p.pf_per_poss for p in roster], dtype=np.float64),
            'assist_target_weight': np.array([p.assist_target_weight for p in roster], dtype=np.float64),
            'and1_rate': np.array([p.and1_rate for p in roster], dtype=np.float64),
            'three_pt_foul_rate': np.array([p.three_pt_foul_rate for p in roster], dtype=np.float64),
            'poss_tempo_seconds': np.array([p.poss_tempo_seconds for p in roster], dtype=np.float64),
            # Counting stat rates
            'stl_per_poss': np.array([p.stl_per_poss for p in roster], dtype=np.float64),
            'blk_per_poss': np.array([p.blk_per_poss for p in roster], dtype=np.float64),
            'dreb_rate': np.array([p.dreb_rate for p in roster], dtype=np.float64),
            'ast_pct': np.array([p.ast_pct for p in roster], dtype=np.float64),
            # Defensive profile
            'def_fg2_pct_allowed': np.array([p.def_fg2_pct_allowed for p in roster], dtype=np.float64),
            'def_fg3_pct_allowed': np.array([p.def_fg3_pct_allowed for p in roster], dtype=np.float64),
            'def_tov_forced_rate': np.array([p.def_tov_forced_rate for p in roster], dtype=np.float64),
            'def_oreb_allowed_rate': np.array([p.def_oreb_allowed_rate for p in roster], dtype=np.float64),
        }

    def _default_arrays(self) -> Dict:
        """Default arrays for a generic 5-player lineup."""
        n = 5
        return {
            'n': n,
            'player_ids': np.arange(n),
            'names': [f'Player_{i}' for i in range(n)],
            'position_slots': [('G',), ('G',), ('W',), ('W',), ('C',)],
            'mpg': np.full(n, 24.0),
            'possession_share': np.full(n, 0.20),
            'turnover_rate': np.full(n, 0.137),
            'two_pt_rate': np.full(n, 0.61),
            'three_pt_rate': np.full(n, 0.39),
            'foul_drawn_rate': np.full(n, 0.12),
            'assist_rate': np.full(n, 0.29),
            'fg2_pct': np.full(n, 0.552),
            'fg3_pct': np.full(n, 0.366),
            'ft_pct': np.full(n, 0.783),
            'oreb_rate': np.full(n, 0.228),
            'pf_per_poss': np.full(n, 0.04),
            'assist_target_weight': np.full(n, 5.0),
            'and1_rate': np.full(n, 0.05),
            'three_pt_foul_rate': np.full(n, 0.15),
            'poss_tempo_seconds': np.full(n, 13.0),
            'stl_per_poss': np.full(n, 0.015),
            'blk_per_poss': np.full(n, 0.012),
            'dreb_rate': np.full(n, 0.15),
            'ast_pct': np.full(n, 0.15),
            'def_fg2_pct_allowed': np.full(n, 0.552),
            'def_fg3_pct_allowed': np.full(n, 0.366),
            'def_tov_forced_rate': np.full(n, 0.137),
            'def_oreb_allowed_rate': np.full(n, 0.228),
        }

    def _get_possession_seconds(self, score_diff: int, is_home: bool,
                                 seconds_remaining: float, quarter: int,
                                 player_tempo: float = 13.0) -> float:
        """How many seconds does this possession consume?

        Affected by:
        - Player tempo (iso-heavy players burn more clock)
        - Team pace (faster teams = shorter possessions)
        - Score differential (trailing = faster, leading = slower)
        - Late game (very short possessions when trailing late)
        """
        rng = self.rng

        # Blend player tempo with team pace
        pace_factor = self._home_pace_factor if is_home else self._away_pace_factor
        team_base = self._base_poss_seconds / pace_factor
        # 50/50 blend of player tempo and team pace
        base = (player_tempo + team_base) / 2.0

        # Score-dependent pace adjustment
        # Positive score_diff = this team is leading
        if score_diff > BLOWOUT_THRESHOLD:
            # Way ahead: slow it down, burn clock
            base *= 1.15
        elif score_diff > CLOSE_GAME_THRESHOLD:
            # Comfortable lead: slightly slower
            base *= 1.05
        elif score_diff < -TRAILING_BIG_THRESHOLD:
            # Way behind: play fast, quick shots
            base *= 0.80
        elif score_diff < -CLOSE_GAME_THRESHOLD:
            # Behind: push pace a bit
            base *= 0.92

        # Late-game intentional speed (last 2 min, trailing)
        is_late = quarter >= REGULATION_QUARTERS - 1 and seconds_remaining < 120
        if is_late and score_diff < -CLOSE_GAME_THRESHOLD:
            base *= 0.65  # intentional fouls, quick shots

        # Add randomness
        seconds = base + rng.normal(0, POSS_SECONDS_STD * 0.5)

        # Clamp: minimum 4 seconds (transition), max 24 (shot clock)
        return np.clip(seconds, 4.0, 24.0)

    def _get_game_state(self, score_diff: int, quarter: int,
                        seconds_remaining: float) -> str:
        """Classify the current game state for behavior adjustments.

        Returns one of: 'normal', 'blowout', 'trailing_big', 'crunch', 'garbage'
        """
        is_late = quarter >= REGULATION_QUARTERS - 1 and seconds_remaining < 300
        is_very_late = quarter >= REGULATION_QUARTERS - 1 and seconds_remaining < 120
        is_ot = quarter >= REGULATION_QUARTERS
        abs_diff = abs(score_diff)

        if abs_diff >= BLOWOUT_THRESHOLD and quarter >= 2:
            return 'garbage'  # either team in a blowout
        if is_ot or (is_late and abs_diff <= 10):
            return 'crunch'
        if score_diff < -TRAILING_BIG_THRESHOLD:
            return 'trailing_big'
        return 'normal'

    def _get_lineup(self, arrays: Dict, quarter: int, game_minutes_elapsed: float,
                    fouls: np.ndarray, minutes_played: np.ndarray,
                    is_home: bool, score_diff: int) -> np.ndarray:
        """Determine which 5 players are on the floor."""
        n = arrays['n']
        if n <= 5:
            return np.arange(n)

        players_used = min(
            self.config.home_players_used if is_home else self.config.away_players_used, n
        )
        mpg = arrays['mpg']
        game_length = 48.0

        if quarter >= REGULATION_QUARTERS:
            ot_extra = OT_SECONDS / 60.0 * (quarter - REGULATION_QUARTERS + 1)
            budget = mpg + (mpg / 48.0) * ot_extra
        else:
            budget = mpg.copy()

        # Availability
        available = np.ones(n, dtype=bool)
        available[fouls >= FOUL_OUT] = False
        available[players_used:] = False
        available_idx = np.where(available)[0]

        if len(available_idx) < 5:
            available_idx = np.where(fouls < FOUL_OUT)[0][:5]
            if len(available_idx) < 5:
                available_idx = np.arange(min(5, n))
            return available_idx[:5]

        # Garbage time: play bench guys, rest starters
        is_garbage = abs(score_diff) >= BLOWOUT_THRESHOLD and quarter >= 2
        if is_garbage and game_minutes_elapsed > 36:  # Q4 garbage time
            # Use players ranked 5-10 by MPG (bench guys)
            bench_avail = available_idx[available_idx >= 5] if len(available_idx[available_idx >= 5]) >= 5 else available_idx
            if len(bench_avail) >= 5:
                return bench_avail[:5]

        # Crunch time override
        is_q4_or_later = quarter >= REGULATION_QUARTERS - 1
        time_left = max(0, game_length - game_minutes_elapsed)
        is_ot = quarter >= REGULATION_QUARTERS
        is_crunch = (is_ot or (is_q4_or_later and time_left <= 5.0)) \
            and abs(score_diff) <= 10

        if is_crunch:
            crunch_avail = np.where((fouls < FOUL_OUT) & available)[0]
            if len(crunch_avail) < 5:
                crunch_avail = np.where(fouls < FOUL_OUT)[0]
            top5 = crunch_avail[np.argsort(mpg[crunch_avail])[-5:]]
            return top5

        # Normal scoring-based lineup selection
        scores = np.full(n, -999.0)
        for i in available_idx:
            mins_remaining = budget[i] - minutes_played[i]
            mins_frac = mins_remaining / max(budget[i], 1.0)
            game_frac = max(game_length - game_minutes_elapsed, 0.1) / game_length

            budget_ratio = mins_frac / game_frac if game_frac > 0 else (1.0 if mins_remaining > 0 else 0.0)
            budget_score = (budget_ratio - 1.0) * 10.0
            if mins_remaining <= 0.5:
                budget_score = -20.0

            foul_threshold = FOUL_TROUBLE_THRESHOLDS.get(min(quarter, 3), 5)
            foul_penalty = 0.0
            if fouls[i] >= foul_threshold:
                foul_penalty = -5.0 * (fouls[i] - foul_threshold + 1)
            elif fouls[i] >= foul_threshold - 1:
                foul_penalty = -2.0

            importance = (mpg[i] / max(mpg[0], 1.0)) * 5.0
            scores[i] = budget_score + foul_penalty + importance

        # Positional constraints
        position_slots = arrays['position_slots']
        sorted_by_score = np.argsort(scores)[::-1]

        lineup = []
        used = set()
        for required_pos in ('G', 'W', 'C'):
            for idx in sorted_by_score:
                if idx in used or scores[idx] <= -999:
                    continue
                if required_pos in position_slots[idx]:
                    lineup.append(idx)
                    used.add(idx)
                    break
        for idx in sorted_by_score:
            if len(lineup) >= 5:
                break
            if idx in used or scores[idx] <= -999:
                continue
            lineup.append(idx)
            used.add(idx)

        if len(lineup) < 5:
            for idx in available_idx:
                if len(lineup) >= 5:
                    break
                if idx not in used:
                    lineup.append(idx)
                    used.add(idx)

        return np.array(sorted(lineup[:5]))

    def simulate(self) -> GameResult:
        """Run a single game simulation with time-based possessions."""
        result = GameResult()
        result.home_q_scores = []
        result.away_q_scores = []

        home_arrays = self._home_arrays
        away_arrays = self._away_arrays
        rng = self.rng

        # Game state tracking
        home_fouls = np.zeros(home_arrays['n'], dtype=np.int32)
        away_fouls = np.zeros(away_arrays['n'], dtype=np.int32)
        home_minutes = np.zeros(home_arrays['n'], dtype=np.float64)
        away_minutes = np.zeros(away_arrays['n'], dtype=np.float64)

        # Player stat tracking
        home_pts = np.zeros(home_arrays['n'], dtype=np.int32)
        away_pts = np.zeros(away_arrays['n'], dtype=np.int32)
        home_fg2a = np.zeros(home_arrays['n'], dtype=np.int32)
        home_fg2m = np.zeros(home_arrays['n'], dtype=np.int32)
        home_fg3a = np.zeros(home_arrays['n'], dtype=np.int32)
        home_fg3m = np.zeros(home_arrays['n'], dtype=np.int32)
        home_fta = np.zeros(home_arrays['n'], dtype=np.int32)
        home_ftm = np.zeros(home_arrays['n'], dtype=np.int32)
        home_tov = np.zeros(home_arrays['n'], dtype=np.int32)
        away_fg2a = np.zeros(away_arrays['n'], dtype=np.int32)
        away_fg2m = np.zeros(away_arrays['n'], dtype=np.int32)
        away_fg3a = np.zeros(away_arrays['n'], dtype=np.int32)
        away_fg3m = np.zeros(away_arrays['n'], dtype=np.int32)
        away_fta = np.zeros(away_arrays['n'], dtype=np.int32)
        away_ftm = np.zeros(away_arrays['n'], dtype=np.int32)
        away_tov = np.zeros(away_arrays['n'], dtype=np.int32)
        # Counting stats
        home_oreb = np.zeros(home_arrays['n'], dtype=np.int32)
        home_dreb = np.zeros(home_arrays['n'], dtype=np.int32)
        home_ast = np.zeros(home_arrays['n'], dtype=np.int32)
        home_stl = np.zeros(home_arrays['n'], dtype=np.int32)
        home_blk = np.zeros(home_arrays['n'], dtype=np.int32)
        away_oreb = np.zeros(away_arrays['n'], dtype=np.int32)
        away_dreb = np.zeros(away_arrays['n'], dtype=np.int32)
        away_ast = np.zeros(away_arrays['n'], dtype=np.int32)
        away_stl = np.zeros(away_arrays['n'], dtype=np.int32)
        away_blk = np.zeros(away_arrays['n'], dtype=np.int32)

        home_total = 0
        away_total = 0
        home_poss_total = 0
        away_poss_total = 0
        game_minutes_elapsed = 0.0

        quarter = 0
        while True:
            is_ot = quarter >= REGULATION_QUARTERS
            quarter_seconds = OT_SECONDS if is_ot else QUARTER_SECONDS

            home_q_score = 0
            away_q_score = 0
            clock = quarter_seconds  # seconds remaining in quarter

            home_lineup = None
            away_lineup = None
            poss_since_sub = 0
            is_home_poss = rng.random() < 0.5  # random first possession

            while clock > 0:
                score_diff_home = home_total + home_q_score - away_total - away_q_score
                current_game_min = game_minutes_elapsed + (quarter_seconds - clock) / 60.0

                # Re-evaluate lineups every ~8 possessions or at start
                if poss_since_sub >= 8 or home_lineup is None:
                    poss_since_sub = 0
                    home_lineup = self._get_lineup(
                        home_arrays, quarter, current_game_min,
                        home_fouls, home_minutes, True, score_diff_home
                    )
                    away_lineup = self._get_lineup(
                        away_arrays, quarter, current_game_min,
                        away_fouls, away_minutes, False, -score_diff_home
                    )

                # Determine possession time based on who's on the floor
                off_diff = score_diff_home if is_home_poss else -score_diff_home
                off_arrays = home_arrays if is_home_poss else away_arrays
                off_lineup = home_lineup if is_home_poss else away_lineup

                # Average tempo of the offensive lineup
                lineup_tempo = np.mean(off_arrays['poss_tempo_seconds'][off_lineup])

                poss_seconds = self._get_possession_seconds(
                    off_diff, is_home_poss, clock, quarter, lineup_tempo
                )

                # Don't exceed remaining time
                poss_seconds = min(poss_seconds, clock)
                poss_minutes = poss_seconds / 60.0

                # Accumulate minutes for on-court players
                if home_lineup is not None:
                    home_minutes[home_lineup] += poss_minutes
                if away_lineup is not None:
                    away_minutes[away_lineup] += poss_minutes

                # Get game state for behavior adjustments
                game_state = self._get_game_state(
                    off_diff, quarter, clock
                )

                # Simulate the possession: offense vs defense
                _h_stats = dict(stat_pts=home_pts, stat_fg2a=home_fg2a, stat_fg2m=home_fg2m,
                                stat_fg3a=home_fg3a, stat_fg3m=home_fg3m,
                                stat_fta=home_fta, stat_ftm=home_ftm, stat_tov=home_tov,
                                stat_oreb=home_oreb, stat_ast=home_ast,
                                stat_stl=away_stl, stat_blk=away_blk, stat_dreb=away_dreb)
                _a_stats = dict(stat_pts=away_pts, stat_fg2a=away_fg2a, stat_fg2m=away_fg2m,
                                stat_fg3a=away_fg3a, stat_fg3m=away_fg3m,
                                stat_fta=away_fta, stat_ftm=away_ftm, stat_tov=away_tov,
                                stat_oreb=away_oreb, stat_ast=away_ast,
                                stat_stl=home_stl, stat_blk=home_blk, stat_dreb=home_dreb)
                if is_home_poss:
                    points, oreb_bonus = self._simulate_possession(
                        home_arrays, home_lineup, True,
                        away_fouls, away_arrays, away_lineup,
                        game_state, off_diff, **_h_stats
                    )
                    home_q_score += points
                    home_poss_total += 1

                    if oreb_bonus and clock > 4:
                        oreb_seconds = min(rng.normal(6.0, 2.0), clock - 1)
                        oreb_seconds = max(oreb_seconds, 3.0)
                        clock -= oreb_seconds
                        if home_lineup is not None:
                            home_minutes[home_lineup] += oreb_seconds / 60.0
                            away_minutes[away_lineup] += oreb_seconds / 60.0

                        bp, _ = self._simulate_possession(
                            home_arrays, home_lineup, True,
                            away_fouls, away_arrays, away_lineup,
                            game_state, off_diff, **_h_stats
                        )
                        home_q_score += bp
                        home_poss_total += 1
                else:
                    points, oreb_bonus = self._simulate_possession(
                        away_arrays, away_lineup, False,
                        home_fouls, home_arrays, home_lineup,
                        game_state, off_diff, **_a_stats
                    )
                    away_q_score += points
                    away_poss_total += 1

                    if oreb_bonus and clock > 4:
                        oreb_seconds = min(rng.normal(6.0, 2.0), clock - 1)
                        oreb_seconds = max(oreb_seconds, 3.0)
                        clock -= oreb_seconds
                        if home_lineup is not None:
                            home_minutes[home_lineup] += oreb_seconds / 60.0
                            away_minutes[away_lineup] += oreb_seconds / 60.0

                        bp, _ = self._simulate_possession(
                            away_arrays, away_lineup, False,
                            home_fouls, home_arrays, home_lineup,
                            game_state, off_diff, **_a_stats
                        )
                        away_q_score += bp
                        away_poss_total += 1

                clock -= poss_seconds
                is_home_poss = not is_home_poss  # alternate possession
                poss_since_sub += 1

            game_minutes_elapsed += quarter_seconds / 60.0
            home_total += home_q_score
            away_total += away_q_score
            result.home_q_scores.append(home_q_score)
            result.away_q_scores.append(away_q_score)

            quarter += 1
            if quarter >= REGULATION_QUARTERS:
                if home_total != away_total:
                    break
                result.overtime_periods += 1
                if result.overtime_periods >= MAX_OT:
                    if rng.random() < 0.5:
                        home_total += 1
                    else:
                        away_total += 1
                    break

        result.home_score = home_total
        result.away_score = away_total
        result.home_possessions = home_poss_total
        result.away_possessions = away_poss_total

        # Build player box scores
        for i in range(home_arrays['n']):
            if home_minutes[i] > 0:
                result.player_box_scores.append(PlayerBoxScore(
                    player_id=str(home_arrays['player_ids'][i]),
                    player_name=home_arrays['names'][i],
                    team='home',
                    minutes=round(float(home_minutes[i]), 1),
                    points=int(home_pts[i]),
                    fg2a=int(home_fg2a[i]), fg2m=int(home_fg2m[i]),
                    fg3a=int(home_fg3a[i]), fg3m=int(home_fg3m[i]),
                    fta=int(home_fta[i]), ftm=int(home_ftm[i]),
                    turnovers=int(home_tov[i]), fouls=int(home_fouls[i]),
                    oreb=int(home_oreb[i]), dreb=int(home_dreb[i]),
                    assists=int(home_ast[i]),
                    steals=int(home_stl[i]), blocks=int(home_blk[i]),
                ))
        for i in range(away_arrays['n']):
            if away_minutes[i] > 0:
                result.player_box_scores.append(PlayerBoxScore(
                    player_id=str(away_arrays['player_ids'][i]),
                    player_name=away_arrays['names'][i],
                    team='away',
                    minutes=round(float(away_minutes[i]), 1),
                    points=int(away_pts[i]),
                    fg2a=int(away_fg2a[i]), fg2m=int(away_fg2m[i]),
                    fg3a=int(away_fg3a[i]), fg3m=int(away_fg3m[i]),
                    fta=int(away_fta[i]), ftm=int(away_ftm[i]),
                    turnovers=int(away_tov[i]), fouls=int(away_fouls[i]),
                    oreb=int(away_oreb[i]), dreb=int(away_dreb[i]),
                    assists=int(away_ast[i]),
                    steals=int(away_stl[i]), blocks=int(away_blk[i]),
                ))

        return result

    def _simulate_possession(self, off_arrays: Dict, off_lineup: np.ndarray,
                              is_home: bool, def_fouls: np.ndarray,
                              def_arrays: Dict, def_lineup: np.ndarray,
                              game_state: str, score_diff: int,
                              stat_pts=None, stat_fg2a=None, stat_fg2m=None,
                              stat_fg3a=None, stat_fg3m=None,
                              stat_fta=None, stat_ftm=None, stat_tov=None,
                              stat_oreb=None, stat_ast=None,
                              stat_stl=None, stat_blk=None, stat_dreb=None
                              ) -> Tuple[int, bool]:
        """Simulate a single possession: offense vs defense.

        Offense produces a number. Defense produces a number.
        The possession uses the blend: (off_rate + def_rate) / 2

        Returns (points_scored, got_offensive_rebound).
        When stat arrays are provided, records per-player stats in-place.
        """
        rng = self.rng
        cfg = self.config

        # ============================================================
        # Step 1: Select who uses the possession (offensive player)
        # ============================================================
        poss_share = off_arrays['possession_share'][off_lineup]
        share_sum = poss_share.sum()
        if share_sum <= 0:
            poss_share = np.ones(len(off_lineup))
            share_sum = poss_share.sum()
        probs = poss_share / share_sum
        player_local_idx = rng.choice(len(off_lineup), p=probs)
        player_idx = off_lineup[player_local_idx]

        # ============================================================
        # Step 2: Positional defensive matchup
        # Guards defend guards, wings defend wings, centers defend centers.
        # Find defenders whose position matches the offensive player,
        # and use THEIR defensive profile. Fallback to full lineup avg.
        # ============================================================
        off_positions = off_arrays['position_slots'][player_idx]  # e.g. ('G',) or ('G','W')
        def_position_slots = def_arrays['position_slots']

        # Find defenders that match the offensive player's position
        matched_defenders = []
        for d_idx in def_lineup:
            d_pos = def_position_slots[d_idx]
            # Check if any position overlaps
            if any(p in d_pos for p in off_positions):
                matched_defenders.append(d_idx)

        if len(matched_defenders) == 0:
            # No positional match — use full lineup average
            matched_defenders = list(def_lineup)

        matched = np.array(matched_defenders)
        def_fg2_allowed = np.mean(def_arrays['def_fg2_pct_allowed'][matched])
        def_fg3_allowed = np.mean(def_arrays['def_fg3_pct_allowed'][matched])
        def_tov_forced = np.mean(def_arrays['def_tov_forced_rate'][matched])
        def_oreb_allowed = np.mean(def_arrays['def_oreb_allowed_rate'][def_lineup])  # OREB is team-wide

        # Ref foul modifier
        ref_foul_mod = cfg.ref_foul_modifier
        if not is_home:
            ref_foul_mod += cfg.ref_home_bias

        # Game-state adjustments
        three_pt_boost = 0.0
        tov_boost = 0.0
        if game_state == 'trailing_big':
            three_pt_boost = 0.10
            tov_boost = 0.02

        # ============================================================
        # Step 3: Home court advantage adjustments
        # ============================================================
        hca_fg2 = cfg.home_court_fg2_bonus if is_home else -cfg.home_court_fg2_bonus
        hca_fg3 = cfg.home_court_fg3_bonus if is_home else -cfg.home_court_fg3_bonus
        hca_foul = cfg.home_court_foul_bonus if is_home else -cfg.home_court_foul_bonus

        # ============================================================
        # Step 4: Turnover check (offense TOV rate + defense forced TOV)
        # ============================================================
        off_tov = off_arrays['turnover_rate'][player_idx]
        # Weight offense 65%, defense 35% — the player matters more than the team D
        eff_tov = off_tov * 0.65 + def_tov_forced * 0.35 + tov_boost
        eff_tov = np.clip(eff_tov, 0.0, 0.35)
        if rng.random() < eff_tov:
            if stat_tov is not None:
                stat_tov[player_idx] += 1
            # ~60% of turnovers are steals
            if stat_stl is not None and rng.random() < 0.60:
                stl_rates = def_arrays['stl_per_poss'][def_lineup]
                stl_sum = stl_rates.sum()
                if stl_sum > 0:
                    stealer_local = rng.choice(len(def_lineup), p=stl_rates / stl_sum)
                    stat_stl[def_lineup[stealer_local]] += 1
            return 0, False

        # ============================================================
        # Step 4: Shooting foul check
        # ============================================================
        foul_rate = (off_arrays['foul_drawn_rate'][player_idx] + hca_foul) * ref_foul_mod
        if rng.random() < foul_rate:
            ft_pct = off_arrays['ft_pct'][player_idx]
            # Use player's actual 3pt foul rate instead of hardcoded 15%
            three_pt_foul_rate = off_arrays['three_pt_foul_rate'][player_idx]
            n_fts = 3 if rng.random() < three_pt_foul_rate else 2
            made = sum(1 for _ in range(n_fts) if rng.random() < ft_pct)
            if stat_fta is not None:
                stat_fta[player_idx] += n_fts
                stat_ftm[player_idx] += made
                stat_pts[player_idx] += made
            if def_arrays['n'] > 0:
                fouler = rng.integers(0, min(5, def_arrays['n']))
                if fouler < len(def_fouls):
                    def_fouls[fouler] += 1
            return made, False

        # ============================================================
        # Step 5: Field goal attempt
        # FG% = blend of (player's offensive FG% + defense's FG% allowed) / 2
        # ============================================================
        two_rate = off_arrays['two_pt_rate'][player_idx]
        three_rate = off_arrays['three_pt_rate'][player_idx] + three_pt_boost
        shot_total = two_rate + three_rate

        points = 0
        oreb = False

        if shot_total > 0 and rng.random() < (three_rate / shot_total):
            # === 3-POINT ATTEMPT ===
            if stat_fg3a is not None:
                stat_fg3a[player_idx] += 1
            off_fg3 = off_arrays['fg3_pct'][player_idx]
            eff_fg3 = off_fg3 * 0.65 + def_fg3_allowed * 0.35 + hca_fg3
            eff_fg3 = np.clip(eff_fg3, 0.20, 0.55)

            if rng.random() < eff_fg3:
                points = 3
                if stat_fg3m is not None:
                    stat_fg3m[player_idx] += 1
                    stat_pts[player_idx] += 3
                # Assist check: ~65% of made 3s are assisted
                if stat_ast is not None and rng.random() < 0.65:
                    ast_weights = off_arrays['ast_pct'][off_lineup].copy()
                    ast_weights[player_local_idx] = 0  # can't assist yourself
                    ast_sum = ast_weights.sum()
                    if ast_sum > 0:
                        passer_local = rng.choice(len(off_lineup), p=ast_weights / ast_sum)
                        stat_ast[off_lineup[passer_local]] += 1
                # And-1: use player's actual and-1 rate, scaled down for 3pt
                and1_rate_3 = off_arrays['and1_rate'][player_idx] * 0.2
                if rng.random() < and1_rate_3 * ref_foul_mod:
                    if stat_fta is not None:
                        stat_fta[player_idx] += 1
                    if rng.random() < off_arrays['ft_pct'][player_idx]:
                        points += 1
                        if stat_ftm is not None:
                            stat_ftm[player_idx] += 1
                            stat_pts[player_idx] += 1
                    if def_arrays['n'] > 0:
                        fouler = rng.integers(0, min(5, def_arrays['n']))
                        if fouler < len(def_fouls):
                            def_fouls[fouler] += 1
            else:
                # Block check: ~4% of 3PA are blocked
                if stat_blk is not None and rng.random() < 0.04:
                    blk_rates = def_arrays['blk_per_poss'][def_lineup]
                    blk_sum = blk_rates.sum()
                    if blk_sum > 0:
                        blocker_local = rng.choice(len(def_lineup), p=blk_rates / blk_sum)
                        stat_blk[def_lineup[blocker_local]] += 1
                # OREB: blend offensive rebounding + defensive rebounding allowed
                off_oreb = np.mean(off_arrays['oreb_rate'][off_lineup])
                eff_oreb = (off_oreb + def_oreb_allowed) / 2.0
                if rng.random() < eff_oreb * 0.7:
                    oreb = True
                    if stat_oreb is not None:
                        oreb_weights = off_arrays['oreb_rate'][off_lineup]
                        oreb_sum = oreb_weights.sum()
                        if oreb_sum > 0:
                            rebounder_local = rng.choice(len(off_lineup), p=oreb_weights / oreb_sum)
                            stat_oreb[off_lineup[rebounder_local]] += 1
                elif stat_dreb is not None:
                    # Defensive rebound
                    dreb_weights = def_arrays['dreb_rate'][def_lineup]
                    dreb_sum = dreb_weights.sum()
                    if dreb_sum > 0:
                        rebounder_local = rng.choice(len(def_lineup), p=dreb_weights / dreb_sum)
                        stat_dreb[def_lineup[rebounder_local]] += 1
        else:
            # === 2-POINT ATTEMPT ===
            if stat_fg2a is not None:
                stat_fg2a[player_idx] += 1
            off_fg2 = off_arrays['fg2_pct'][player_idx]
            eff_fg2 = off_fg2 * 0.65 + def_fg2_allowed * 0.35 + hca_fg2
            eff_fg2 = np.clip(eff_fg2, 0.25, 0.80)

            if rng.random() < eff_fg2:
                points = 2
                if stat_fg2m is not None:
                    stat_fg2m[player_idx] += 1
                    stat_pts[player_idx] += 2
                # Assist check: ~55% of made 2s are assisted
                if stat_ast is not None and rng.random() < 0.55:
                    ast_weights = off_arrays['ast_pct'][off_lineup].copy()
                    ast_weights[player_local_idx] = 0
                    ast_sum = ast_weights.sum()
                    if ast_sum > 0:
                        passer_local = rng.choice(len(off_lineup), p=ast_weights / ast_sum)
                        stat_ast[off_lineup[passer_local]] += 1
                # And-1: use player's actual and-1 rate
                and1_rate = off_arrays['and1_rate'][player_idx]
                if rng.random() < and1_rate * ref_foul_mod:
                    if stat_fta is not None:
                        stat_fta[player_idx] += 1
                    if rng.random() < off_arrays['ft_pct'][player_idx]:
                        points += 1
                        if stat_ftm is not None:
                            stat_ftm[player_idx] += 1
                            stat_pts[player_idx] += 1
                    if def_arrays['n'] > 0:
                        fouler = rng.integers(0, min(5, def_arrays['n']))
                        if fouler < len(def_fouls):
                            def_fouls[fouler] += 1
            else:
                # Block check: ~9% of 2PA are blocked
                if stat_blk is not None and rng.random() < 0.09:
                    blk_rates = def_arrays['blk_per_poss'][def_lineup]
                    blk_sum = blk_rates.sum()
                    if blk_sum > 0:
                        blocker_local = rng.choice(len(def_lineup), p=blk_rates / blk_sum)
                        stat_blk[def_lineup[blocker_local]] += 1
                off_oreb = np.mean(off_arrays['oreb_rate'][off_lineup])
                eff_oreb = (off_oreb + def_oreb_allowed) / 2.0
                if rng.random() < eff_oreb:
                    oreb = True
                    if stat_oreb is not None:
                        oreb_weights = off_arrays['oreb_rate'][off_lineup]
                        oreb_sum = oreb_weights.sum()
                        if oreb_sum > 0:
                            rebounder_local = rng.choice(len(off_lineup), p=oreb_weights / oreb_sum)
                            stat_oreb[off_lineup[rebounder_local]] += 1
                elif stat_dreb is not None:
                    dreb_weights = def_arrays['dreb_rate'][def_lineup]
                    dreb_sum = dreb_weights.sum()
                    if dreb_sum > 0:
                        rebounder_local = rng.choice(len(def_lineup), p=dreb_weights / dreb_sum)
                        stat_dreb[def_lineup[rebounder_local]] += 1

        # Non-shooting defensive foul
        if rng.random() < BASE_FOUL_RATE * 0.3 * ref_foul_mod:
            if def_arrays['n'] > 0:
                fouler = rng.integers(0, min(5, def_arrays['n']))
                if fouler < len(def_fouls):
                    def_fouls[fouler] += 1

        return points, oreb

    def simulate_batch(self, n_sims: int) -> List[GameResult]:
        """Run N simulations and return all results."""
        return [self.simulate() for _ in range(n_sims)]
