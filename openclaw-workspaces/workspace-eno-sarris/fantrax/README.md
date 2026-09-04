# Fantrax Integration for Chris's Fantasy Baseball

## Account
- **Email:** choover323@gmail.com
- **League:** Money Ball (ID: fq6li5m5mhuxa22g)
- **Team:** "We Got Worms the 19th" (ID: 5cqtzk7mmhuxa22k)
- **Draft:** March 16, 2026 @ 1:00 PM EDT

## API Access
Fantrax API requires an active browser session. External curl/fetch calls get rejected.

### Using Browser Automation
```javascript
// Inside browser context (profile="openclaw"):
const response = await fetch('/fxpa/req?leagueId=fq6li5m5mhuxa22g', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    msgs: [{method: 'getFantasyTeams', data: {}}],
    uiv: 3,
    refUrl: location.href,
    dt: 1, at: 0, av: '0.0',
    tz: 'UTC',
    v: '179.0.1'
  })
});
const data = await response.json();
```

### Known API Methods
- `getPlayerStats` - Get player statistics
- `getFantasyTeams` - Get all teams in league
- `getFantasyColumns` - Get column configurations
- `getPendingTransactions` - Get pending claims/trades

## Current Roster (as of Feb 23, 2026)

### Hitting
| Pos | Player | Team | FPts | Notes |
|-----|--------|------|------|-------|
| C | Adley Rutschman | BAL | 323 | |
| 1B | Bryce Harper | PHI | 410 | |
| 2B | Ozzie Albies | ATL | 374 | |
| 3B | Alex Bregman | CHC | 420 | |
| SS | EMPTY | - | - | **NEED TO FILL** |
| OF | Jarren Duran | BOS | 417 | |
| OF | Michael Harris II | ATL | 371 | |
| OF | Kyle Schwarber | PHI | 475 | |
| UT | Rafael Devers | SF | 424 | |

### Reserves (Hitting)
- Alec Burleson (1B/OF - STL)
- Sal Frelick (OF - MIL)
- Jung Hoo Lee (OF - SF)
- Jakob Marsee (OF - MIA)
- Chandler Simpson (OF - TB)
- Ivan Herrera (C - STL)

### Pitching
| Pos | Player | Team | FPts | Notes |
|-----|--------|------|------|-------|
| SP | Jack Leiter | TEX | 275 | |
| SP | Casey Mize | DET | 269 | |
| SP | David Peterson | NYM | 283 | |
| SP | Hurston Waldrep | ATL | 182 | |
| SP | Gavin Williams | CLE | 304 | |
| RP | Ryne Nelson | ARI | 225 | SP/RP eligible |
| RP | EMPTY | - | - | **NEED TO FILL** |

### Reserves (Pitching)
- Noah Cameron (SP - KC)
- Michael McGreevy (SP - STL)
- Parker Messick (SP - CLE)
- Luis Morales (SP - ATH)
- Will Warren (SP - NYY)

### Injured Reserve
- Landen Roupp (SP - SF)
- Emmanuel Clase (RP - N/A) - **No stats projected**
- Randy Rodriguez (RP - SF)

## Immediate Needs
1. **SS position is EMPTY** - Need to acquire shortstop
2. **RP slot empty** - One of the reserve SPs could move here
3. Emmanuel Clase showing 0 projected stats - check status

## Draft Picks
- 2026: Rounds 2-5 (picks 16, 26, 36, 46)
- 2027-2029: Full 5 picks each year

## Claim Budget
$125.00 remaining
