#!/usr/bin/env python3
"""MLB StatsAPI leaderboard fetcher — FanGraphs replacement.

WHY THIS EXISTS
---------------
FanGraphs (www.fangraphs.com/api/leaders/...) sits behind a Cloudflare
*interactive* challenge as of 2026-08-30. Verified NOT bypassable from this box:
  - curl with a real Chrome UA + Referer      -> 403 "Just a moment..."
  - headless chromium via Playwright          -> 403, challenge never clears (45s)
  - Playwright + webdriver-flag stealth patch -> 403
  - scrapling StealthyFetcher (Eno, 08-29)    -> 403 block pages
This is a JS/browser-integrity challenge, not the User-Agent/WAF case we beat on
WordPress. Do not spend more time on UA tricks; they cannot work here.

MLB StatsAPI is the official, free, un-gated substitute. It serves true
date-ranged splits, which is exactly what the streamer board needs.

Docs: https://statsapi.mlb.com/api/v1/  (no key, no auth, no rate limit published)
"""

import json
import urllib.error
import urllib.request
from datetime import date, timedelta

API_BASE = "https://statsapi.mlb.com/api/v1"
SPORT_ID_MLB = 1
REQUEST_TIMEOUT_SECONDS = 25
USER_AGENT = "Mozilla/5.0 (compatible; THHT-eno/1.0)"
MAX_PEOPLE_PER_LOOKUP = 100


def fetchJson(url):
    """GET a StatsAPI URL and return parsed JSON.

    Raises RuntimeError with a readable message — callers should not have to
    unpack urllib exception types to know what broke.
    """
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"StatsAPI HTTP {exc.code} for {url}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(f"StatsAPI unreachable for {url}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"StatsAPI returned non-JSON for {url}: {exc}") from exc


def getDateRange(daysBack, endDate=None):
    """Return (startIso, endIso) for a trailing window ending on endDate."""
    end = endDate or date.today()
    start = end - timedelta(days=daysBack)
    return start.isoformat(), end.isoformat()


def buildLeaderUrl(group, startIso, endIso, limit):
    return (
        f"{API_BASE}/stats?stats=byDateRange&group={group}"
        f"&startDate={startIso}&endDate={endIso}"
        f"&sportId={SPORT_ID_MLB}&limit={limit}"
    )


def buildSeasonUrl(group, season, limit):
    return (
        f"{API_BASE}/stats?stats=season&group={group}"
        f"&season={season}&sportId={SPORT_ID_MLB}&limit={limit}"
    )


def extractSplits(payload):
    """Pull the splits list out of a StatsAPI stats payload, tolerating shape drift."""
    statsBlocks = payload.get("stats") or []
    if not statsBlocks:
        return []
    return statsBlocks[0].get("splits") or []


def fetchPlayerAges(playerIds):
    """Return {playerId: currentAge}. Batches to keep URLs sane.

    Age is NOT included in stats splits, so the under-26 board needs this
    second call. Missing players simply get no entry — callers must treat
    unknown age as unknown, never as young.
    """
    ages = {}
    uniqueIds = list(dict.fromkeys(playerIds))
    for offset in range(0, len(uniqueIds), MAX_PEOPLE_PER_LOOKUP):
        batch = uniqueIds[offset:offset + MAX_PEOPLE_PER_LOOKUP]
        idParam = ",".join(str(pid) for pid in batch)
        payload = fetchJson(f"{API_BASE}/people?personIds={idParam}")
        for person in payload.get("people", []):
            age = person.get("currentAge")
            if age is not None:
                ages[person["id"]] = age
    return ages


def normalizeSplit(split):
    """Flatten a StatsAPI split into a flat dict the report layer can use."""
    player = split.get("player") or {}
    team = split.get("team") or {}
    stat = split.get("stat") or {}
    return {
        "playerId": player.get("id"),
        "name": player.get("fullName"),
        "team": team.get("abbreviation") or team.get("name"),
        **stat,
    }


def fetchPitcherLeaders(daysBack=30, limit=200, endDate=None):
    """Trailing-window pitching leaders — the streamer-tier input.

    StatsAPI has no `qual` param, so filter on innings downstream rather than
    trusting the API to have done it.
    """
    startIso, endIso = getDateRange(daysBack, endDate)
    payload = fetchJson(buildLeaderUrl("pitching", startIso, endIso, limit))
    rows = [normalizeSplit(split) for split in extractSplits(payload)]
    return {"start": startIso, "end": endIso, "rows": rows}


def fetchPitcherSeasonStats(season=None, limit=800):
    """Full-season pitching stats keyed by playerId, for the season baseline.

    The streamer score needs a season-long anchor next to the 30-day window;
    without it every pitcher scores identically off form alone (this is why the
    Sept 1 board defaulted every SP to 65/100).

    Keyed by playerId so it joins to the trailing-window rows and to Savant
    skills with no name matching — accents and suffixes silently drop rows.
    """
    seasonYear = season or date.today().year
    payload = fetchJson(buildSeasonUrl("pitching", seasonYear, limit))
    rows = [normalizeSplit(split) for split in extractSplits(payload)]
    return {
        "season": seasonYear,
        "rows": {row["playerId"]: row for row in rows if row.get("playerId")},
        "scanned": len(rows),
    }


def fetchHitterLeaders(daysBack=30, limit=300, endDate=None):
    """Trailing-window hitting leaders, unfiltered — the daily board's batting feed.

    This is the general equivalent of FanGraphs' `batting_stats` 30-day pull.
    Use fetchYoungHitterLeaders() when you specifically need the age-gated
    prospect board; this one deliberately does no age lookup so it does not
    drop players whose age fails to resolve.
    """
    startIso, endIso = getDateRange(daysBack, endDate)
    payload = fetchJson(buildLeaderUrl("hitting", startIso, endIso, limit))
    rows = [normalizeSplit(split) for split in extractSplits(payload)]
    return {"start": startIso, "end": endIso, "rows": rows}


def fetchYoungHitterLeaders(daysBack=7, maxAge=25, limit=200, endDate=None):
    """Trailing-window hitters filtered to under-`maxAge`+1 (default: 25 and under).

    Players whose age we could not resolve are EXCLUDED, not assumed young —
    a hot-board that silently includes a 34-year-old is worse than a short one.
    """
    startIso, endIso = getDateRange(daysBack, endDate)
    payload = fetchJson(buildLeaderUrl("hitting", startIso, endIso, limit))
    rows = [normalizeSplit(split) for split in extractSplits(payload)]
    ages = fetchPlayerAges([row["playerId"] for row in rows if row.get("playerId")])
    young = [
        {**row, "age": ages[row["playerId"]]}
        for row in rows
        if row.get("playerId") in ages and ages[row["playerId"]] <= maxAge
    ]
    unresolved = sum(1 for row in rows if row.get("playerId") not in ages)
    return {
        "start": startIso,
        "end": endIso,
        "rows": young,
        "scanned": len(rows),
        "ageUnresolved": unresolved,
    }


def main():
    """Smoke-run both boards and print a coverage line.

    The coverage line matters: a silent empty board and a broken fetch must
    not look identical (issue-008 antidote).
    """
    pitchers = fetchPitcherLeaders(daysBack=30)
    print(f"PITCHERS {pitchers['start']}..{pitchers['end']}: {len(pitchers['rows'])} rows")
    for row in pitchers["rows"][:5]:
        print(f"  {row['name']:<24} {row.get('team','?'):<4} ERA {row.get('era')} K {row.get('strikeOuts')}")

    season = fetchPitcherSeasonStats()
    joined = sum(1 for row in pitchers["rows"] if row.get("playerId") in season["rows"])
    print(
        f"SEASON PITCHING {season['season']}: {len(season['rows'])} pitchers "
        f"({joined}/{len(pitchers['rows'])} of the 30-day rows have a season baseline)"
    )

    allHitters = fetchHitterLeaders(daysBack=30)
    print(f"HITTERS 30d {allHitters['start']}..{allHitters['end']}: {len(allHitters['rows'])} rows")

    hitters = fetchYoungHitterLeaders(daysBack=7, maxAge=25)
    print(
        f"U26 HITTERS {hitters['start']}..{hitters['end']}: "
        f"{len(hitters['rows'])} of {hitters['scanned']} scanned "
        f"({hitters['ageUnresolved']} age-unresolved, excluded)"
    )
    for row in hitters["rows"][:5]:
        print(f"  {row['name']:<24} age {row['age']} OPS {row.get('ops')} HR {row.get('homeRuns')}")


if __name__ == "__main__":
    main()
