"""Daily streamer rankings (SP) + under-26 hitter hot-streak board.

Reads the JSON dumps written by daily_fetch.py plus today's MLB probables, then
scores every starter 0-100 and every young hot bat 0-100. Skills first: SIERA and
xwOBA carry the weight, surface results are only a tiebreak.
"""
import json
import re
import sys
import urllib.request

STATSAPI = "https://statsapi.mlb.com/api/v1/schedule"

# Static run park factors (100 = neutral). Used as a small nudge only.
PARK_FACTORS = {
    "COL": 112, "CIN": 106, "BOS": 106, "KCR": 104, "PHI": 103, "ARI": 102,
    "BAL": 102, "TEX": 102, "ATL": 101, "LAA": 101, "TOR": 101, "WSN": 101,
    "CHC": 100, "MIL": 100, "MIN": 100, "NYY": 100, "STL": 100, "HOU": 99,
    "LAD": 99, "NYM": 99, "CHW": 99, "SDP": 98, "TBR": 98, "ATH": 98,
    "PIT": 97, "MIA": 97, "CLE": 97, "DET": 96, "SFG": 95, "SEA": 93,
}

# StatsAPI abbreviations differ from FanGraphs for a handful of clubs.
ABBR_FIX = {"SD": "SDP", "TB": "TBR", "KC": "KCR", "SF": "SFG", "CWS": "CHW",
            "WSH": "WSN", "AZ": "ARI", "OAK": "ATH"}

TAG_RE = re.compile(r"<[^>]+>")


def strip_tags(value):
    return TAG_RE.sub("", str(value)).strip()


def clamp(value, low=0.0, high=100.0):
    return max(low, min(high, value))


def load_leaderboard(path, key="Name"):
    with open(path) as fh:
        rows = json.load(fh)["data"]
    return {strip_tags(r[key]): r for r in rows}


def fetch_probables(date_str):
    url = f"{STATSAPI}?sportId=1&date={date_str}&hydrate=probablePitcher,team"
    with urllib.request.urlopen(url, timeout=30) as resp:
        payload = json.load(resp)
    games = []
    for date_block in payload.get("dates", []):
        for game in date_block["games"]:
            away, home = game["teams"]["away"], game["teams"]["home"]
            a_abbr = norm(away["team"]["abbreviation"])
            h_abbr = norm(home["team"]["abbreviation"])
            for side, opp, venue, label in (
                (away, h_abbr, h_abbr, f"@ {h_abbr}"),
                (home, a_abbr, h_abbr, f"vs {a_abbr}"),
            ):
                pitcher = side.get("probablePitcher")
                if not pitcher:
                    continue
                games.append({
                    "name": pitcher["fullName"],
                    "team": a_abbr if side is away else h_abbr,
                    "opp": opp,
                    "venue": venue,
                    "matchup": label,
                })
    return games


def norm(abbr):
    return ABBR_FIX.get(abbr, abbr)


def score_pitcher(season, recent, opp_wrc, park):
    """0-100 start confidence. SIERA dominates; matchup and length adjust it."""
    siera = season["SIERA"]
    siera_pts = clamp(100 - (siera - 2.30) * 30)

    # Recent swinging-strike form as a leading indicator of the skill trend.
    swstr = (recent or season).get("SwStr%", season["SwStr%"]) * 100
    form_pts = clamp(50 + (swstr - 11.0) * 6)

    opp_pts = clamp(100 - (opp_wrc - 100) * 1.6)
    park_pts = clamp(100 - (park - 100) * 2.0)

    # Quality-start length matters a lot in this league (QS = +8).
    ip_per_gs = season["IP"] / max(season["GS"], 1)
    length_pts = clamp((ip_per_gs - 3.8) * 42)

    return round(
        siera_pts * 0.50 + opp_pts * 0.20 + form_pts * 0.13
        + length_pts * 0.12 + park_pts * 0.05
    )


def pitcher_tier(score):
    if score >= 76:
        return "🟢 Auto Start"
    if score >= 60:
        return "🔵 Probably Start"
    if score >= 44:
        return "🟡 Questionable"
    return "🔴 Do Not Start"


def build_pitcher_board(date_str):
    season = load_leaderboard("/tmp/fgp.txt")
    recent = load_leaderboard("/tmp/fgp_30d.txt")
    teams = {strip_tags(v["Team"]): v for v in
             json.load(open("/tmp/fg_team30.txt"))["data"]}

    rows = []
    for game in fetch_probables(date_str):
        stats = season.get(game["name"])
        if not stats or stats.get("SIERA") is None:
            rows.append({**game, "score": None})
            continue
        opp_team = teams.get(game["opp"])
        opp_wrc = opp_team["wRC+"] if opp_team else 100.0
        park = PARK_FACTORS.get(game["venue"], 100)
        rows.append({
            **game,
            "score": score_pitcher(stats, recent.get(game["name"]), opp_wrc, park),
            "siera": stats["SIERA"],
            "opp_wrc": opp_wrc,
        })
    return rows


def score_hitter(recent, season):
    """0-100 'is this streak real' score. Expected stats over surface results."""
    xwoba = recent["xwOBA"]
    skill_pts = clamp((xwoba - 0.270) * 555)

    barrel_pts = clamp((recent["Barrel%"] * 100 - 4.0) * 7.0)
    hardhit_pts = clamp((recent["HardHit%"] * 100 - 30.0) * 3.2)

    # K rate is worth -1 per whiff in this league, so contact carries real weight.
    k_pts = clamp((0.30 - recent["K%"]) * 500)

    # Reward guys whose 30-day skills beat their season baseline: a real change,
    # not just a random hot month.
    delta = (recent["xwOBA"] - season["xwOBA"]) if season else 0.0
    breakout_pts = clamp(50 + delta * 700)

    score = (skill_pts * 0.38 + barrel_pts * 0.16 + hardhit_pts * 0.14
             + k_pts * 0.14 + breakout_pts * 0.18)

    # Penalize mirages: big wOBA/xwOBA gaps mean the results outran the contact.
    luck_gap = recent["wOBA"] - recent["xwOBA"]
    if luck_gap > 0.040:
        score -= min((luck_gap - 0.040) * 300, 18)
    return round(clamp(score)), luck_gap


def hitter_tier(score):
    if score >= 72:
        return "🟢 Add Now"
    if score >= 58:
        return "🔵 Strong Watch"
    if score >= 45:
        return "🟡 Monitor"
    return "🔴 Mirage"


def build_hitter_board(max_age=26, min_pa=40):
    recent_rows = json.load(open("/tmp/fgb_30d.txt"))["data"]
    season = load_leaderboard("/tmp/fgb_season.txt")

    board = []
    for row in recent_rows:
        if row["Age"] > max_age or row["PA"] < min_pa:
            continue
        name = strip_tags(row["Name"])
        score, luck_gap = score_hitter(row, season.get(name))
        board.append({
            "name": name,
            "team": strip_tags(row["Team"]),
            "age": row["Age"],
            "pa": row["PA"],
            "score": score,
            "luck_gap": luck_gap,
            "xwoba": row["xwOBA"],
            "wrc": row["wRC+"],
            "hr": row["HR"],
            "sb": row["SB"],
            "k_rate": row["K%"] * 100,
            "barrel": row["Barrel%"] * 100,
        })
    return sorted(board, key=lambda r: -r["score"])


def render(date_str, pitchers, hitters, top_n=15):
    out = [f"⚾ DAILY BOARD — {date_str}", "", "═══ STARTING PITCHERS ═══", ""]
    ranked = sorted([p for p in pitchers if p["score"] is not None],
                    key=lambda p: -p["score"])
    current_tier = None
    for p in ranked:
        tier = pitcher_tier(p["score"])
        if tier != current_tier:
            out.append(tier)
            current_tier = tier
        out.append(f"  {p['score']} — {p['name']} ({p['team']}) {p['matchup']}"
                   f" | SIERA {p['siera']:.2f} | opp wRC+ {p['opp_wrc']:.0f}")
    for p in pitchers:
        if p["score"] is None:
            out.append(f"  ?? — {p['name']} ({p['team']}) {p['matchup']} | no qualifying data")

    out += ["", "═══ HOT BATS, AGE ≤26 (last 30d) ═══", ""]
    current_tier = None
    for h in hitters[:top_n]:
        tier = hitter_tier(h["score"])
        if tier != current_tier:
            out.append(tier)
            current_tier = tier
        flag = "  ⚠️ luck" if h["luck_gap"] > 0.040 else ""
        out.append(
            f"  {h['score']} — {h['name']} ({h['team']}, {h['age']}) "
            f"| xwOBA {h['xwoba']:.3f} | wRC+ {h['wrc']:.0f} | "
            f"{h['hr']}HR {h['sb']}SB | K {h['k_rate']:.0f}% | Brl {h['barrel']:.0f}%{flag}"
        )
    return "\n".join(out)


def main():
    date_str = sys.argv[1]
    print(render(date_str, build_pitcher_board(date_str), build_hitter_board()))


if __name__ == "__main__":
    main()
