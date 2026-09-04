#!/usr/bin/env python3
"""
Atlanta Fed GDPNow Scraper for Elliot Crane
============================================
Fetches the latest GDPNow GDP growth estimate.

Usage:
    python3 gdpnow-scraper.py          # Print latest estimate
    python3 gdpnow-scraper.py --json   # Output as JSON
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import sys
from datetime import datetime

GDPNOW_URL = "https://www.atlantafed.org/cqer/research/gdpnow/archives"

def fetch_gdpnow():
    """Fetch the latest GDPNow estimate from Atlanta Fed."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        resp = requests.get(GDPNOW_URL, headers=headers, timeout=15)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        text = soup.get_text()
        
        # Find the latest estimate - pattern: "X.X percent on Month DD"
        # Example: "2.7 percent on March 13"
        pattern = r'(\-?\d+\.?\d*)\s+percent\s+on\s+(\w+\s+\d+,?\s*\d*)'
        matches = re.findall(pattern, text)
        
        if matches:
            estimate = float(matches[0][0])
            date_str = matches[0][1].strip().rstrip(',')
            
            # Find quarter info
            quarter_pattern = r'(first|second|third|fourth)\s+quarter\s+of\s+(\d{4})'
            quarter_match = re.search(quarter_pattern, text, re.IGNORECASE)
            
            quarter = None
            year = None
            if quarter_match:
                quarter_map = {'first': 'Q1', 'second': 'Q2', 'third': 'Q3', 'fourth': 'Q4'}
                quarter = quarter_map.get(quarter_match.group(1).lower(), quarter_match.group(1))
                year = quarter_match.group(2)
            
            # Find next update date
            next_update_pattern = r'next GDPNow update is\s+(\w+,?\s+\w+\s+\d+)'
            next_match = re.search(next_update_pattern, text)
            next_update = next_match.group(1) if next_match else None
            
            return {
                'estimate': estimate,
                'as_of': date_str,
                'quarter': quarter,
                'year': year,
                'next_update': next_update,
                'fetched_at': datetime.utcnow().isoformat() + 'Z',
                'source': 'Atlanta Fed GDPNow'
            }
        else:
            return {'error': 'Could not parse GDPNow estimate from page'}
            
    except Exception as e:
        return {'error': str(e)}

def main():
    data = fetch_gdpnow()
    
    if '--json' in sys.argv:
        print(json.dumps(data, indent=2))
    else:
        if 'error' in data:
            print(f"❌ Error: {data['error']}")
        else:
            print("📊 ATLANTA FED GDPNOW")
            print("=" * 40)
            print(f"🎯 Estimate: {data['estimate']}%")
            print(f"📅 As of: {data['as_of']}")
            if data['quarter'] and data['year']:
                print(f"📈 Quarter: {data['quarter']} {data['year']}")
            if data['next_update']:
                print(f"⏰ Next update: {data['next_update']}")
            print("=" * 40)

if __name__ == '__main__':
    main()
