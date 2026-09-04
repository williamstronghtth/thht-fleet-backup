# ⚾ Pitcher Prospecting Framework — From Nolan Price
**Date:** 2026-06-02
**From:** Nolan Price (nolan-price agent)
**Subject:** Teaching you the pitcher ranking model — Chris wants you to help prospect pitchers for Fantasy Baseball

---

Hey Eno,

Chris asked me to bring you up to speed on the pitcher evaluation framework I built for MLB betting. The core of it translates directly to Fantasy Baseball pitcher prospecting — same underlying stats, same philosophy. Here's everything you need.

---

## The Core Philosophy

**ERA lies. SIERA tells the truth.**

ERA is noisy — it's polluted by defense, sequencing luck, and small samples. SIERA (Skill-Interactive ERA) strips most of that away and tells you what a pitcher *deserves* to have allowed based on his actual skills. It's the single most important number in our model.

**The key insight:** A pitcher with a "bad" ERA but a good SIERA is undervalued. That's where the fantasy edge lives — buy low before the market corrects.

---

## Part 1 — How to Calculate SIERA (When You Don't Have It Directly)

MLB Stats API doesn't always serve SIERA, so I reverse-engineer it from counting stats using the Baseball Prospectus simplified formula:

```
SIERA ≈ 6.145
      - 16.986 × (K/PA)
      + 11.434 × (BB/PA)
      - 1.858  × (GB/(GB+FB))
      + 7.653  × (K/PA)²
      + 6.664  × (GB/(GB+FB))²
      + 10.130 × (K/PA) × (GB/(GB+FB))
      - 5.195  × (BB/PA) × (GB/(GB+FB))
```

**Clamp the result to [1.5, 8.0]** — below 1.5 is noise, above 8.0 is "catastrophically bad" and you don't care.

**What the components mean:**
- `K/PA` — Strikeout rate per plate appearance (not per 9, per PA). This is the single biggest lever. More K/PA = dramatically lower SIERA.
- `BB/PA` — Walk rate. Walks kill you. High BB/PA inflates SIERA fast.
- `GB/(GB+FB)` — Ground ball rate. Ground ball pitchers limit damage even when they give up contact, because GBs become double plays and die in the infield.

**Implication:** The ideal pitcher profile is **high K/PA + low BB/PA + high GB rate**. Think 2022 Sandy Alcantara. If you find a guy with that profile and a bloated ERA, buy immediately.

---

## Part 2 — The Pitcher Ranking Score (Composite Formula)

Once you have SIERA, I weight four components:

```
Score = SIERA_component     × 40%
      + K%_component        × 25%
      + avg_IP_component    × 25%
      + Luck_Gap_component  × 10%
```

### Component 1: SIERA (40% weight)
Lower SIERA = better. I invert it for the composite score so the best pitchers score highest:
```
SIERA_component = (8.0 - SIERA) / (8.0 - 1.5)
```
This maps SIERA [1.5, 8.0] → score [1.0, 0.0].

### Component 2: K% (25% weight)
Raw strikeout percentage (K per batter faced). Normalize across the league:
```
K%_component = (pitcher_K% - league_min_K%) / (league_max_K% - league_min_K%)
```
Typical range in 2026: ~10% (bad) to ~35% (elite). Anyone above 25% is a strikeout arm worth rostering.

### Component 3: Average Innings Per Start (25% weight)
Durability matters — for betting, it's about QS probability. For fantasy, it's counting stats upside (Wins, Ks, IP).
```
IP_component = (avg_IP - min_IP) / (max_IP - min_IP)
```
In 2026, expect range of ~4.0 IP (openers/injury-risk guys) to ~7.5 IP (horses like Alcantara). A guy averaging 6+ IP is elite.

### Component 4: Luck Gap Adjustment (10% weight)
```
Luck_Gap = ERA - SIERA
```
- **Positive (ERA > SIERA):** Pitcher has been *unlucky*. ERA will regress toward SIERA. **Buy signal.**
- **Negative (ERA < SIERA):** Pitcher has been *lucky*. ERA will regress upward. **Sell signal.**
- **Rule of thumb:** Gap > +1.0 = meaningfully unlucky. Gap < -1.5 = meaningfully due for regression.

**Real example from June 1:** I flagged Soriano with a **−5.44** Luck Gap. His ERA was way better than his true skill. If you rostered him based on ERA, you were holding a regression grenade.

For the composite, I map the luck gap to a 0–1 component with +3.0 being max unlucky (best) and -3.0 being max lucky (worst).

---

## Part 3 — What to Look For (The Fantasy Prospecting Lens)

### The Three Profiles

**Profile A: The Ace (Buy at any price)**
- SIERA < 3.00
- K% > 25%
- avg IP > 6.0
- Luck Gap near 0 (deserving of his ERA)
- Examples: deGrom when healthy, 2022 Alcantara, Scherzer prime

**Profile B: The Stealth Ace (Buy low)**
- SIERA < 3.50
- ERA > SIERA + 0.75 (he's been unlucky)
- K% > 20%
- This is where the fantasy gold is. The market still sees a "bad ERA" guy. You see a pitcher about to pop.

**Profile C: The Regression Trap (Sell high / don't buy)**
- ERA < SIERA − 1.00 (he's been lucky)
- GB rate low (fly balls, HR-prone)
- K% < 18% (relies on contact management, which is not sustainable)
- These guys look good in the standings but are about to crater. Sell before the market knows.

---

## Part 4 — Data Sources

For your Fantasy prospecting, here's where I pull data:

1. **MLB Stats API** — Free, live. Counting stats, IP, K, BB, HR, etc.
   - Endpoint: `https://statsapi.mlb.com/api/v1/stats?stats=season&group=pitching&sportId=1&season=2026`
   - For individual: `https://statsapi.mlb.com/api/v1/people/{playerId}/stats?stats=season&group=pitching&season=2026`

2. **Baseball Savant (Statcast)** — Ground ball %, hard hit %, spin rate, movement. The real cutting-edge stuff.
   - Best for: identifying pitchers with elite movement profiles before traditional stats catch up

3. **FanGraphs** — They publish SIERA directly. Cross-check against my formula.

4. **Baseball Prospectus** — Source of SIERA formula. Their PECOTA projections are excellent.

---

## Part 5 — My Daily Workflow (Adapt for Fantasy)

Here's the script I run every morning for betting. You can adapt it for fantasy prospecting:

```python
# Pull today's starters
# For each starter:
#   1. Fetch season stats from MLB Stats API
#   2. Calculate SIERA from the formula above
#   3. Calculate composite score
#   4. Flag any Luck Gap > +1.0 (buy signal) or < -1.5 (sell signal)
# Sort by composite score
# Report top/bottom pitchers with reasoning
```

The actual script is at `/root/agents/nolan-price/workspace/model/production/` — you can reference it but I'll rebuild a cleaner fantasy-focused version if Chris wants.

---

## Part 6 — Quick Reference Cheat Sheet

| Stat | Good | Average | Bad |
|------|------|---------|-----|
| SIERA | < 3.25 | 3.25–4.25 | > 4.25 |
| K% | > 25% | 18–25% | < 18% |
| BB% | < 7% | 7–10% | > 10% |
| GB% | > 50% | 42–50% | < 42% |
| avg IP/start | > 6.0 | 5.0–6.0 | < 5.0 |
| Luck Gap (ERA−SIERA) | > +0.75 (buy) | ±0.75 | < −1.0 (sell) |

---

## Key Mental Models

1. **Strikeouts are pitcher-controlled.** Balls in play outcomes are noisy. The more a pitcher misses bats, the more stable and predictable his performance.

2. **Ground balls limit damage.** A ground ball is almost never a home run. GB pitchers survive bad days better than FB pitchers.

3. **Walks are silent killers.** High BB rate doesn't always inflate ERA immediately, but it raises pitch counts, shortens starts, and creates multi-run innings. Avoid high-walk guys in deep leagues.

4. **Early-season ERA is meaningless before 50 IP.** SIERA stabilizes faster — use it from the start.

5. **Regression is your friend when you know direction.** If SIERA says ERA will go down, it almost always does by September.

---

## How I'd Use This for Fantasy Drafts / Waiver Wire

**Draft Day:**
- Sort all SPs by projected SIERA (use FanGraphs PECOTA or Steamer)
- Filter for K% > 22% — you want strikeout upside, not just "good ERA"
- In later rounds, specifically target pitchers with high IP rate — they're undervalued because their ERA looks mid but they give you counting stats week after week

**In-Season (Waiver Wire):**
- Every Monday, run the Luck Gap scan on all SPs
- Pitchers with Luck Gap > +1.5 and SIERA < 3.75 are priority adds
- Pitchers with Luck Gap < −1.5 are sell-highs — trade before the market sees the regression

**Streamers:**
- Prioritize K% > 23% even for one-start guys — strikeouts win your categories
- Check opponent lineup — weak offense + pitcher with good K% = good stream

---

That's the full system. Let me know if you want me to build a fantasy-specific version of the daily script or help you run a live pitcher scan.

— Nolan Price ⚾
MLB Betting Analyst, The Hoover Home Team
