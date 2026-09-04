#!/usr/bin/env python3
"""
Quick microstructure scan for Kalshi markets.
Usage: python3 scan.py TICKER [--exec SIZE]
"""

import sys
import argparse
from analyzer import MarketAnalyzer


def main():
    parser = argparse.ArgumentParser(description='Analyze Kalshi market microstructure')
    parser.add_argument('ticker', help='Market ticker (e.g., KXCPI-26MAR-T0.7)')
    parser.add_argument('--trades', type=int, default=200, help='Number of trades to analyze')
    parser.add_argument('--exec', type=float, help='Generate execution schedule for this position size')
    parser.add_argument('--hours', type=float, default=2.0, help='Execution time horizon (hours)')
    
    args = parser.parse_args()
    
    analyzer = MarketAnalyzer()
    
    # Run analysis
    print(f"\n🔍 Analyzing {args.ticker}...\n")
    analysis = analyzer.analyze_market(args.ticker, args.trades)
    print(analysis)
    
    # Execution schedule if requested
    if args.exec:
        print(f"\n\n📊 Execution schedule for ${args.exec:.0f} position:\n")
        schedule = analyzer.get_execution_schedule(args.ticker, args.exec, args.hours)
        print(schedule)
    
    # Return exit code based on safety
    return 0 if analysis.safe_to_trade else 1


if __name__ == '__main__':
    sys.exit(main())
