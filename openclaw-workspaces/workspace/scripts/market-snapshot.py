#!/usr/bin/env python3
"""
THHT Market Snapshot Tool
Fetches Redfin public housing market data and generates a quick snapshot
for Florida markets relevant to The Hoover Home Team.

Usage: python3 market-snapshot.py [--output markdown|json] [--save]
"""

import csv
import io
import json
import sys
import argparse
from datetime import datetime, timedelta
from urllib.request import urlopen, Request
from urllib.error import URLError

# Redfin public data URL (weekly, metro-level)
REDFIN_DATA_URL = "https://redfin-public-data.s3.us-west-2.amazonaws.com/redfin_market_tracker/city_market_tracker.tsv000.gz"

# Alternative: use their direct TSV endpoint for recent data
# This is the weekly regional data
REDFIN_REGIONAL_URL = "https://redfin-public-data.s3.us-west-2.amazonaws.com/redfin_market_tracker/redfin_metro_market_tracker.tsv000.gz"

# Florida metros we care about
TARGET_REGIONS = [
    "Cape Coral",
    "Fort Myers", 
    "Naples",
    "Miami",
    "Tampa",
    "Orlando",
    "Jacksonville",
    "Sarasota",
]

def fetch_redfin_data():
    """Fetch recent Redfin market data from their public S3 bucket."""
    import gzip
    
    print("📡 Fetching Redfin market data...")
    headers = {"User-Agent": "Mozilla/5.0 (compatible; THHT-MarketTool/1.0)"}
    req = Request(REDFIN_REGIONAL_URL, headers=headers)
    
    try:
        with urlopen(req, timeout=30) as resp:
            raw = resp.read()
            data = gzip.decompress(raw).decode("utf-8")
            print(f"✅ Downloaded {len(data)//1024}KB of market data")
            return data
    except URLError as e:
        print(f"❌ Failed to fetch data: {e}")
        return None

def parse_market_data(tsv_data):
    """Parse TSV data and filter for Florida markets."""
    reader = csv.DictReader(io.StringIO(tsv_data), delimiter="\t", quotechar='"')
    
    florida_data = {}
    
    for row in reader:
        # Columns are uppercase and quoted
        region = row.get("REGION", "")
        state = row.get("STATE_CODE", "")
        prop_type = row.get("PROPERTY_TYPE", "")
        
        # Only FL, only "All Residential" for aggregate stats
        if state != "FL":
            continue
        if prop_type != "All Residential":
            continue
        
        # Check if this is a Florida market we care about
        matched = None
        for target in TARGET_REGIONS:
            if target.lower() in region.lower():
                matched = target
                break
        
        if not matched:
            continue
        
        period = row.get("PERIOD_END", "")
        
        # Keep only most recent data per region
        if matched not in florida_data or period > florida_data[matched].get("_period", ""):
            florida_data[matched] = {
                "_period": period,
                "region_full": region,
                "median_sale_price": safe_num(row.get("MEDIAN_SALE_PRICE", "")),
                "median_sale_price_yoy": safe_pct(row.get("MEDIAN_SALE_PRICE_YOY", "")),
                "homes_sold": safe_num(row.get("HOMES_SOLD", "")),
                "homes_sold_yoy": safe_pct(row.get("HOMES_SOLD_YOY", "")),
                "new_listings": safe_num(row.get("NEW_LISTINGS", "")),
                "new_listings_yoy": safe_pct(row.get("NEW_LISTINGS_YOY", "")),
                "inventory": safe_num(row.get("INVENTORY", "")),
                "inventory_yoy": safe_pct(row.get("INVENTORY_YOY", "")),
                "median_dom": safe_num(row.get("MEDIAN_DOM", "")),
                "median_dom_yoy": safe_pct(row.get("MEDIAN_DOM_YOY", "")),
                "avg_sale_to_list": safe_pct(row.get("AVG_SALE_TO_LIST", "")),
                "period_end": period,
            }
    
    return florida_data

def safe_num(val):
    """Convert to number safely."""
    try:
        if val is None or val == "":
            return None
        return round(float(val))
    except (ValueError, TypeError):
        return None

def safe_pct(val):
    """Convert to percentage safely."""
    try:
        if val is None or val == "":
            return None
        f = float(val)
        if abs(f) < 1:  # Already decimal
            return round(f * 100, 1)
        return round(f, 1)
    except (ValueError, TypeError):
        return None

def format_change(val):
    """Format a YoY change with arrow."""
    if val is None:
        return "N/A"
    arrow = "📈" if val > 0 else "📉" if val < 0 else "➡️"
    sign = "+" if val > 0 else ""
    return f"{arrow} {sign}{val}%"

def generate_markdown(data):
    """Generate a markdown market snapshot."""
    now = datetime.utcnow().strftime("%B %d, %Y")
    
    lines = [
        f"# 🏠 THHT Florida Market Snapshot",
        f"**Generated:** {now}",
        f"**Source:** Redfin Public Data",
        "",
    ]
    
    if not data:
        lines.append("⚠️ No data available for target markets.")
        return "\n".join(lines)
    
    for region in sorted(data.keys()):
        d = data[region]
        lines.append(f"## {region}")
        lines.append(f"*Data through: {d['period_end']}*")
        lines.append("")
        
        if d["median_sale_price"]:
            lines.append(f"- **Median Sale Price:** ${d['median_sale_price']:,} {format_change(d['median_sale_price_yoy'])}")
        if d["homes_sold"]:
            lines.append(f"- **Homes Sold:** {d['homes_sold']:,} {format_change(d['homes_sold_yoy'])}")
        if d["new_listings"]:
            lines.append(f"- **New Listings:** {d['new_listings']:,} {format_change(d['new_listings_yoy'])}")
        if d["inventory"]:
            lines.append(f"- **Active Inventory:** {d['inventory']:,} {format_change(d['inventory_yoy'])}")
        if d["median_dom"]:
            lines.append(f"- **Median Days on Market:** {d['median_dom']} {format_change(d['median_dom_yoy'])}")
        if d["avg_sale_to_list"]:
            lines.append(f"- **Sale-to-List Ratio:** {d['avg_sale_to_list']}%")
        
        lines.append("")
    
    # Add quick analysis
    lines.append("## 📊 Quick Analysis")
    
    # Find hottest/coldest markets
    priced = {k: v for k, v in data.items() if v["median_sale_price_yoy"] is not None}
    if priced:
        hottest = max(priced, key=lambda k: priced[k]["median_sale_price_yoy"])
        coldest = min(priced, key=lambda k: priced[k]["median_sale_price_yoy"])
        lines.append(f"- **Fastest appreciating:** {hottest} ({format_change(priced[hottest]['median_sale_price_yoy'])} YoY)")
        lines.append(f"- **Slowest/declining:** {coldest} ({format_change(priced[coldest]['median_sale_price_yoy'])} YoY)")
    
    inv = {k: v for k, v in data.items() if v["inventory_yoy"] is not None}
    if inv:
        most_inv = max(inv, key=lambda k: inv[k]["inventory_yoy"])
        lines.append(f"- **Most inventory growth:** {most_inv} ({format_change(inv[most_inv]['inventory_yoy'])} YoY)")
    
    lines.append("")
    return "\n".join(lines)

def generate_json(data):
    """Generate JSON output."""
    return json.dumps(data, indent=2, default=str)

def main():
    parser = argparse.ArgumentParser(description="THHT Market Snapshot Tool")
    parser.add_argument("--output", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--save", action="store_true", help="Save to reports directory")
    args = parser.parse_args()
    
    tsv_data = fetch_redfin_data()
    if not tsv_data:
        print("Failed to fetch data. Exiting.")
        sys.exit(1)
    
    data = parse_market_data(tsv_data)
    print(f"📍 Found data for {len(data)} Florida markets: {', '.join(sorted(data.keys()))}")
    
    if args.output == "json":
        output = generate_json(data)
    else:
        output = generate_markdown(data)
    
    if args.save:
        import os
        reports_dir = os.path.join(os.path.dirname(__file__), "..", "reports")
        os.makedirs(reports_dir, exist_ok=True)
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        filename = f"market-snapshot-{date_str}.md" if args.output == "markdown" else f"market-snapshot-{date_str}.json"
        filepath = os.path.join(reports_dir, filename)
        with open(filepath, "w") as f:
            f.write(output)
        print(f"💾 Saved to {filepath}")
    else:
        print("\n" + output)

if __name__ == "__main__":
    main()
