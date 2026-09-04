"""
ingestion/coaches.py — Pull coach info and map to teams/seasons.

Uses nba_api.stats.endpoints.CommonTeamRoster to get coach info per team,
then aggregates across all teams for a season.
"""

import json
import logging
import os
import time

import pandas as pd
from nba_api.stats.endpoints import CommonTeamRoster
from nba_api.stats.static import teams as nba_teams

import config

logger = logging.getLogger(__name__)


def fetch_coaches(season: str = config.CURRENT_SEASON,
                  force: bool = False) -> list[dict]:
    """
    Fetch coach data for all teams in a season.

    Iterates through all 30 teams and pulls their coaching staff
    from CommonTeamRoster.

    Returns
    -------
    list[dict]
        List of coach records with team info.
    """
    out_dir = config.raw_season_dir(season, "coaches")
    cache_path = os.path.join(out_dir, "all_coaches.json")

    if os.path.exists(cache_path) and not force:
        logger.info("Cache hit: %s", cache_path)
        with open(cache_path, "r") as f:
            return json.load(f)

    teams = nba_teams.get_teams()
    all_coaches = []

    logger.info("Fetching coaches for %d teams in %s ...", len(teams), season)
    for i, team in enumerate(teams):
        team_id = team["id"]
        try:
            result = CommonTeamRoster(
                team_id=team_id,
                season=season,
                timeout=config.API_TIMEOUT,
            )
            data = result.get_normalized_dict()
            time.sleep(config.API_DELAY)

            # CommonTeamRoster returns "Coaches" result set
            coaches = data.get("Coaches", [])
            for coach in coaches:
                coach["TEAM_ID"] = team_id
                coach["TEAM_NAME"] = team["full_name"]
                coach["TEAM_ABBREVIATION"] = team["abbreviation"]
            all_coaches.extend(coaches)

            # Also save individual team roster
            team_path = os.path.join(out_dir, f"team_{team_id}.json")
            with open(team_path, "w") as f:
                json.dump(data, f)

            if (i + 1) % 10 == 0:
                logger.info("Progress: %d/%d teams", i + 1, len(teams))

        except Exception as e:
            logger.error("Failed to fetch coaches for %s: %s",
                         team["abbreviation"], e)

    with open(cache_path, "w") as f:
        json.dump(all_coaches, f)
    logger.info("Saved %d coach records → %s", len(all_coaches), cache_path)

    return all_coaches


def process_coaches(season: str = config.CURRENT_SEASON) -> pd.DataFrame:
    """Process raw coach data into a clean DataFrame and save as parquet."""
    raw_dir = config.raw_season_dir(season, "coaches")
    cache_path = os.path.join(raw_dir, "all_coaches.json")

    if not os.path.exists(cache_path):
        fetch_coaches(season)

    with open(cache_path, "r") as f:
        coaches = json.load(f)

    if not coaches:
        logger.warning("No coach data for %s", season)
        return pd.DataFrame()

    df = pd.DataFrame(coaches)
    df.columns = [c.strip().lower() for c in df.columns]

    # Filter to head coaches only (coach_type == "Head Coach")
    if "coach_type" in df.columns:
        head_coaches = df[df["coach_type"] == "Head Coach"].copy()
    else:
        head_coaches = df

    out_dir = config.processed_season_dir(season, "coaches")
    # Save all coaches
    df.to_parquet(os.path.join(out_dir, "all_coaches.parquet"), index=False)
    # Save head coaches separately
    head_coaches.to_parquet(os.path.join(out_dir, "head_coaches.parquet"), index=False)

    logger.info("Saved processed coaches (%d total, %d head) → %s",
                len(df), len(head_coaches), out_dir)
    return head_coaches
