"""
Player Model Settings
======================

All tunable parameters for the simulation player model.
Edit this file to experiment. Use tune_settings.py to find optimal values.

Backup convention: settings_v1.py, settings_v2.py, etc.
"""

# ============================================================
# RECENT FORM WINDOW
# ============================================================
WINDOW = 25  # Number of recent games to use (tuned from 20, MAE 13.56→13.19)
DECAY = 0.97  # Exponential decay per game (tuned from 0.93, MAE 13.56→12.96)
MIN_GAMES = 3             # Minimum games to build a profile

# ============================================================
# BAYESIAN PRIOR STRENGTHS
# Higher = more shrinkage toward career/league average
# Lower = trust recent data more quickly
# ============================================================
PRIOR_FGA = 50  # Prior strength for FG% (~0.6 games of attempts)
PRIOR_FTA = 20            # Prior strength for FT% (~0.8 games of FTA)
PRIOR_POSS = 40  # Prior strength for possession rates (~0.4 games)

# ============================================================
# LOOKBACK FOR ROSTER BUILDING
# ============================================================
ROSTER_LOOKBACK_DAYS = 60  # How far back to look for team roster

# ============================================================
# DEFENSIVE PROFILE
# ============================================================
DEF_BLEND_GAMES = 8       # Games to fully trust recent defensive data
DEF_CAREER_TRUST = 40     # Games for full career defense trust

# ============================================================
# OFFENSIVE/DEFENSIVE WEIGHT SPLIT
# How much does the offensive player matter vs the defender?
# ============================================================
OFF_WEIGHT = 0.65         # Offensive player weight (e.g., shooter's FG%)
DEF_WEIGHT = 0.35         # Defensive player weight (e.g., defender's FG% allowed)

# ============================================================
# HOME COURT ADVANTAGE
# ============================================================
HCA_FG2_BONUS = 0.0037    # +/- to 2pt FG% (total gap ~0.74%)
HCA_FG3_BONUS = 0.0056    # +/- to 3pt FG% (total gap ~1.12%)
HCA_FOUL_BONUS = 0.005    # +/- to foul draw rate

# ============================================================
# ASSIST / REBOUND / STEAL / BLOCK RATES
# These are the league-wide rates used in the possession sim
# ============================================================
ASSIST_RATE_2PM = 0.55     # % of made 2-pointers that are assisted
ASSIST_RATE_3PM = 0.65     # % of made 3-pointers that are assisted
STEAL_ON_TOV = 0.60        # % of turnovers that are steals
BLOCK_RATE_2PA = 0.09      # % of 2-point attempts blocked
BLOCK_RATE_3PA = 0.04      # % of 3-point attempts blocked
