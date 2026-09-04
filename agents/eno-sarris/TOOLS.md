# TOOLS.md - Eno's Fantasy Baseball Toolkit

## Fantrax Access

### Browser Automation (Primary Method)
Fantrax requires an active browser session. Use browser automation:

```
profile: "openclaw"
```

Ryan Chen maintains the authenticated session. The browser is logged in as `choover323@gmail.com`.

### League Details
- **League:** Money Ball (ID: `fq6li5m5mhuxa22g`)
- **Team:** "We Got Worms the 19th" (ID: `5cqtzk7mmhuxa22k`)
- **Owner:** Chris Hoover
- **Draft:** March 16, 2026 @ 1:00 PM EDT
- **Claim Budget:** $125.00

### API Structure (for browser fetch calls)
```javascript
// Run inside browser context
await fetch('/fxpa/req?leagueId=fq6li5m5mhuxa22g', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    msgs: [{method: 'METHOD_NAME', data: {}}],
    uiv: 3,
    refUrl: location.href,
    dt: 1, at: 0, av: '0.0',
    tz: 'UTC',
    v: '179.0.1'
  })
});
```

### Known API Methods
- `getPlayerStats` - Player statistics
- `getFantasyTeams` - All teams in league
- `getFantasyColumns` - Column configurations
- `getPendingTransactions` - Pending claims/trades

### Config Files
- `fantrax/fantrax-config.json` - Full config with credentials
- `fantrax/README.md` - Current roster snapshot

## Team Communication

### Ryan Chen (Software Engineer)
- Session: `agent:ryan-chen:main`
- Use `sessions_send` to coordinate on technical issues
- He handles browser session maintenance

### Chris Hoover (Owner)
- Telegram: 8560812913
- Final decision maker on moves

## 🌴 Spring Training Stats Script ✅ NEW

Get Spring Training batting and pitching stats directly from Statcast:

```bash
# From your workspace
cd /root/.openclaw/workspace-eno-sarris/scripts

# Batting stats (last 14 days)
python3 spring-training-stats.py batting

# Pitching stats
python3 spring-training-stats.py pitching

# Both batting and pitching
python3 spring-training-stats.py both

# Specify days (e.g., last 21 days)
python3 spring-training-stats.py both 21
```

**Output includes:**
- Batting: PA, AB, H, 2B, 3B, HR, BB, K, AVG, OBP, SLG, Exit Velo, Launch Angle
- Pitching: BF, K, BB, H, HR, K%, BB%, Whiff%, CSW%, Velocity, Spin

**Note:** Minor leaguers without MLB IDs show as "ID:######" — focus on the known names.

---

## pybaseball (FanGraphs/Statcast Data) ✅ PRIMARY

Direct Python access to FanGraphs and Statcast — no browser needed!

```python
from pybaseball import batting_stats, pitching_stats, playerid_lookup

# Get qualified batters/pitchers for a season
batters = batting_stats(2024, qual=400)
pitchers = pitching_stats(2024, qual=100)

# Key columns for our format:
# Batting: Name, WAR, AVG, OBP, SLG, wOBA, K%, BB%
# Pitching: Name, WAR, ERA, FIP, K/9, BB/9, WHIP, IP

# Player lookup
player = playerid_lookup('ohtani', 'shohei')
```

**Use this for:** FanGraphs stats, Statcast data, historical analysis, draft prep.

## Scrapling (Anti-Bot Web Scraping)

For sites with Cloudflare/bot protection (FanGraphs, etc.), use Scrapling instead of default browser:

```python
# Activate the venv first
source /root/.openclaw/workspace-ryan-chen/scrapling_env/bin/activate

# Then in Python:
from scrapling import StealthyFetcher
fetcher = StealthyFetcher()
page = fetcher.fetch('https://example.com')
```

**Use cases:**
- FanGraphs (Cloudflare blocked)
- Baseball Savant (if blocked)
- Any site returning 403/Cloudflare challenge

**For Fantrax browser automation:** Still use `profile="openclaw"` with the browser tool.

## Research Sources (Browser Automation)

### CBS Sports Rankings ✅
- **Dynasty Rankings**: `https://www.cbssports.com/fantasy/baseball/rankings/dynasty/`
- **H2H Points Rankings**: `https://www.cbssports.com/fantasy/baseball/rankings/h2h/top300/`
- **Roto Rankings**: `https://www.cbssports.com/fantasy/baseball/rankings/roto/top300/`

### FantasyPros Rankings ✅
- **Dynasty Overall**: `https://www.fantasypros.com/mlb/rankings/dynasty-overall.php`

### Other Sources
- **FanGraphs**: `https://www.fangraphs.com/` (often Cloudflare blocked - use browser)
- **Baseball Savant**: `https://baseballsavant.mlb.com/`
- **Roster Resource**: `https://www.rosterresource.com/`
- **PitcherList**: `https://www.pitcherlist.com/`


---

## ⚠️ Email — Do NOT use MCP or Gmail Auth

Never ask Chris (or anyone) to connect MCP or authenticate Gmail.
Use the local email script instead:
```bash
python3 /root/agents/bin/send-email.py --to "recipient@example.com" --subject "Subject" --body "Body text"
```
