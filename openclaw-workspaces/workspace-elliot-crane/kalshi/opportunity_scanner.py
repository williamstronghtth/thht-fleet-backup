"""
Multi-Category Opportunity Scanner
Unified scanner for all Kalshi market categories.

Combines:
- Economics (CPI, GDP, Fed) with Cleveland Fed/Atlanta Fed nowcasts
- Weather with NWS/Open-Meteo forecasts
- Politics with sentiment analysis
- Any market with microstructure signals

Goal: Surface the best opportunities across ALL categories.
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class Category(Enum):
    ECONOMICS = "economics"
    WEATHER = "weather"
    POLITICS = "politics"
    CRYPTO = "crypto"
    ENTERTAINMENT = "entertainment"
    OTHER = "other"


@dataclass
class Opportunity:
    """A trading opportunity across any category."""
    ticker: str
    title: str
    category: Category
    market_price: float
    estimated_prob: float
    edge: float
    volume: float
    spread: float
    confidence: str  # HIGH, MEDIUM, LOW
    signal_source: str  # What generated this signal
    reasoning: str
    timestamp: str
    
    @property
    def direction(self) -> str:
        return "YES" if self.edge > 0 else "NO"
    
    @property
    def trade_size_suggestion(self) -> str:
        """Suggest position size based on edge and confidence."""
        abs_edge = abs(self.edge)
        
        if self.confidence == "HIGH" and abs_edge > 0.15:
            return "$50-75 (high conviction)"
        elif self.confidence == "HIGH" and abs_edge > 0.10:
            return "$25-50 (standard)"
        elif abs_edge > 0.10:
            return "$15-25 (moderate)"
        else:
            return "$10-15 (small/test)"


class OpportunityScanner:
    """
    Unified scanner for all market categories.
    """
    
    def __init__(self, kalshi_client=None):
        self._kalshi = kalshi_client
        self.data_dir = Path('/root/.openclaw/workspace-elliot-crane/kalshi/scanner_data')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.opportunities_file = self.data_dir / 'latest_opportunities.json'
    
    @property
    def kalshi(self):
        if self._kalshi is None:
            import sys
            sys.path.insert(0, '/root/.openclaw/workspace-elliot-crane')
            from kalshi.kalshi_client import KalshiClient
            self._kalshi = KalshiClient()
        return self._kalshi
    
    def scan_economics(self) -> List[Opportunity]:
        """Scan economics markets (CPI, GDP, Fed)."""
        opportunities = []
        
        # Import our existing scanner
        try:
            import sys
            sys.path.insert(0, '/root/.openclaw/workspace-elliot-crane')
            from kalshi.hourly_scanner import HourlyScanner
            scanner = HourlyScanner(self.kalshi)
            
            # Get CPI opportunities
            cpi_opps = scanner.scan_cpi_markets()
            
            for opp in cpi_opps:
                opportunities.append(Opportunity(
                    ticker=opp.get('ticker', ''),
                    title=opp.get('title', ''),
                    category=Category.ECONOMICS,
                    market_price=opp.get('market_price', 0.5),
                    estimated_prob=opp.get('estimated_prob', 0.5),
                    edge=opp.get('edge', 0),
                    volume=opp.get('volume', 0),
                    spread=opp.get('spread', 0.1),
                    confidence=opp.get('confidence', 'MEDIUM'),
                    signal_source='Cleveland Fed Nowcast + Bias Model',
                    reasoning=opp.get('reasoning', ''),
                    timestamp=datetime.now(timezone.utc).isoformat(),
                ))
        except Exception as e:
            print(f"Economics scan error: {e}")
        
        return opportunities
    
    def scan_weather(self) -> List[Opportunity]:
        """Scan weather markets."""
        opportunities = []
        
        try:
            import sys
            sys.path.insert(0, '/root/.openclaw/workspace-elliot-crane')
            from kalshi.weather_scanner import WeatherScanner
            scanner = WeatherScanner(self.kalshi)
            
            weather_opps = scanner.scan()
            
            for opp in weather_opps:
                opportunities.append(Opportunity(
                    ticker=opp.ticker,
                    title=opp.title,
                    category=Category.WEATHER,
                    market_price=opp.market_price,
                    estimated_prob=opp.forecast_prob,
                    edge=opp.edge,
                    volume=opp.volume,
                    spread=opp.spread,
                    confidence=opp.confidence,
                    signal_source=f'{opp.forecast_source} Forecast',
                    reasoning=opp.forecast_detail,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                ))
        except Exception as e:
            print(f"Weather scan error: {e}")
        
        return opportunities
    
    def scan_politics(self) -> List[Opportunity]:
        """
        Scan politics markets.
        Uses sentiment analysis where available.
        """
        opportunities = []
        
        # Key political series to monitor
        political_series = [
            'KXAMEND25',      # 25th Amendment
            'KXTARIFFSNEW',   # New tariffs
            'AILEGISLATION',  # AI regulation
            'KXRECNC',        # Reconciliation bill
        ]
        
        try:
            for series in political_series:
                events = self.kalshi._request('GET', '/events', params={'series_ticker': series, 'limit': 5})
                
                for event in events.get('events', []):
                    event_data = self.kalshi._request('GET', f'/events/{event.get("event_ticker")}')
                    
                    for market in event_data.get('markets', []):
                        if market.get('status') != 'active':
                            continue
                        
                        yes_bid = float(market.get('yes_bid_dollars', 0) or 0)
                        yes_ask = float(market.get('yes_ask_dollars', 0) or 0)
                        volume = float(market.get('volume_fp', 0) or 0)
                        
                        if not yes_bid or not yes_ask:
                            continue
                        
                        market_price = (yes_bid + yes_ask) / 2
                        spread = yes_ask - yes_bid
                        
                        # For politics, we flag opportunities based on:
                        # 1. Volume spikes (someone knows something)
                        # 2. Extreme prices (potential overreaction)
                        # 3. Spread tightening (increased interest)
                        
                        # Flag extreme prices for review
                        if market_price < 0.10 or market_price > 0.90:
                            edge_direction = 0.05 if market_price > 0.90 else -0.05  # Fade extremes
                            estimated = market_price - edge_direction
                            
                            opportunities.append(Opportunity(
                                ticker=market.get('ticker', ''),
                                title=market.get('title', ''),
                                category=Category.POLITICS,
                                market_price=market_price,
                                estimated_prob=estimated,
                                edge=edge_direction,
                                volume=volume,
                                spread=spread,
                                confidence='LOW',  # Politics is hard to predict
                                signal_source='Extreme Price Detection',
                                reasoning=f'Price at extreme ({market_price*100:.0f}%) - potential fade opportunity',
                                timestamp=datetime.now(timezone.utc).isoformat(),
                            ))
        except Exception as e:
            print(f"Politics scan error: {e}")
        
        return opportunities
    
    def scan_microstructure(self, tickers: List[str] = None) -> List[Opportunity]:
        """
        Scan markets using microstructure signals.
        """
        opportunities = []
        
        try:
            import sys
            sys.path.insert(0, '/root/.openclaw/workspace-elliot-crane')
            from kalshi.microstructure.analyzer import MarketAnalyzer
            analyzer = MarketAnalyzer()
            
            # If no tickers specified, use our watchlist
            if not tickers:
                tickers = ['KXCPI-26MAR-T0.7', 'KXGDP-26APR30-T1.5']
            
            for ticker in tickers:
                try:
                    result = analyzer.analyze_market(ticker)
                    
                    # If microstructure signals danger, flag it
                    if result.risk_score > 60:
                        opportunities.append(Opportunity(
                            ticker=ticker,
                            title=f"Microstructure Warning: {ticker}",
                            category=Category.OTHER,
                            market_price=0.5,  # Placeholder
                            estimated_prob=0.5,
                            edge=0,
                            volume=0,
                            spread=0,
                            confidence='HIGH',
                            signal_source='Microstructure Analysis',
                            reasoning=f'Risk score {result.risk_score}/100 - {result.recommendation}',
                            timestamp=datetime.now(timezone.utc).isoformat(),
                        ))
                except Exception:
                    pass
        except ImportError:
            pass
        
        return opportunities
    
    def scan_all(self, min_edge: float = 0.05) -> List[Opportunity]:
        """
        Scan all categories and return unified opportunity list.
        """
        all_opportunities = []
        
        print("🔍 Scanning Economics...")
        all_opportunities.extend(self.scan_economics())
        
        print("🌤️ Scanning Weather...")
        all_opportunities.extend(self.scan_weather())
        
        print("🏛️ Scanning Politics...")
        all_opportunities.extend(self.scan_politics())
        
        # Filter by minimum edge
        filtered = [o for o in all_opportunities if abs(o.edge) >= min_edge]
        
        # Sort by edge magnitude
        filtered.sort(key=lambda x: abs(x.edge), reverse=True)
        
        # Save results
        self._save_opportunities(filtered)
        
        return filtered
    
    def _save_opportunities(self, opportunities: List[Opportunity]):
        """Save opportunities to file."""
        data = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'count': len(opportunities),
            'opportunities': [
                {**asdict(o), 'category': o.category.value}
                for o in opportunities
            ]
        }
        
        with open(self.opportunities_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def report(self, min_edge: float = 0.05) -> str:
        """Generate comprehensive opportunity report."""
        opportunities = self.scan_all(min_edge=min_edge)
        
        lines = [
            "═" * 75,
            "  MULTI-CATEGORY OPPORTUNITY SCANNER",
            f"  {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC",
            "═" * 75,
            "",
        ]
        
        if not opportunities:
            lines.append(f"  No opportunities found with edge ≥ {min_edge*100:.0f}%")
        else:
            # Group by category
            by_category = {}
            for opp in opportunities:
                cat = opp.category.value
                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append(opp)
            
            lines.append(f"  Found {len(opportunities)} opportunities across {len(by_category)} categories:")
            lines.append("")
            
            for category, opps in by_category.items():
                lines.append(f"  ┌─ {category.upper()} ({len(opps)} opportunities)")
                lines.append("  │")
                
                for opp in opps[:5]:  # Top 5 per category
                    direction = "▲" if opp.edge > 0 else "▼"
                    lines.append(
                        f"  │  {direction} {opp.ticker:<25} "
                        f"Edge: {opp.edge*100:>+5.0f}% | "
                        f"Mkt: {opp.market_price*100:>3.0f}% | "
                        f"Vol: ${opp.volume:>8,.0f}"
                    )
                    lines.append(f"  │    └─ {opp.title[:55]}")
                    lines.append(f"  │    └─ {opp.signal_source} | Conf: {opp.confidence}")
                    lines.append(f"  │    └─ Size: {opp.trade_size_suggestion}")
                    lines.append("  │")
                
                lines.append("  └" + "─" * 70)
                lines.append("")
        
        lines.extend([
            "═" * 75,
            "  Scan complete. Review opportunities above.",
            "═" * 75,
        ])
        
        return "\n".join(lines)
    
    def quick_scan(self) -> str:
        """Quick one-liner summary of best opportunities."""
        opportunities = self.scan_all(min_edge=0.10)
        
        if not opportunities:
            return "No opportunities with edge ≥10%"
        
        best = opportunities[0]
        return (
            f"Best: {best.ticker} ({best.category.value}) | "
            f"Edge: {best.edge*100:+.0f}% | "
            f"Signal: {best.signal_source}"
        )


def main():
    """CLI for opportunity scanner."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Multi-category opportunity scanner')
    parser.add_argument('action', choices=['scan', 'report', 'quick', 'economics', 'weather', 'politics'],
                        help='Action to perform')
    parser.add_argument('--min-edge', type=float, default=0.05,
                        help='Minimum edge threshold (default: 5%%)')
    
    args = parser.parse_args()
    
    scanner = OpportunityScanner()
    
    if args.action == 'scan':
        opps = scanner.scan_all(min_edge=args.min_edge)
        print(f"Found {len(opps)} opportunities")
        for opp in opps[:10]:
            print(f"  {opp.ticker}: {opp.edge*100:+.0f}% ({opp.category.value})")
    
    elif args.action == 'report':
        print(scanner.report(min_edge=args.min_edge))
    
    elif args.action == 'quick':
        print(scanner.quick_scan())
    
    elif args.action == 'economics':
        opps = scanner.scan_economics()
        print(f"Economics: {len(opps)} opportunities")
        for opp in opps:
            print(f"  {opp.ticker}: {opp.edge*100:+.0f}%")
    
    elif args.action == 'weather':
        opps = scanner.scan_weather()
        print(f"Weather: {len(opps)} opportunities")
        for opp in opps:
            print(f"  {opp.ticker}: {opp.edge*100:+.0f}%")
    
    elif args.action == 'politics':
        opps = scanner.scan_politics()
        print(f"Politics: {len(opps)} opportunities")
        for opp in opps:
            print(f"  {opp.ticker}: {opp.edge*100:+.0f}%")


if __name__ == '__main__':
    main()
