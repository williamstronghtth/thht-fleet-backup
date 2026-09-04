"""
Referee Profile Model (Layer 3)
================================

Builds statistical profiles for each NBA referee based on game-level data.
Key metrics per referee:
- Total points impact (vs league average)
- Foul rate impact
- Free throw rate impact
- Pace impact
- Home foul differential (bias)
- Scoring variance

All metrics use Bayesian shrinkage toward league average for small samples.
Walk-forward safe: only uses data strictly before the prediction date.
"""

import duckdb
import numpy as np
import pandas as pd
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, field


@dataclass
class RefereeProfile:
    """Statistical profile for a single referee."""
    official_id: int
    name: str
    games: int = 0
    # Raw averages (for this ref's games)
    avg_total_pts: float = 0.0
    avg_total_pf: float = 0.0
    avg_total_fta: float = 0.0
    avg_pace: float = 0.0
    avg_home_pf: float = 0.0
    avg_away_pf: float = 0.0
    # Deviations from league average (shrunk)
    total_pts_impact: float = 0.0    # key metric
    total_pf_impact: float = 0.0
    total_fta_impact: float = 0.0
    pace_impact: float = 0.0
    home_foul_diff: float = 0.0      # positive = more fouls on away team
    scoring_variance: float = 0.0
    # Shrinkage factor applied
    shrinkage: float = 0.0


class RefereeProfileModel:
    """Build and query referee profiles from historical game data."""

    # Bayesian shrinkage prior strength (number of "phantom" games at league avg)
    PRIOR_GAMES = 50

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ref_game_data: Optional[pd.DataFrame] = None
        self._profiles_cache: Dict[Tuple[str, str], Dict[int, RefereeProfile]] = {}

    def _load_ref_game_data(self):
        """Load all referee-game data joined with game stats. Cached."""
        if self._ref_game_data is not None:
            return

        con = duckdb.connect(self.db_path, read_only=True)
        df = con.execute("""
            SELECT 
                o.game_id,
                o.official_id,
                o.first_name || ' ' || o.last_name as ref_name,
                g.game_date,
                g.season_id,
                g.pts_home,
                g.pts_away,
                g.pts_home + g.pts_away as total_pts,
                g.pf_home,
                g.pf_away,
                g.pf_home + g.pf_away as total_pf,
                g.fta_home,
                g.fta_away,
                g.fta_home + g.fta_away as total_fta,
                g.fga_home, g.oreb_home, g.tov_home,
                g.fga_away, g.oreb_away, g.tov_away
            FROM officials o
            JOIN game g ON o.game_id = g.game_id
            WHERE g.season_type = 'Regular Season'
              AND g.pts_home IS NOT NULL
              AND g.pf_home IS NOT NULL
              AND g.fga_home IS NOT NULL
              AND g.fta_home IS NOT NULL
        """).fetchdf()
        con.close()

        df['game_date'] = pd.to_datetime(df['game_date'])

        # Estimate possessions for pace
        def est_poss(row, side):
            fga = row[f'fga_{side}']
            oreb = row[f'oreb_{side}']
            tov = row[f'tov_{side}']
            fta = row[f'fta_{side}']
            if pd.isna(fga) or pd.isna(oreb) or pd.isna(tov) or pd.isna(fta):
                return np.nan
            return fga - oreb + tov + 0.44 * fta

        df['poss_home'] = df.apply(lambda r: est_poss(r, 'home'), axis=1)
        df['poss_away'] = df.apply(lambda r: est_poss(r, 'away'), axis=1)
        df['total_poss'] = (df['poss_home'] + df['poss_away']) / 2

        # Drop rows with NaN possessions
        df = df.dropna(subset=['total_poss']).reset_index(drop=True)

        self._ref_game_data = df

    def _build_profiles(self, before_date: pd.Timestamp,
                        season_id: str) -> Dict[int, RefereeProfile]:
        """Build referee profiles using only data before the given date.
        
        Uses data from the current season and previous 2 seasons,
        with recency weighting.
        """
        cache_key = (str(before_date.date()), season_id)
        if cache_key in self._profiles_cache:
            return self._profiles_cache[cache_key]

        self._load_ref_game_data()
        df = self._ref_game_data

        # Filter to before_date
        df = df[df['game_date'] < before_date].copy()

        if df.empty:
            self._profiles_cache[cache_key] = {}
            return {}

        # Use last 3 seasons of data for stability
        try:
            year = int(season_id[1:])
            valid_seasons = [f"2{y}" for y in range(year - 2, year + 1)]
        except ValueError:
            valid_seasons = df['season_id'].unique()

        df = df[df['season_id'].isin(valid_seasons)]

        if df.empty:
            self._profiles_cache[cache_key] = {}
            return {}

        # League averages (across all games in this window)
        # Each game has ~3 refs, so use unique game-level stats
        game_stats = df.drop_duplicates(subset='game_id')
        lg_avg_total_pts = game_stats['total_pts'].mean()
        lg_avg_total_pf = game_stats['total_pf'].mean()
        lg_avg_total_fta = game_stats['total_fta'].mean()
        lg_avg_pace = game_stats['total_poss'].mean()
        lg_avg_home_pf = game_stats['pf_home'].mean()
        lg_avg_away_pf = game_stats['pf_away'].mean()
        lg_scoring_var = game_stats['total_pts'].std()

        # Per-referee aggregation
        ref_agg = df.groupby(['official_id', 'ref_name']).agg(
            games=('game_id', 'nunique'),
            avg_total_pts=('total_pts', 'mean'),
            avg_total_pf=('total_pf', 'mean'),
            avg_total_fta=('total_fta', 'mean'),
            avg_pace=('total_poss', 'mean'),
            avg_home_pf=('pf_home', 'mean'),
            avg_away_pf=('pf_away', 'mean'),
            std_total_pts=('total_pts', 'std'),
        ).reset_index()

        profiles = {}
        for _, row in ref_agg.iterrows():
            n = row['games']
            # Bayesian shrinkage: weighted avg of ref's data and league prior
            # shrinkage = n / (n + prior_games)
            shrink = n / (n + self.PRIOR_GAMES)

            raw_pts_impact = row['avg_total_pts'] - lg_avg_total_pts
            raw_pf_impact = row['avg_total_pf'] - lg_avg_total_pf
            raw_fta_impact = row['avg_total_fta'] - lg_avg_total_fta
            raw_pace_impact = row['avg_pace'] - lg_avg_pace
            raw_home_diff = (row['avg_away_pf'] - row['avg_home_pf']) - (lg_avg_away_pf - lg_avg_home_pf)

            profile = RefereeProfile(
                official_id=int(row['official_id']),
                name=row['ref_name'],
                games=int(n),
                avg_total_pts=row['avg_total_pts'],
                avg_total_pf=row['avg_total_pf'],
                avg_total_fta=row['avg_total_fta'],
                avg_pace=row['avg_pace'],
                avg_home_pf=row['avg_home_pf'],
                avg_away_pf=row['avg_away_pf'],
                # Shrunk impacts
                total_pts_impact=raw_pts_impact * shrink,
                total_pf_impact=raw_pf_impact * shrink,
                total_fta_impact=raw_fta_impact * shrink,
                pace_impact=raw_pace_impact * shrink,
                home_foul_diff=raw_home_diff * shrink,
                scoring_variance=row['std_total_pts'] if not pd.isna(row['std_total_pts']) else lg_scoring_var,
                shrinkage=shrink,
            )
            profiles[int(row['official_id'])] = profile

        self._profiles_cache[cache_key] = profiles
        return profiles

    def get_ref_profile(self, official_id: int, before_date: pd.Timestamp,
                        season_id: str) -> Optional[RefereeProfile]:
        """Get a single referee's profile."""
        profiles = self._build_profiles(before_date, season_id)
        return profiles.get(official_id)

    def get_crew_adjustment(self, crew_ids: List[int], before_date: pd.Timestamp,
                            season_id: str) -> Dict[str, float]:
        """Calculate the combined adjustment for a 3-ref crew.
        
        Returns the average of individual ref impacts, which gives
        the expected deviation from league average for this crew.
        
        Returns:
            dict with total_pts_adj, total_pf_adj, total_fta_adj,
            pace_adj, home_foul_adj, and n_refs_found
        """
        profiles = self._build_profiles(before_date, season_id)

        found_profiles = []
        for rid in crew_ids:
            p = profiles.get(rid)
            if p is not None:
                found_profiles.append(p)

        if not found_profiles:
            return {
                'total_pts_adj': 0.0,
                'total_pf_adj': 0.0,
                'total_fta_adj': 0.0,
                'pace_adj': 0.0,
                'home_foul_adj': 0.0,
                'n_refs_found': 0,
            }

        n = len(found_profiles)
        return {
            'total_pts_adj': sum(p.total_pts_impact for p in found_profiles) / n,
            'total_pf_adj': sum(p.total_pf_impact for p in found_profiles) / n,
            'total_fta_adj': sum(p.total_fta_impact for p in found_profiles) / n,
            'pace_adj': sum(p.pace_impact for p in found_profiles) / n,
            'home_foul_adj': sum(p.home_foul_diff for p in found_profiles) / n,
            'n_refs_found': n,
        }

    def get_all_profiles(self, before_date: pd.Timestamp,
                         season_id: str) -> List[RefereeProfile]:
        """Get all referee profiles (for analysis/reporting)."""
        profiles = self._build_profiles(before_date, season_id)
        return sorted(profiles.values(), key=lambda p: p.total_pts_impact, reverse=True)

    def clear_cache(self):
        """Clear profile cache."""
        self._profiles_cache.clear()

    def get_analysis(self, before_date: pd.Timestamp, season_id: str) -> Dict:
        """Get interesting analysis about referee impacts.
        
        Returns dict with top/bottom refs, home bias stats, variance analysis.
        """
        self._load_ref_game_data()
        df = self._ref_game_data
        df = df[df['game_date'] < before_date].copy()

        try:
            year = int(season_id[1:])
            valid_seasons = [f"2{y}" for y in range(year - 2, year + 1)]
        except ValueError:
            valid_seasons = df['season_id'].unique()

        df = df[df['season_id'].isin(valid_seasons)]
        game_stats = df.drop_duplicates(subset='game_id')

        profiles = self.get_all_profiles(before_date, season_id)
        # Filter to refs with decent sample
        experienced = [p for p in profiles if p.games >= 30]

        # Top/bottom total scorers
        top_total = sorted(experienced, key=lambda p: p.total_pts_impact, reverse=True)[:10]
        bottom_total = sorted(experienced, key=lambda p: p.total_pts_impact)[:10]

        # Most fouls called
        top_fouls = sorted(experienced, key=lambda p: p.total_pf_impact, reverse=True)[:10]

        # Home bias — refs with biggest away-foul differential
        top_home_bias = sorted(experienced, key=lambda p: p.home_foul_diff, reverse=True)[:10]

        # Variance explained: R² of ref assignment on totals
        # Simple approach: compare variance of ref-game totals vs overall
        if len(experienced) > 10 and len(game_stats) > 100:
            overall_var = game_stats['total_pts'].var()
            # Create ref-explained variance via mean per-ref total
            ref_means = df.groupby('official_id')['total_pts'].mean()
            # Map each game-ref to ref mean
            df_temp = df.merge(ref_means.rename('ref_mean_pts'), on='official_id')
            between_var = df_temp.groupby('game_id')['ref_mean_pts'].mean().var()
            r_squared = between_var / overall_var if overall_var > 0 else 0
        else:
            r_squared = 0.0

        return {
            'top_total_refs': top_total,
            'bottom_total_refs': bottom_total,
            'top_foul_refs': top_fouls,
            'top_home_bias_refs': top_home_bias,
            'variance_explained_r2': r_squared,
            'n_refs_analyzed': len(experienced),
            'n_games_used': len(game_stats),
        }
