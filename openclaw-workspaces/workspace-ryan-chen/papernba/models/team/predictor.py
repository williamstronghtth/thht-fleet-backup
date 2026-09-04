"""
Baseline Game Predictor
=======================

Predicts NBA game scores using team ratings and home court advantage.

Approach (inspired by Christopher Long's log-score method):
1. Estimate possessions = avg of both teams' pace
2. Expected score = (team_off_rtg × opp_def_rtg / league_avg) × possessions / 100
3. Apply home court adjustment
4. Use log-score for better calibration of extreme values

Output: predicted home/away scores, spread, total
"""

import numpy as np
import pandas as pd
from typing import Optional, List
from .ratings import TeamRatings
from .home_court import HomeCourtModel
from ..player.impact import PlayerImpactModel
from ..player.streaks import StreakDetector
from ..referee.predictor import RefereePredictor
from ..coach.predictor import CoachPredictor


class BaselinePredictor:
    """Predict NBA game outcomes using team ratings."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.ratings = TeamRatings(db_path)
        self.home_court = HomeCourtModel(db_path)
        self.player_impact = PlayerImpactModel(db_path)
        self.streak_detector = StreakDetector(db_path)
        self.referee_predictor = RefereePredictor(db_path)
        self.coach_predictor = CoachPredictor(db_path)

    def predict_game(self, home_team_id: str, away_team_id: str,
                     game_date: pd.Timestamp, season_id: str,
                     home_inactive: Optional[List[str]] = None,
                     away_inactive: Optional[List[str]] = None,
                     ref_crew_ids: Optional[List[int]] = None,
                     use_coach: bool = False,
                     use_streaks: bool = False) -> Optional[dict]:
        """Predict the outcome of a game.
        
        Uses only data available before game_date (walk-forward safe).
        
        Args:
            home_team_id: Home team NBA ID
            away_team_id: Away team NBA ID
            game_date: Date of the game (predictions use only prior data)
            season_id: Season identifier (e.g., '22022')
            home_inactive: List of inactive player IDs for home team
            away_inactive: List of inactive player IDs for away team
            ref_crew_ids: List of official_ids for the referee crew
        
        Returns:
            dict with pred_home_pts, pred_away_pts, pred_spread, pred_total
            or None if insufficient data
        """
        # Get team ratings (walk-forward: only data before game_date)
        home_rating = self.ratings.get_team_rating_before_date(
            home_team_id, game_date, season_id)
        away_rating = self.ratings.get_team_rating_before_date(
            away_team_id, game_date, season_id)

        if home_rating is None or away_rating is None:
            return None

        # League average (walk-forward)
        lg_avg = self.ratings.league_average_before_date(season_id, game_date)

        # Home court advantage
        hca = self.home_court.get_home_advantage(season_id, before_date=game_date)

        # Predicted possessions = average of both teams' pace
        pred_poss = (home_rating['pace'] + away_rating['pace']) / 2

        # Log-score approach: work in log space for better calibration
        # ln(score) = ln(off_rtg) + ln(opp_def_rtg) - ln(lg_avg) + ln(poss/100)
        lg_off = lg_avg['off_rtg']

        # Home team expected score
        # home_off × away_def / league_avg × possessions / 100
        # With home court boost
        home_off_adj = home_rating['off_rtg'] * hca['off_boost']
        away_def_adj = away_rating['def_rtg'] / hca['def_boost']  # away team defends worse on road

        log_home_score = (np.log(home_off_adj) + np.log(away_def_adj)
                          - np.log(lg_off) + np.log(pred_poss / 100))
        pred_home_pts = np.exp(log_home_score)

        # Away team expected score (no home boost, opponent gets home defensive boost)
        away_off_adj = away_rating['off_rtg'] / hca['off_boost']  # away team scores less
        home_def_adj = home_rating['def_rtg'] * hca['def_boost']  # home team defends better

        log_away_score = (np.log(away_off_adj) + np.log(home_def_adj)
                          - np.log(lg_off) + np.log(pred_poss / 100))
        pred_away_pts = np.exp(log_away_score)

        pred_spread = pred_away_pts - pred_home_pts  # Negative = home favored
        pred_total = pred_home_pts + pred_away_pts

        # Apply player availability adjustments if provided
        home_scoring_adj = 0.0
        away_scoring_adj = 0.0

        if home_inactive is not None or away_inactive is not None:
            # Per-player impact estimation using individual game log profiles
            if home_inactive:
                home_scoring_adj = self.player_impact.get_team_adjustment(
                    str(home_team_id), [str(p) for p in home_inactive], game_date)
            if away_inactive:
                away_scoring_adj = self.player_impact.get_team_adjustment(
                    str(away_team_id), [str(p) for p in away_inactive], game_date)

        # Convert to margin adjustment (spread-only, preserve total)
        # home_scoring_adj and away_scoring_adj are both negative (team loses pts)
        # margin_adj = change in home margin = home_impact - away_impact
        # If home is hurt more (larger negative), margin_adj is negative (home worse off)
        margin_adj = home_scoring_adj - away_scoring_adj

        # Apply as spread adjustment, split evenly between teams to preserve total
        adj_home_pts = pred_home_pts + margin_adj / 2
        adj_away_pts = pred_away_pts - margin_adj / 2
        adj_spread = adj_away_pts - adj_home_pts
        adj_total = adj_home_pts + adj_away_pts  # preserved

        # Referee crew adjustments (Layer 3)
        ref_total_adj = 0.0
        ref_spread_adj = 0.0
        ref_n_refs = 0

        if ref_crew_ids is not None and len(ref_crew_ids) > 0:
            ref_adj = self.referee_predictor.get_adjustment(
                ref_crew_ids, game_date, season_id)
            ref_total_adj = ref_adj['total_adj']
            ref_spread_adj = ref_adj['spread_adj']
            ref_n_refs = ref_adj['n_refs']

        # Apply ref adjustments on top of player-adjusted predictions
        # Total adjustment: split evenly between teams
        ref_adj_home_pts = adj_home_pts + ref_total_adj / 2
        ref_adj_away_pts = adj_away_pts + ref_total_adj / 2
        # Spread adjustment: negative spread_adj = home favored more
        ref_adj_home_pts -= ref_spread_adj / 2
        ref_adj_away_pts += ref_spread_adj / 2

        ref_adj_spread = ref_adj_away_pts - ref_adj_home_pts
        ref_adj_total = ref_adj_home_pts + ref_adj_away_pts

        # Coach adjustments (Layer 4)
        coach_spread_adj = 0.0
        coach_total_adj = 0.0
        coach_n_profiles = 0

        if use_coach:
            coach_adj = self.coach_predictor.get_adjustment(
                home_team_id=home_team_id,
                away_team_id=away_team_id,
                game_date=game_date,
                season_id=season_id,
                predicted_spread=ref_adj_spread,
                predicted_total=ref_adj_total,
            )
            coach_spread_adj = coach_adj['spread_adj']
            coach_total_adj = coach_adj['total_adj']
            coach_n_profiles = coach_adj['n_profiles']

        # Apply coach adjustments on top of ref-adjusted predictions
        final_home_pts = ref_adj_home_pts - coach_spread_adj / 2 + coach_total_adj / 2
        final_away_pts = ref_adj_away_pts + coach_spread_adj / 2 + coach_total_adj / 2
        final_spread = final_away_pts - final_home_pts
        final_total = final_home_pts + final_away_pts

        # Streak adjustments (Layer 5)
        home_streak_adj = 0.0
        away_streak_adj = 0.0
        home_n_hot = 0
        home_n_cold = 0
        away_n_hot = 0
        away_n_cold = 0
        home_weighted_streak = 0.0
        away_weighted_streak = 0.0

        if use_streaks:
            # Get active players for each team
            home_active = self.streak_detector.get_team_active_players(
                int(home_team_id), game_date,
                inactive_ids=[int(p) for p in home_inactive] if home_inactive else None
            )
            away_active = self.streak_detector.get_team_active_players(
                int(away_team_id), game_date,
                inactive_ids=[int(p) for p in away_inactive] if away_inactive else None
            )

            home_streak_info = self.streak_detector.get_team_streak_adjustment(
                int(home_team_id), home_active, game_date)
            away_streak_info = self.streak_detector.get_team_streak_adjustment(
                int(away_team_id), away_active, game_date)

            home_streak_adj = home_streak_info['streak_adj']
            away_streak_adj = away_streak_info['streak_adj']
            home_n_hot = home_streak_info['n_hot']
            home_n_cold = home_streak_info['n_cold']
            away_n_hot = away_streak_info['n_hot']
            away_n_cold = away_streak_info['n_cold']
            home_weighted_streak = home_streak_info['weighted_streak']
            away_weighted_streak = away_streak_info['weighted_streak']

            # Apply streak adjustments additively on top of final
            final_home_pts += home_streak_adj
            final_away_pts += away_streak_adj
            final_spread = final_away_pts - final_home_pts
            final_total = final_home_pts + final_away_pts

        return {
            'pred_home_pts': round(pred_home_pts, 1),
            'pred_away_pts': round(pred_away_pts, 1),
            'pred_spread': round(pred_spread, 1),
            'pred_total': round(pred_total, 1),
            'adj_home_pts': round(adj_home_pts, 1),
            'adj_away_pts': round(adj_away_pts, 1),
            'adj_spread': round(adj_spread, 1),
            'adj_total': round(adj_total, 1),
            'home_adj': round(home_scoring_adj, 2),
            'away_adj': round(away_scoring_adj, 2),
            'ref_adj_home_pts': round(ref_adj_home_pts, 1),
            'ref_adj_away_pts': round(ref_adj_away_pts, 1),
            'ref_adj_spread': round(ref_adj_spread, 1),
            'ref_adj_total': round(ref_adj_total, 1),
            'ref_total_adj': round(ref_total_adj, 2),
            'ref_spread_adj': round(ref_spread_adj, 2),
            'ref_n_refs': ref_n_refs,
            'pred_poss': round(pred_poss, 1),
            'home_off_rtg': round(home_rating['off_rtg'], 1),
            'home_def_rtg': round(home_rating['def_rtg'], 1),
            'away_off_rtg': round(away_rating['off_rtg'], 1),
            'away_def_rtg': round(away_rating['def_rtg'], 1),
            'hca_margin': round(hca['margin'], 2),
            'coach_spread_adj': round(coach_spread_adj, 2),
            'coach_total_adj': round(coach_total_adj, 2),
            'coach_n_profiles': coach_n_profiles,
            'final_home_pts': round(final_home_pts, 1),
            'final_away_pts': round(final_away_pts, 1),
            'final_spread': round(final_spread, 1),
            'final_total': round(final_total, 1),
            'home_streak_adj': round(home_streak_adj, 3),
            'away_streak_adj': round(away_streak_adj, 3),
            'home_n_hot': home_n_hot,
            'home_n_cold': home_n_cold,
            'away_n_hot': away_n_hot,
            'away_n_cold': away_n_cold,
            'home_weighted_streak': home_weighted_streak,
            'away_weighted_streak': away_weighted_streak,
        }
