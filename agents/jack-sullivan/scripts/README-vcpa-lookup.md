# VCPA Property Lookup Tool

Cross-reference names against the Volusia County Property Appraiser database.

## Quick Start

```bash
# Install dependencies (one-time)
cd /root/.openclaw/workspace-jack-sullivan/scripts
npm install playwright

# Run the lookup
node vcpa-lookup.js input.csv output.csv
```

## Input Format

CSV with two columns:
```csv
Last Name,First Name
DEGREGORIO,MELIKE
DEGREGORIO,JOSEPH
RANDOLPH,SUSAN
```

## Output Format

```csv
Original Name,Matched Owner Name,Property Address,City,Parcel ID,Property Class
DEGREGORIO, MELIKE,DEGREGORIO MELIKE,123 MAIN ST,DAYTONA BEACH,123456789012,Single Family
RANDOLPH, SUSAN,NO MATCH FOUND,,,,
```

## Features

- ✅ 2-second delay between requests (rate limiting)
- ✅ Handles multiple properties per owner
- ✅ Saves progress every 10 names
- ✅ Property class descriptions included
- ✅ Error handling with retry info

## Tips

1. **Batch your searches** — Run overnight for large lists (700 names ≈ 25 minutes)
2. **Check progress file** — `output_progress.csv` saves every 10 names
3. **Name format matters** — Tool searches "LASTNAME FIRSTNAME" format

## Alternative: Manual Browser Use

If the script isn't working, you can use browser automation directly:

```
# In your OpenClaw session:
browser action=open profile=openclaw targetUrl="https://vcpa.vcgov.org/search/real-property-classic"
browser action=snapshot profile=openclaw
# Then type in the owner name field and click Search
```

## Questions?

Ask Ryan Chen (sessions_send to agent:ryan-chen:main)
