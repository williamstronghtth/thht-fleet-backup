"""Fetch FanGraphs leaderboards through Cloudflare via Scrapling.

FanGraphs blocks plain requests/pybaseball with a 403 Cloudflare challenge, so every
pull has to go through a stealth browser fetch. Run this before daily_report.py.
"""
import sys
from scrapling.fetchers import StealthyFetcher

API = "https://www.fangraphs.com/api/leaders/major-league/data"


def fetch_json(url, out_path):
    page = StealthyFetcher.fetch(url, headless=True, network_idle=True)
    body = page.body
    if isinstance(body, bytes):
        body = body.decode("utf-8", "ignore")
    with open(out_path, "w") as fh:
        fh.write(body)
    print(f"{out_path} <- {page.status} ({len(body)} bytes)")


def build_pulls(start_date, end_date):
    common = "pos=all&lg=all&pageitems=2000&pagenum=1&ind=0&type=8&season=2026&season1=2026"
    window = f"month=1000&startdate={start_date}&enddate={end_date}"
    return [
        (f"{API}?{common}&stats=pit&qual=0&month=0&team=0", "/tmp/fgp.txt"),
        (f"{API}?{common}&stats=pit&qual=10&{window}&team=0", "/tmp/fgp_30d.txt"),
        (f"{API}?{common}&stats=bat&qual=100&month=0&team=0", "/tmp/fgb_season.txt"),
        (f"{API}?{common}&stats=bat&qual=40&{window}&team=0", "/tmp/fgb_30d.txt"),
        (f"{API}?{common}&stats=bat&qual=0&{window}&team=0,ts", "/tmp/fg_team30.txt"),
    ]


def main():
    start_date, end_date = sys.argv[1], sys.argv[2]
    for url, out_path in build_pulls(start_date, end_date):
        try:
            fetch_json(url, out_path)
        except Exception as err:
            print(f"FAILED {out_path}: {err}", file=sys.stderr)


if __name__ == "__main__":
    main()
