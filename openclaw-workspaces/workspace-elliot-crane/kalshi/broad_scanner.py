#!/usr/bin/env python3
"""
Broad Market Scanner
Scans liquid non-sports Kalshi markets and filters for actual tradeability.
"""

import sys
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime, timezone

sys.path.insert(0, '/root/.openclaw/workspace-elliot-crane')

from kalshi.kalshi_client import KalshiClient


@dataclass
class MarketOpportunity:
    ticker: str
    title: str
    category: str
    yes_bid: float
    yes_ask: float
    no_bid: float
    no_ask: float
    volume: int
    open_interest: int
    mid_price: float
    spread: float
    can_buy_yes: bool
    can_buy_no: bool
    event_ticker: str


class BroadScanner:
    """Scan all liquid, tradeable non-sports markets on Kalshi."""

    SKIP_TICKERS = ['GAME', 'SPREAD', 'PARLAY']
    SKIP_CATEGORIES = {'Sports'}
    MIN_VOLUME = 1000
    MIN_OPEN_INTEREST = 100

    def __init__(self):
        self.client = KalshiClient()

    def get_all_markets(self) -> List[MarketOpportunity]:
        """Fetch all liquid markets with actual order-book availability."""
        markets = []
        cursor = None

        for _ in range(15):
            params = {'limit': 100}
            if cursor:
                params['cursor'] = cursor

            result = self.client._request('GET', '/events', params=params)
            events = result.get('events', [])

            for event in events:
                event_ticker = event.get('event_ticker', '')
                category = event.get('category', 'unknown')

                if category in self.SKIP_CATEGORIES:
                    continue
                if any(skip in event_ticker for skip in self.SKIP_TICKERS):
                    continue

                try:
                    e = self.client._request('GET', f'/events/{event_ticker}')
                    for m in e.get('markets', []):
                        volume = float(m.get('volume_fp', 0) or 0)
                        open_interest = float(m.get('open_interest_fp', 0) or 0)
                        yes_ask = float(m.get('yes_ask_dollars', 0) or 0)
                        yes_bid = float(m.get('yes_bid_dollars', 0) or 0)
                        yes_ask_size = float(m.get('yes_ask_size_fp', 0) or 0)
                        no_ask = float(m.get('no_ask_dollars', 0) or 0)
                        no_bid = float(m.get('no_bid_dollars', 0) or 0)
                        no_ask_size = float(m.get('no_ask_size_fp', 0) or 0)

                        if volume < self.MIN_VOLUME:
                            continue
                        if open_interest < self.MIN_OPEN_INTEREST:
                            continue

                        can_buy_yes = yes_ask > 0 and yes_ask_size > 0
                        can_buy_no = no_ask > 0 and no_ask_size > 0
                        if not (can_buy_yes or can_buy_no):
                            continue

                        prices = [p for p in [yes_bid, yes_ask] if p > 0]
                        if not prices:
                            continue
                        mid = sum(prices) / len(prices)

                        if mid < 0.05 or mid > 0.95:
                            continue

                        spread = (yes_ask - yes_bid) * 100 if yes_ask > 0 and yes_bid > 0 else 99

                        markets.append(MarketOpportunity(
                            ticker=m.get('ticker'),
                            title=m.get('yes_sub_title', m.get('title', ''))[:80],
                            category=category,
                            yes_bid=yes_bid,
                            yes_ask=yes_ask,
                            no_bid=no_bid,
                            no_ask=no_ask,
                            volume=int(volume),
                            open_interest=int(open_interest),
                            mid_price=mid,
                            spread=spread,
                            can_buy_yes=can_buy_yes,
                            can_buy_no=can_buy_no,
                            event_ticker=event_ticker,
                        ))
                except Exception:
                    continue

            cursor = result.get('cursor')
            if not cursor or not events:
                break

        return markets

    def get_interesting_markets(self, min_volume: int = 10000, max_spread: float = 6.0) -> List[MarketOpportunity]:
        """High-volume, non-extreme, actually tradeable markets."""
        all_markets = self.get_all_markets()
        interesting = [
            m for m in all_markets
            if m.volume >= min_volume
            and 0.10 <= m.mid_price <= 0.90
            and m.spread <= max_spread
            and (m.can_buy_yes or m.can_buy_no)
        ]
        interesting.sort(key=lambda x: (x.spread, -x.volume))
        return interesting

    def get_tight_spread_markets(self, max_spread: float = 3.0) -> List[MarketOpportunity]:
        all_markets = self.get_all_markets()
        tight = [
            m for m in all_markets
            if m.spread <= max_spread
            and 0.15 <= m.mid_price <= 0.85
            and (m.can_buy_yes or m.can_buy_no)
        ]
        tight.sort(key=lambda x: (x.spread, -x.volume))
        return tight

    def scan(self) -> List[MarketOpportunity]:
        return self.get_all_markets()

    def report(self, limit: int = 30) -> str:
        markets = self.get_interesting_markets(min_volume=5000)
        lines = [
            "=" * 70,
            f"  BROAD MARKET SCAN — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
            "=" * 70,
            "",
            f"Found {len(markets)} interesting markets (vol > 5K, tradeable, 10-90% range)",
            "",
        ]

        by_category = {}
        for m in markets:
            by_category.setdefault(m.category, []).append(m)

        for category, cat_markets in sorted(by_category.items(), key=lambda x: -len(x[1])):
            lines.append(f"📁 {category} ({len(cat_markets)} markets)")
            for m in cat_markets[:5]:
                sides = []
                if m.can_buy_yes:
                    sides.append('YES')
                if m.can_buy_no:
                    sides.append('NO')
                lines.append(f"   {m.ticker}")
                lines.append(f"      {m.title}")
                lines.append(
                    f"      Mid: {m.mid_price*100:.0f}% | Vol: {m.volume:,} | OI: {m.open_interest:,} | Spread: {m.spread:.0f}¢ | Buyable: {'/'.join(sides)}"
                )
            if len(cat_markets) > 5:
                lines.append(f"   ... and {len(cat_markets) - 5} more")
            lines.append("")

        return "\n".join(lines)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Broad market scanner')
    parser.add_argument('action', choices=['scan', 'report', 'interesting', 'tight'], help='Action to perform')
    parser.add_argument('--limit', type=int, default=30, help='Max results')
    parser.add_argument('--min-volume', type=int, default=5000, help='Min volume')

    args = parser.parse_args()
    scanner = BroadScanner()

    if args.action == 'scan':
        markets = scanner.scan()
        print(f"Found {len(markets)} liquid markets")
        for m in markets[:args.limit]:
            print(f"{m.ticker}: {m.title} | {m.mid_price*100:.0f}% | Vol: {m.volume:,}")
    elif args.action == 'report':
        print(scanner.report(limit=args.limit))
    elif args.action == 'interesting':
        markets = scanner.get_interesting_markets(min_volume=args.min_volume)
        for m in markets[:args.limit]:
            sides = []
            if m.can_buy_yes:
                sides.append('YES')
            if m.can_buy_no:
                sides.append('NO')
            print(f"{m.ticker}")
            print(f"  {m.title}")
            print(f"  {m.category} | Mid: {m.mid_price*100:.0f}% | Vol: {m.volume:,} | Spread: {m.spread:.0f}¢ | Buyable: {'/'.join(sides)}")
            print()
    elif args.action == 'tight':
        markets = scanner.get_tight_spread_markets()
        for m in markets[:args.limit]:
            print(f"{m.ticker}: Spread {m.spread:.0f}¢ | Mid: {m.mid_price*100:.0f}%")


if __name__ == '__main__':
    main()
