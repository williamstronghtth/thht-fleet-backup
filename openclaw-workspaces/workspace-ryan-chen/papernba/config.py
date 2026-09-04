"""
Configuration for the papernba project.
Central place for seasons, paths, API settings, and feature flags.
"""

import os

# ── Project root ──────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# ── Seasons ───────────────────────────────────────────────────
CURRENT_SEASON = "2025-26"
CURRENT_SEASON_NBA_API = "2025-26"  # nba_api format

SUPPORTED_SEASONS = [
    "2019-20",
    "2020-21",
    "2021-22",
    "2022-23",
    "2023-24",
    "2024-25",
    "2025-26",
]

# ── Data paths ────────────────────────────────────────────────
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
MODELS_DIR = os.path.join(DATA_DIR, "models")


def raw_season_dir(season: str, category: str) -> str:
    """Return (and create) the raw data directory for a season + category."""
    path = os.path.join(RAW_DIR, season, category)
    os.makedirs(path, exist_ok=True)
    return path


def processed_season_dir(season: str, category: str) -> str:
    """Return (and create) the processed data directory for a season + category."""
    path = os.path.join(PROCESSED_DIR, season, category)
    os.makedirs(path, exist_ok=True)
    return path


# ── API settings ──────────────────────────────────────────────
API_DELAY = 0.6          # seconds between nba_api requests
API_TIMEOUT = 30         # seconds per request timeout
API_MAX_RETRIES = 3      # retry count on failure
API_RETRY_DELAY = 5.0    # seconds between retries

# ── Betting defaults ─────────────────────────────────────────
DEFAULT_BANKROLL = 1000.0   # paper dollars
DEFAULT_BET_UNIT = 0.02     # 2% of bankroll per unit

# ── Logging ──────────────────────────────────────────────────
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
