#!/usr/bin/env python3
"""Baseball Savant skills layer — the FanGraphs SIERA/SwStr% substitute.

WHY THIS EXISTS
---------------
FanGraphs sits behind a Cloudflare browser-integrity challenge (see the header of
statsapi_leaders.py for the full test matrix). SIERA and SwStr% are FanGraphs
*modeled* stats, so losing that source loses the skills layer, not just rows.

Savant (official MLB, public, no key, no challenge) publishes every INPUT to
SIERA, so we recompute it locally instead of scraping someone's paywall.

  StatsAPI  -> playing time, counting stats, true date ranges
  Savant    -> skills: K%, BB%, batted-ball mix, whiff%, xERA
  this file -> SIERA recomputed from the published formula

HONEST ACCURACY NOTE — READ BEFORE PUTTING THIS ON A BOARD
----------------------------------------------------------
`computeSiera()` implements the published Swartz/Seidman formula, but the number
it returns is NOT identical to FanGraphs' SIERA and must not be labelled as such:

  1. FanGraphs classifies batted balls with BIS/SIS data; we use Statcast. GB/FB/PU
     splits genuinely differ between the two providers.
  2. FanGraphs applies park and league-environment adjustments we do not have.

Expect agreement within roughly a few tenths of a run, not to the decimal. Label
it "SIERA (est.)" on anything Chris sees. A number that is quietly 0.3 wrong while
wearing a trusted name is worse than no number at all.

`whiff_percent` is likewise NOT SwStr%:
  whiff% = swings-and-misses / SWINGS
  SwStr% = swings-and-misses / PITCHES
Whiff% runs roughly 2x SwStr%. They are not interchangeable; do not port a
SwStr%-tuned threshold onto whiff% without re-tuning it.
"""

import csv
import io
import urllib.error
import urllib.request

SAVANT_LEADERBOARD_URL = "https://baseballsavant.mlb.com/leaderboard/custom"
REQUEST_TIMEOUT_SECONDS = 45
USER_AGENT = "Mozilla/5.0 (compatible; THHT-eno/1.0)"
DEFAULT_MIN_BATTERS_FACED = 50

PITCHER_SELECTIONS = (
    "pa,k_percent,bb_percent,whiff_percent,groundballs_percent,"
    "flyballs_percent,popups_percent,xera"
)

# Swartz/Seidman published SIERA coefficients.
SIERA_INTERCEPT = 6.145
SIERA_SO_COEF = -16.986
SIERA_BB_COEF = 11.434
SIERA_NETGB_COEF = -1.858
SIERA_SO_SQ_COEF = 7.653
SIERA_NETGB_SQ_MAGNITUDE = 6.664
SIERA_SO_NETGB_COEF = 10.130
SIERA_BB_NETGB_COEF = -5.195


def fetchCsv(url):
    """GET a CSV URL and return a list of dict rows.

    Raises RuntimeError with a readable message rather than leaking urllib types.
    """
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            text = response.read().decode("utf-8-sig")
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"Savant HTTP {exc.code} for {url}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(f"Savant unreachable for {url}: {exc}") from exc
    return list(csv.DictReader(io.StringIO(text)))


def parseFloatOrNone(value):
    """Savant leaves cells empty for unqualified players — empty must stay None.

    Coercing a missing rate to 0.0 would make a pitcher look elite at everything,
    which is the exact silent-wrongness we are trying to avoid.
    """
    if value is None:
        return None
    stripped = str(value).strip()
    if not stripped:
        return None
    try:
        return float(stripped)
    except ValueError:
        return None


def buildSavantUrl(season, minBattersFaced):
    return (
        f"{SAVANT_LEADERBOARD_URL}?year={season}&type=pitcher&filter="
        f"&min={minBattersFaced}&selections={PITCHER_SELECTIONS}"
        f"&chart=false&x=k_percent&y=k_percent&r=no&chartType=beeswarm"
        f"&sort=k_percent&sortDir=desc&csv=true"
    )


def computeSiera(strikeoutPct, walkPct, groundballPct, flyballPct, popupPct):
    """Recompute SIERA from rate components. Returns None if any input is missing.

    All arguments are percentages (22.5 means 22.5%), matching Savant's CSV.
    Returning None on partial input is deliberate: a SIERA built from three of
    five components is not a worse SIERA, it is a different statistic.
    """
    components = (strikeoutPct, walkPct, groundballPct, flyballPct, popupPct)
    if any(component is None for component in components):
        return None

    soRate = strikeoutPct / 100.0
    bbRate = walkPct / 100.0
    netGroundballRate = (groundballPct - flyballPct - popupPct) / 100.0

    # The squared net-GB term flips sign with the term itself in the published
    # formula — it is not a plain quadratic.
    netGbSquaredCoef = (
        -SIERA_NETGB_SQ_MAGNITUDE if netGroundballRate > 0 else SIERA_NETGB_SQ_MAGNITUDE
    )

    return (
        SIERA_INTERCEPT
        + SIERA_SO_COEF * soRate
        + SIERA_BB_COEF * bbRate
        + SIERA_NETGB_COEF * netGroundballRate
        + SIERA_SO_SQ_COEF * (soRate ** 2)
        + netGbSquaredCoef * (netGroundballRate ** 2)
        + SIERA_SO_NETGB_COEF * soRate * netGroundballRate
        + SIERA_BB_NETGB_COEF * bbRate * netGroundballRate
    )


def normalizeSavantRow(row):
    """Flatten one Savant CSV row and attach the estimated SIERA."""
    strikeoutPct = parseFloatOrNone(row.get("k_percent"))
    walkPct = parseFloatOrNone(row.get("bb_percent"))
    groundballPct = parseFloatOrNone(row.get("groundballs_percent"))
    flyballPct = parseFloatOrNone(row.get("flyballs_percent"))
    popupPct = parseFloatOrNone(row.get("popups_percent"))
    lastFirst = (row.get("last_name, first_name") or "").strip()
    return {
        "playerId": int(row["player_id"]) if row.get("player_id") else None,
        "name": lastFirst,
        "battersFaced": parseFloatOrNone(row.get("pa")),
        "strikeoutPct": strikeoutPct,
        "walkPct": walkPct,
        "whiffPct": parseFloatOrNone(row.get("whiff_percent")),
        "groundballPct": groundballPct,
        "flyballPct": flyballPct,
        "popupPct": popupPct,
        "xera": parseFloatOrNone(row.get("xera")),
        "sieraEstimated": computeSiera(
            strikeoutPct, walkPct, groundballPct, flyballPct, popupPct
        ),
    }


def fetchPitcherSkills(season, minBattersFaced=DEFAULT_MIN_BATTERS_FACED):
    """Season-long pitcher skills keyed by MLBAM playerId.

    playerId is the same id space StatsAPI uses, so this joins directly onto
    fetchPitcherLeaders() output with no name matching. Never match on name —
    accents and suffixes silently drop rows.
    """
    rows = [normalizeSavantRow(row) for row in fetchCsv(buildSavantUrl(season, minBattersFaced))]
    keyed = {row["playerId"]: row for row in rows if row["playerId"] is not None}
    sieraResolved = sum(1 for row in keyed.values() if row["sieraEstimated"] is not None)
    return {
        "season": season,
        "rows": keyed,
        "scanned": len(rows),
        "sieraResolved": sieraResolved,
        "sieraMissing": len(keyed) - sieraResolved,
    }


def main():
    """Smoke-run and print a coverage line so an empty pull cannot look like a clean one."""
    skills = fetchPitcherSkills(season=2026)
    print(
        f"SAVANT PITCHER SKILLS {skills['season']}: {len(skills['rows'])} pitchers "
        f"({skills['sieraResolved']} with SIERA est., {skills['sieraMissing']} missing components)"
    )
    ranked = sorted(
        (row for row in skills["rows"].values() if row["sieraEstimated"] is not None),
        key=lambda row: row["sieraEstimated"],
    )
    print(f"{'PITCHER':<26}{'K%':>7}{'BB%':>7}{'Whiff%':>8}{'xERA':>7}{'SIERA*':>8}")
    for row in ranked[:8]:
        whiff = f"{row['whiffPct']:.1f}" if row["whiffPct"] is not None else "  -"
        xera = f"{row['xera']:.2f}" if row["xera"] is not None else "  -"
        print(
            f"{row['name']:<26}{row['strikeoutPct']:>7.1f}{row['walkPct']:>7.1f}"
            f"{whiff:>8}{xera:>7}{row['sieraEstimated']:>8.2f}"
        )
    print("\n* SIERA is ESTIMATED from Statcast components — not FanGraphs' published value.")


if __name__ == "__main__":
    main()
