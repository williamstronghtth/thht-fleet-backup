"""
NBA Betting Model V4
====================
Combines multiple factors for spread predictions:
1. Net Rating (baseline team strength)
2. Four Factors matchups (offense vs defense)
3. Rest/B2B adjustments
4. Last 10 games recency weighting
5. Injury adjustments (stars + rotation players)
6. Home court advantage (+ altitude)

Built from research: Oliver, Winston, Pardo, Miller, Buchdahl, etc.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# =============================================================================
# CONFIGURATION
# =============================================================================

# Factor weights (should sum to 1.0)
WEIGHTS = {
    'net_rating': 0.35,      # Baseline team strength
    'four_factors': 0.35,    # Matchup-based efficiency
    'recency': 0.20,         # Last 10 games trend
    'rest': 0.10,            # Schedule factors
}

# Home court advantage
HCA_BASE = 3.5  # League average
HCA_ALTITUDE = {'DEN': 1.5, 'UTA': 0.5}  # Altitude bonuses

# Rest adjustments (points)
REST_ADJUSTMENTS = {
    'b2b': -3.0,           # Back-to-back
    '3_in_4': -2.0,        # 3 games in 4 nights
    '4_in_5': -2.5,        # 4 games in 5 nights
    'rest_3plus': 1.0,     # 3+ days rest
    'travel_cross': -0.5,  # Cross-country travel
}

# Injury impact by minutes played
def injury_impact(mpg: float, is_star: bool = False) -> float:
    """Calculate point impact of missing player based on minutes."""
    if is_star:  # Known stars get boosted
        if mpg >= 32: return 7.0   # MVP level
        if mpg >= 28: return 5.0   # All-NBA
        if mpg >= 24: return 3.5   # All-Star
    # Minutes-based for others
    if mpg >= 30: return 3.0      # High-minute starter
    if mpg >= 25: return 2.0      # Quality starter
    if mpg >= 20: return 1.5      # Rotation player
    if mpg >= 15: return 1.0      # Bench contributor
    if mpg >= 10: return 0.5      # Deep rotation
    return 0.0

# Star players (for boosted injury impact)
STAR_PLAYERS = {
    # MVP Tier
    'Nikola Jokic', 'Shai Gilgeous-Alexander', 'Luka Doncic', 'Giannis Antetokounmpo',
    'Jayson Tatum', 'Joel Embiid', 'Stephen Curry', 'Kevin Durant',
    # All-NBA Tier
    'Anthony Davis', 'Jaylen Brown', 'Donovan Mitchell', 'Trae Young',
    'Ja Morant', 'Tyrese Haliburton', 'Anthony Edwards', 'LaMelo Ball',
    'Devin Booker', 'Bam Adebayo', 'Karl-Anthony Towns', 'Evan Mobley',
    'Scottie Barnes', 'Paolo Banchero', 'Chet Holmgren', 'Victor Wembanyama',
    'De\'Aaron Fox', 'Darius Garland', 'Jalen Brunson', 'Tyler Herro',
    'Damian Lillard', 'Jimmy Butler', 'Kawhi Leonard', 'Paul George',
    'Zion Williamson', 'Brandon Ingram', 'Alperen Sengun', 'Jalen Green',
}

# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class FourFactors:
    """Four Factors for a team (offense or defense)."""
    efg_pct: float      # Effective FG%
    tov_pct: float      # Turnover %
    orb_pct: float      # Offensive Rebound % (or DRB% for defense)
    ft_rate: float      # Free Throw Rate (FTA/FGA)
    
    def to_points(self, is_offense: bool = True) -> float:
        """Convert Four Factors to estimated point differential contribution."""
        # Weights from Dean Oliver's research
        efg_weight = 0.40
        tov_weight = 0.25
        orb_weight = 0.20
        ft_weight = 0.15
        
        # League averages (approximate)
        lg_efg = 0.545
        lg_tov = 0.13
        lg_orb = 0.26
        lg_ft = 0.25
        
        # Calculate deviations from league average
        efg_diff = (self.efg_pct - lg_efg) * 100  # Convert to percentage points
        tov_diff = (lg_tov - self.tov_pct) * 100 if is_offense else (self.tov_pct - lg_tov) * 100
        orb_diff = (self.orb_pct - lg_orb) * 100
        ft_diff = (self.ft_rate - lg_ft) * 100
        
        # Weight and sum (roughly 1 pct point = 1 point of margin)
        total = (efg_diff * efg_weight + 
                 tov_diff * tov_weight + 
                 orb_diff * orb_weight + 
                 ft_diff * ft_weight)
        
        return total

@dataclass
class TeamData:
    """All data for a team."""
    name: str
    abbrev: str
    net_rating: float
    off_four_factors: FourFactors
    def_four_factors: FourFactors
    last_10_net: float  # Net rating over last 10 games
    games_schedule: List[datetime]  # Recent game dates
    injuries: List[Tuple[str, float, str]]  # (player_name, mpg, status)

@dataclass 
class GamePrediction:
    """Model prediction for a game."""
    away: str
    home: str
    predicted_margin: float  # Positive = home wins
    spread: float  # Vegas spread (positive = home dog)
    edge: float
    edge_pct: float  # Win probability
    confidence: str  # HIGH/MED/LOW
    factors_breakdown: Dict[str, float]

# =============================================================================
# CORE MODEL
# =============================================================================

class NBAModelV4:
    """V4 NBA Betting Model."""
    
    def __init__(self):
        self.teams: Dict[str, TeamData] = {}
        self.league_avg_net = 0.0
        
    def load_team_data(self, team_data: Dict):
        """Load team data from dictionary."""
        for abbrev, data in team_data.items():
            off_ff = FourFactors(
                efg_pct=data.get('off_efg', 0.545),
                tov_pct=data.get('off_tov', 0.13),
                orb_pct=data.get('orb_pct', 0.26),
                ft_rate=data.get('off_ft_rate', 0.25)
            )
            def_ff = FourFactors(
                efg_pct=data.get('def_efg', 0.545),
                tov_pct=data.get('def_tov', 0.13),
                orb_pct=data.get('drb_pct', 0.74),
                ft_rate=data.get('def_ft_rate', 0.25)
            )
            self.teams[abbrev] = TeamData(
                name=data.get('name', abbrev),
                abbrev=abbrev,
                net_rating=data.get('net_rating', 0.0),
                off_four_factors=off_ff,
                def_four_factors=def_ff,
                last_10_net=data.get('last_10_net', data.get('net_rating', 0.0)),
                games_schedule=data.get('schedule', []),
                injuries=data.get('injuries', [])
            )
    
    def calculate_rest_adjustment(self, team: TeamData, game_date: datetime) -> float:
        """Calculate rest-based adjustment."""
        if not team.games_schedule:
            return 0.0
        
        # Sort games before this date
        past_games = [g for g in team.games_schedule if g < game_date]
        if not past_games:
            return 0.0
        
        past_games.sort(reverse=True)
        last_game = past_games[0]
        days_rest = (game_date - last_game).days
        
        adjustment = 0.0
        
        # Back-to-back
        if days_rest == 1:
            adjustment += REST_ADJUSTMENTS['b2b']
        
        # 3+ days rest bonus
        if days_rest >= 3:
            adjustment += REST_ADJUSTMENTS['rest_3plus']
        
        # Check for 3 in 4 nights
        games_in_4 = len([g for g in past_games[:3] if (game_date - g).days <= 4])
        if games_in_4 >= 3:
            adjustment += REST_ADJUSTMENTS['3_in_4']
        
        return adjustment
    
    def calculate_injury_adjustment(self, team: TeamData) -> float:
        """Calculate total injury impact for a team."""
        total = 0.0
        for player_name, mpg, status in team.injuries:
            if status.upper() in ['OUT', 'DOUBTFUL']:
                is_star = player_name in STAR_PLAYERS
                total += injury_impact(mpg, is_star)
            elif status.upper() in ['QUESTIONABLE', 'GTD', 'DAY-TO-DAY']:
                # 50% weight for questionable players
                is_star = player_name in STAR_PLAYERS
                total += injury_impact(mpg, is_star) * 0.5
        return total
    
    def calculate_four_factors_matchup(self, offense: TeamData, defense: TeamData) -> float:
        """Calculate expected point differential from Four Factors matchup."""
        off_ff = offense.off_four_factors
        def_ff = defense.def_four_factors
        
        # Matchup-adjusted Four Factors (average of offense skill and defense weakness)
        # Higher is better for offense
        
        # eFG%: offense wants high, defense wants to allow low
        expected_efg = (off_ff.efg_pct + def_ff.efg_pct) / 2
        
        # TOV%: offense wants low, defense wants to force high
        expected_tov = (off_ff.tov_pct + def_ff.tov_pct) / 2
        
        # ORB%: offense wants high, defense wants low (drb_pct)
        expected_orb = (off_ff.orb_pct + (1 - def_ff.orb_pct)) / 2
        
        # FT Rate: offense wants high, defense wants to allow low
        expected_ft = (off_ff.ft_rate + def_ff.ft_rate) / 2
        
        # Convert to points
        matchup_ff = FourFactors(expected_efg, expected_tov, expected_orb, expected_ft)
        return matchup_ff.to_points(is_offense=True)
    
    def predict_game(self, away_abbrev: str, home_abbrev: str, 
                     spread: float, game_date: datetime = None) -> GamePrediction:
        """Generate prediction for a single game."""
        
        if game_date is None:
            game_date = datetime.now()
        
        away = self.teams.get(away_abbrev)
        home = self.teams.get(home_abbrev)
        
        if not away or not home:
            raise ValueError(f"Team not found: {away_abbrev} or {home_abbrev}")
        
        factors = {}
        
        # 1. NET RATING COMPONENT
        net_diff = home.net_rating - away.net_rating
        factors['net_rating'] = net_diff
        
        # 2. FOUR FACTORS MATCHUP COMPONENT
        home_off_vs_away_def = self.calculate_four_factors_matchup(home, away)
        away_off_vs_home_def = self.calculate_four_factors_matchup(away, home)
        ff_diff = home_off_vs_away_def - away_off_vs_home_def
        factors['four_factors'] = ff_diff
        
        # 3. RECENCY COMPONENT (Last 10 games)
        recency_diff = home.last_10_net - away.last_10_net
        factors['recency'] = recency_diff
        
        # 4. REST COMPONENT
        home_rest = self.calculate_rest_adjustment(home, game_date)
        away_rest = self.calculate_rest_adjustment(away, game_date)
        rest_diff = home_rest - away_rest
        factors['rest'] = rest_diff
        
        # 5. HOME COURT ADVANTAGE
        hca = HCA_BASE + HCA_ALTITUDE.get(home_abbrev, 0)
        factors['hca'] = hca
        
        # 6. INJURY ADJUSTMENTS
        home_inj = self.calculate_injury_adjustment(home)
        away_inj = self.calculate_injury_adjustment(away)
        inj_diff = away_inj - home_inj  # Positive = home benefits from away injuries
        factors['injuries'] = inj_diff
        
        # COMBINE WEIGHTED FACTORS
        weighted_diff = (
            factors['net_rating'] * WEIGHTS['net_rating'] +
            factors['four_factors'] * WEIGHTS['four_factors'] +
            factors['recency'] * WEIGHTS['recency'] +
            factors['rest'] * WEIGHTS['rest']
        )
        
        # Add non-weighted factors
        predicted_margin = weighted_diff + hca + inj_diff
        
        # CALCULATE EDGE
        # spread > 0 means home is underdog
        # edge_on_home = predicted_margin + spread
        edge = predicted_margin + spread
        
        # Determine which side to bet
        if edge > 0:
            # Bet home
            final_edge = edge
        else:
            # Bet away
            final_edge = -edge
        
        # Convert edge to win probability (rough approximation)
        # Using ~4.5 points per 10% probability
        edge_pct = 50 + (final_edge / 4.5) * 10
        edge_pct = max(min(edge_pct, 85), 50)  # Cap at 50-85%
        
        # Confidence level
        if final_edge >= 6:
            confidence = 'HIGH'
        elif final_edge >= 3:
            confidence = 'MED'
        else:
            confidence = 'LOW'
        
        return GamePrediction(
            away=away_abbrev,
            home=home_abbrev,
            predicted_margin=predicted_margin,
            spread=spread,
            edge=edge,
            edge_pct=edge_pct,
            confidence=confidence,
            factors_breakdown=factors
        )


# =============================================================================
# DATA: CURRENT TEAM STATS (2025-26 Season)
# =============================================================================

TEAM_DATA_2026 = {
    'ATL': {'name': 'Atlanta Hawks', 'net_rating': -2.7, 'last_10_net': -3.5,
            'off_efg': 0.548, 'off_tov': 0.128, 'orb_pct': 0.268, 'off_ft_rate': 0.252,
            'def_efg': 0.562, 'def_tov': 0.118, 'drb_pct': 0.720, 'def_ft_rate': 0.268},
    'BOS': {'name': 'Boston Celtics', 'net_rating': 9.7, 'last_10_net': 5.2,
            'off_efg': 0.572, 'off_tov': 0.122, 'orb_pct': 0.252, 'off_ft_rate': 0.238,
            'def_efg': 0.522, 'def_tov': 0.142, 'drb_pct': 0.768, 'def_ft_rate': 0.232},
    'BKN': {'name': 'Brooklyn Nets', 'net_rating': -6.6, 'last_10_net': -5.8,
            'off_efg': 0.528, 'off_tov': 0.138, 'orb_pct': 0.248, 'off_ft_rate': 0.228,
            'def_efg': 0.558, 'def_tov': 0.122, 'drb_pct': 0.712, 'def_ft_rate': 0.258},
    'CHA': {'name': 'Charlotte Hornets', 'net_rating': -8.4, 'last_10_net': -7.2,
            'off_efg': 0.518, 'off_tov': 0.142, 'orb_pct': 0.262, 'off_ft_rate': 0.242,
            'def_efg': 0.565, 'def_tov': 0.115, 'drb_pct': 0.705, 'def_ft_rate': 0.272},
    'CHI': {'name': 'Chicago Bulls', 'net_rating': -4.7, 'last_10_net': -6.1,
            'off_efg': 0.532, 'off_tov': 0.132, 'orb_pct': 0.255, 'off_ft_rate': 0.235,
            'def_efg': 0.552, 'def_tov': 0.125, 'drb_pct': 0.722, 'def_ft_rate': 0.248},
    'CLE': {'name': 'Cleveland Cavaliers', 'net_rating': 9.6, 'last_10_net': 7.8,
            'off_efg': 0.568, 'off_tov': 0.118, 'orb_pct': 0.272, 'off_ft_rate': 0.245,
            'def_efg': 0.518, 'def_tov': 0.138, 'drb_pct': 0.762, 'def_ft_rate': 0.225},
    'DAL': {'name': 'Dallas Mavericks', 'net_rating': 1.7, 'last_10_net': -1.2,
            'off_efg': 0.552, 'off_tov': 0.125, 'orb_pct': 0.258, 'off_ft_rate': 0.248,
            'def_efg': 0.545, 'def_tov': 0.128, 'drb_pct': 0.738, 'def_ft_rate': 0.252},
    'DEN': {'name': 'Denver Nuggets', 'net_rating': 3.6, 'last_10_net': 4.8,
            'off_efg': 0.558, 'off_tov': 0.115, 'orb_pct': 0.285, 'off_ft_rate': 0.255,
            'def_efg': 0.542, 'def_tov': 0.125, 'drb_pct': 0.745, 'def_ft_rate': 0.248},
    'DET': {'name': 'Detroit Pistons', 'net_rating': -1.3, 'last_10_net': 0.5,
            'off_efg': 0.538, 'off_tov': 0.128, 'orb_pct': 0.275, 'off_ft_rate': 0.258,
            'def_efg': 0.548, 'def_tov': 0.128, 'drb_pct': 0.728, 'def_ft_rate': 0.252},
    'GSW': {'name': 'Golden State Warriors', 'net_rating': -2.3, 'last_10_net': -4.5,
            'off_efg': 0.542, 'off_tov': 0.135, 'orb_pct': 0.245, 'off_ft_rate': 0.225,
            'def_efg': 0.548, 'def_tov': 0.132, 'drb_pct': 0.735, 'def_ft_rate': 0.242},
    'HOU': {'name': 'Houston Rockets', 'net_rating': 3.7, 'last_10_net': 5.2,
            'off_efg': 0.548, 'off_tov': 0.122, 'orb_pct': 0.295, 'off_ft_rate': 0.268,
            'def_efg': 0.528, 'def_tov': 0.135, 'drb_pct': 0.752, 'def_ft_rate': 0.238},
    'IND': {'name': 'Indiana Pacers', 'net_rating': 0.3, 'last_10_net': -2.8,
            'off_efg': 0.552, 'off_tov': 0.138, 'orb_pct': 0.268, 'off_ft_rate': 0.262,
            'def_efg': 0.555, 'def_tov': 0.125, 'drb_pct': 0.718, 'def_ft_rate': 0.265},
    'LAC': {'name': 'LA Clippers', 'net_rating': 0.7, 'last_10_net': 2.1,
            'off_efg': 0.545, 'off_tov': 0.125, 'orb_pct': 0.258, 'off_ft_rate': 0.242,
            'def_efg': 0.542, 'def_tov': 0.128, 'drb_pct': 0.742, 'def_ft_rate': 0.245},
    'LAL': {'name': 'Los Angeles Lakers', 'net_rating': 0.7, 'last_10_net': -0.5,
            'off_efg': 0.548, 'off_tov': 0.128, 'orb_pct': 0.262, 'off_ft_rate': 0.252,
            'def_efg': 0.545, 'def_tov': 0.125, 'drb_pct': 0.738, 'def_ft_rate': 0.255},
    'MEM': {'name': 'Memphis Grizzlies', 'net_rating': 4.3, 'last_10_net': 2.5,
            'off_efg': 0.545, 'off_tov': 0.135, 'orb_pct': 0.302, 'off_ft_rate': 0.275,
            'def_efg': 0.532, 'def_tov': 0.138, 'drb_pct': 0.725, 'def_ft_rate': 0.258},
    'MIA': {'name': 'Miami Heat', 'net_rating': 0.3, 'last_10_net': 3.8,
            'off_efg': 0.538, 'off_tov': 0.122, 'orb_pct': 0.265, 'off_ft_rate': 0.248,
            'def_efg': 0.535, 'def_tov': 0.132, 'drb_pct': 0.748, 'def_ft_rate': 0.242},
    'MIL': {'name': 'Milwaukee Bucks', 'net_rating': 1.7, 'last_10_net': -3.5,
            'off_efg': 0.555, 'off_tov': 0.128, 'orb_pct': 0.268, 'off_ft_rate': 0.262,
            'def_efg': 0.548, 'def_tov': 0.125, 'drb_pct': 0.735, 'def_ft_rate': 0.258},
    'MIN': {'name': 'Minnesota Timberwolves', 'net_rating': 2.6, 'last_10_net': 4.2,
            'off_efg': 0.542, 'off_tov': 0.125, 'orb_pct': 0.272, 'off_ft_rate': 0.245,
            'def_efg': 0.525, 'def_tov': 0.132, 'drb_pct': 0.758, 'def_ft_rate': 0.235},
    'NOP': {'name': 'New Orleans Pelicans', 'net_rating': -7.3, 'last_10_net': -8.5,
            'off_efg': 0.525, 'off_tov': 0.138, 'orb_pct': 0.275, 'off_ft_rate': 0.258,
            'def_efg': 0.558, 'def_tov': 0.118, 'drb_pct': 0.708, 'def_ft_rate': 0.268},
    'NYK': {'name': 'New York Knicks', 'net_rating': 5.3, 'last_10_net': 6.8,
            'off_efg': 0.555, 'off_tov': 0.118, 'orb_pct': 0.285, 'off_ft_rate': 0.255,
            'def_efg': 0.532, 'def_tov': 0.135, 'drb_pct': 0.752, 'def_ft_rate': 0.242},
    'OKC': {'name': 'Oklahoma City Thunder', 'net_rating': 10.7, 'last_10_net': 11.2,
            'off_efg': 0.565, 'off_tov': 0.115, 'orb_pct': 0.288, 'off_ft_rate': 0.262,
            'def_efg': 0.512, 'def_tov': 0.148, 'drb_pct': 0.772, 'def_ft_rate': 0.228},
    'ORL': {'name': 'Orlando Magic', 'net_rating': -4.3, 'last_10_net': -2.8,
            'off_efg': 0.528, 'off_tov': 0.125, 'orb_pct': 0.278, 'off_ft_rate': 0.248,
            'def_efg': 0.525, 'def_tov': 0.128, 'drb_pct': 0.755, 'def_ft_rate': 0.232},
    'PHI': {'name': 'Philadelphia 76ers', 'net_rating': -7.0, 'last_10_net': -5.5,
            'off_efg': 0.532, 'off_tov': 0.135, 'orb_pct': 0.258, 'off_ft_rate': 0.268,
            'def_efg': 0.555, 'def_tov': 0.122, 'drb_pct': 0.718, 'def_ft_rate': 0.272},
    'PHX': {'name': 'Phoenix Suns', 'net_rating': -3.0, 'last_10_net': -1.8,
            'off_efg': 0.548, 'off_tov': 0.128, 'orb_pct': 0.252, 'off_ft_rate': 0.242,
            'def_efg': 0.552, 'def_tov': 0.125, 'drb_pct': 0.728, 'def_ft_rate': 0.255},
    'POR': {'name': 'Portland Trail Blazers', 'net_rating': -5.7, 'last_10_net': -4.2,
            'off_efg': 0.535, 'off_tov': 0.132, 'orb_pct': 0.265, 'off_ft_rate': 0.248,
            'def_efg': 0.558, 'def_tov': 0.122, 'drb_pct': 0.715, 'def_ft_rate': 0.262},
    'SAC': {'name': 'Sacramento Kings', 'net_rating': -1.4, 'last_10_net': -0.8,
            'off_efg': 0.548, 'off_tov': 0.132, 'orb_pct': 0.258, 'off_ft_rate': 0.252,
            'def_efg': 0.552, 'def_tov': 0.125, 'drb_pct': 0.725, 'def_ft_rate': 0.258},
    'SAS': {'name': 'San Antonio Spurs', 'net_rating': -3.7, 'last_10_net': -2.5,
            'off_efg': 0.535, 'off_tov': 0.138, 'orb_pct': 0.272, 'off_ft_rate': 0.262,
            'def_efg': 0.548, 'def_tov': 0.128, 'drb_pct': 0.728, 'def_ft_rate': 0.255},
    'TOR': {'name': 'Toronto Raptors', 'net_rating': -6.7, 'last_10_net': -4.5,
            'off_efg': 0.532, 'off_tov': 0.135, 'orb_pct': 0.268, 'off_ft_rate': 0.255,
            'def_efg': 0.558, 'def_tov': 0.122, 'drb_pct': 0.712, 'def_ft_rate': 0.262},
    'UTA': {'name': 'Utah Jazz', 'net_rating': -10.3, 'last_10_net': -11.5,
            'off_efg': 0.522, 'off_tov': 0.142, 'orb_pct': 0.255, 'off_ft_rate': 0.238,
            'def_efg': 0.568, 'def_tov': 0.112, 'drb_pct': 0.698, 'def_ft_rate': 0.275},
    'WAS': {'name': 'Washington Wizards', 'net_rating': -12.3, 'last_10_net': -13.8,
            'off_efg': 0.515, 'off_tov': 0.145, 'orb_pct': 0.262, 'off_ft_rate': 0.248,
            'def_efg': 0.572, 'def_tov': 0.108, 'drb_pct': 0.695, 'def_ft_rate': 0.278},
}


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def run_predictions(games: List[dict], injuries: Dict[str, List] = None) -> List[GamePrediction]:
    """Run predictions for a list of games."""
    
    model = NBAModelV4()
    
    # Load base data
    model.load_team_data(TEAM_DATA_2026)
    
    # Add injuries if provided
    if injuries:
        for team_abbrev, inj_list in injuries.items():
            if team_abbrev in model.teams:
                model.teams[team_abbrev].injuries = inj_list
    
    predictions = []
    for game in games:
        try:
            pred = model.predict_game(
                away_abbrev=game['away'],
                home_abbrev=game['home'],
                spread=game['spread'],
                game_date=game.get('date', datetime.now())
            )
            predictions.append(pred)
        except Exception as e:
            print(f"Error predicting {game}: {e}")
    
    return predictions


def print_predictions(predictions: List[GamePrediction]):
    """Pretty print predictions."""
    print("\n" + "=" * 70)
    print("NBA MODEL V4 PREDICTIONS")
    print("=" * 70)
    
    # Sort by edge
    predictions.sort(key=lambda x: abs(x.edge), reverse=True)
    
    for pred in predictions:
        # Determine pick
        if pred.edge > 0:
            if pred.spread > 0:
                pick = f"{pred.home} +{pred.spread}"
            else:
                pick = f"{pred.home} {pred.spread}"
        else:
            if pred.spread > 0:
                pick = f"{pred.away} -{pred.spread}"
            else:
                pick = f"{pred.away} +{abs(pred.spread)}"
        
        edge = abs(pred.edge)
        emoji = "🔥" if pred.confidence == "HIGH" else "👀" if pred.confidence == "MED" else "⏸️"
        
        print(f"\n{emoji} {pred.away} @ {pred.home}")
        print(f"   Pick: {pick}")
        print(f"   Model: {pred.home} by {pred.predicted_margin:+.1f}")
        print(f"   Edge: {edge:.1f} pts ({pred.edge_pct:.0f}%)")
        print(f"   Confidence: {pred.confidence}")
        
        # Factor breakdown
        print(f"   Factors: NR={pred.factors_breakdown['net_rating']:.1f}, "
              f"FF={pred.factors_breakdown['four_factors']:.1f}, "
              f"REC={pred.factors_breakdown['recency']:.1f}, "
              f"REST={pred.factors_breakdown['rest']:.1f}, "
              f"INJ={pred.factors_breakdown['injuries']:.1f}")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY - TOP PICKS")
    print("=" * 70)
    
    for pred in predictions:
        if pred.confidence in ['HIGH', 'MED']:
            edge = abs(pred.edge)
            if pred.edge > 0:
                if pred.spread > 0:
                    pick = f"{pred.home} +{pred.spread}"
                else:
                    pick = f"{pred.home} {pred.spread}"
            else:
                if pred.spread > 0:
                    pick = f"{pred.away} -{pred.spread}"
                else:
                    pick = f"{pred.away} +{abs(pred.spread)}"
            
            emoji = "🔥" if pred.confidence == "HIGH" else "👀"
            print(f"{emoji} {pick} ({edge:.1f} pt edge, {pred.edge_pct:.0f}%)")


if __name__ == "__main__":
    # Example: Today's games (Feb 9, 2026)
    games = [
        {'away': 'DET', 'home': 'CHA', 'spread': 3},
        {'away': 'MIL', 'home': 'ORL', 'spread': -10.5},
        {'away': 'CHI', 'home': 'BKN', 'spread': 3.5},
        {'away': 'UTA', 'home': 'MIA', 'spread': -8},
        {'away': 'ATL', 'home': 'MIN', 'spread': -6.5},
        {'away': 'SAC', 'home': 'NOP', 'spread': -7.5},
        {'away': 'CLE', 'home': 'DEN', 'spread': 1},
        {'away': 'MEM', 'home': 'GSW', 'spread': -6.5},
        {'away': 'OKC', 'home': 'LAL', 'spread': 6},
        {'away': 'PHI', 'home': 'POR', 'spread': 4},
    ]
    
    # Key injuries for today
    injuries = {
        'MIL': [('Giannis Antetokounmpo', 32, 'OUT')],
        'CLE': [('Evan Mobley', 28, 'OUT')],
        'MEM': [('Ja Morant', 32, 'OUT')],
        'GSW': [('Stephen Curry', 32, 'OUT')],
    }
    
    predictions = run_predictions(games, injuries)
    print_predictions(predictions)
