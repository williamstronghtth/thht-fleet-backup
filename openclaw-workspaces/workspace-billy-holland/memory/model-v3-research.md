# Model V3 Research - Book Learnings

## Book 1: The Logic of Sports Betting – Ed Miller & Matthew Davidow (2019)

### Core Philosophy
Miller (poker pro) + Davidow (betting syndicate quant) wrote the definitive modern sports betting primer. Key thesis: **Betting is a market, not a game.**

### Key Concepts

#### 1. Closing Line Value (CLV) — The Holy Grail
- **The single best predictor of long-term success**
- If you consistently beat the closing line, you're a winning bettor (even if short-term results vary)
- Track your CLV religiously, not just W/L
- The market gets MORE efficient as game time approaches
- Early bets have more edge potential but more variance

#### 2. The Hold & Market Structure
- Understand the vig: -110/-110 = 4.5% hold
- Break-even at -110 requires 52.4% wins
- **Line shopping is non-negotiable** — 1 point = ~3-4% EV difference
- Multiple books = mandatory for serious bettors
- The hold is your enemy; minimize it by finding the best number

#### 3. Expected Value (+EV) Mindset
- Never bet for entertainment; bet for +EV
- True probability vs. implied probability is everything
- Small edges (2-3%) compound massively over time
- A 55% bettor at -110 has ~4.5% ROI — that's elite
- **You don't need to be right often, you need to be right more than the line implies**

#### 4. Market Efficiency Spectrum
| Market | Efficiency |
|--------|------------|
| NFL sides | Very high |
| NBA sides | High |
| NFL/NBA totals | Moderate |
| Player props | Lower |
| Live betting | Variable |
| Obscure markets | Lowest |

- **Implication for us**: Props and totals may offer more edge than spreads

#### 5. Key Numbers & Half-Points
- NFL: 3 and 7 are sacred (margin of victory distribution)
- NBA: 1-5 points matter less; larger margins reduce key number impact
- **Buying points is usually -EV** unless crossing a key number
- Know when a half-point is worth paying for

#### 6. Sharp vs. Public Money
- "Sharps" = professional bettors who move lines
- "Steam moves" = sudden line movement from sharp action
- Reverse Line Movement (RLM) = line moves against public betting %
- **Respect sharp money; don't blindly follow public**
- Opening lines are set to balance theoretical value; closing lines reflect actual market consensus

#### 7. Bankroll Management (Kelly Criterion)
- Full Kelly = bet (edge / odds) of bankroll
- **Fractional Kelly (25-50%)** recommended to reduce variance
- Never bet more than 1-5% of bankroll on a single wager
- Losing streaks happen even to +EV bettors
- Survival > maximization in the short term

#### 8. Building & Protecting Your Edge
- **Edges are fleeting** — markets adapt
- Specialize: better to be great at one thing than mediocre at many
- **Record everything**: pick, line, closing line, reasoning, result
- Analyze results for signal, not just W/L
- Books will limit winning bettors — use multiple accounts, bet through friends if needed

#### 9. Information Value
- Information decays rapidly
- Breaking news (injuries, lineup changes) = short-lived edge
- **Speed matters**: getting down before line moves
- Stale information = no edge

#### 10. Props & Derivatives
- Books have limited resources to price every prop perfectly
- Correlation plays: if you expect a blowout, player props for starters may go UNDER (less playing time)
- **Prop markets are less efficient** but also have higher vig
- Build models for props where books are weakest

---

### Model V3 Implications

| Current State | Recommended Change |
|---------------|-------------------|
| Track W/L only | **Add CLV tracking** |
| Single line source | **Multi-book line shopping** |
| Focus on spreads | **Expand props/totals focus** |
| Arbitrary confidence % | **Tie confidence to edge size + Kelly** |
| No bankroll tracking | **Implement Kelly-based unit sizing** |
| Bet whenever edge found | **Weight for market efficiency (props > sides)** |

### Action Items for Model V3
1. ✅ Track closing line for every pick (CLV = key metric)
2. ✅ Calculate true EV: (model prob × payout) - (1 - model prob)
3. ✅ Implement fractional Kelly for unit sizing
4. ✅ Add market efficiency weight (props get bonus, NFL sides get penalty)
5. ✅ Build line shopping into workflow (compare Hard Rock to consensus)
6. ✅ Track reasoning for every pick (not just result)

---

## Book 2: Sharp Sports Betting – Stanford Wong (2001)

### Background
Stanford Wong = legendary blackjack advantage player (invented "Wonging" — back-counting). Applied same mathematical rigor to sports betting. This book is the OG quantitative sports betting text.

### Core Concepts

#### 1. The Betting Market as a Marketplace
- Lines are not predictions — they're prices designed to balance action
- **The line is right most of the time** — respect market efficiency
- Your job: find the rare mispricing, not outsmart the market constantly
- Books want balanced action; sharps exploit temporary imbalances

#### 2. True Odds vs. Betting Odds
- Convert American odds to implied probability:
  - (-110) = 110/(110+100) = 52.4% implied
  - (+150) = 100/(100+150) = 40% implied
- **Your model must output TRUE probability, then compare to implied**
- Edge = True Prob - Implied Prob
- Only bet when edge exceeds the vig

#### 3. The Vig Deep Dive
| Line | Implied Prob | Hold |
|------|--------------|------|
| -110/-110 | 52.4% each | 4.76% |
| -105/-105 | 51.2% each | 2.44% |
| -115/-105 | 53.5%/51.2% | 4.76% |

- **Reduced juice books are gold** (-105 lines save ~2% per bet)
- Over 1000 bets, 2% = massive profit difference

#### 4. Line Movement Theory
Wong's classification:
- **Opening line**: Book's initial estimate (often beatable)
- **Early sharp action**: Moves the line 30-60 min after open
- **Public money**: Floods in closer to game time
- **Steam move**: Sudden, sharp line movement from syndicate action
- **Closing line**: Most accurate estimate (wisdom of crowds)

**Key insight**: If you can consistently bet BEFORE the line moves against you, you have an edge.

#### 5. Middling & Scalping
- **Middle**: Bet both sides at different numbers hoping to hit between
  - Example: Take Team A +7, later take Team B -4. If margin is 5-6, win both
- **Scalp (arbitrage)**: Lock guaranteed profit from line discrepancies
  - Requires multiple books with different lines
  - Rare but risk-free

#### 6. Teaser Math (NFL)
Wong did the original teaser EV analysis:
- 6-point 2-team teasers: Move through 3 and 7 = valuable
- **Wong teaser**: Tease home underdogs through 3 and 7 specifically
- Most teasers are -EV; Wong teasers can be +EV

#### 7. Totals Strategy
- Totals are often less efficient than sides
- **Weather impacts totals more than spreads**
- Wind, rain, cold = lean UNDER
- Dome games normalize totals
- Pace of play and coaching tendencies matter

#### 8. Handicapping Fundamentals
Wong's hierarchy of importance (NFL):
1. Injuries (especially QB)
2. Home field advantage
3. Situational spots (revenge, lookahead, letdown)
4. Recent performance vs. season-long metrics
5. Weather
6. Referee tendencies

For NBA:
1. Rest differential (B2B = significant)
2. Injuries to stars
3. Travel/schedule spots
4. Pace matchups
5. Home court (~3 pts on average)

#### 9. Record Keeping (Wong's Original Tracking Sheet)
Track for every bet:
- Date, game, bet type
- Line when bet placed
- Closing line (calculate CLV)
- Result
- Reasoning/notes
- Confidence level

**Review weekly**: Look for patterns in wins AND losses

#### 10. Bankroll & Survival
- **Survival is job #1** — you can't win if you're broke
- 1-2% of bankroll per bet max
- 200+ unit bankroll to weather variance
- Never chase losses
- Flat betting > aggressive scaling for most bettors

### Wong's Golden Rules
1. "The line is usually right" — don't fight the market blindly
2. "Bet early or don't bet" — closing line is too efficient
3. "Keep detailed records or quit" — gut feel doesn't scale
4. "Shop every line" — worst sin is betting a bad number
5. "Specialize" — know one sport deeply beats dabbling in many

---

### Model V3 Implications (Additive to Book 1)

| Wong Insight | V3 Implementation |
|--------------|-------------------|
| True odds calculation | Output probability %, convert to fair line |
| Line movement tracking | Log open line + close line for every pick |
| Vig awareness | Prioritize reduced juice books |
| Rest differential (NBA) | Already in model — keep/weight higher |
| Totals efficiency | Lean into totals model, less into spreads |
| Weather for totals | Add weather factor (outdoor games) |

### Action Items
1. ✅ Convert model output to true probability %
2. ✅ Calculate fair line from probability
3. ✅ Compare fair line to market to find edge
4. ✅ Track opening vs. closing lines
5. ✅ Document reasoning for every pick
6. ✅ Add weather data for outdoor sports (future: NFL)

---

## Book 3: Squares & Sharps, Suckers & Sharks – Joseph Buchdahl (2016)

### Background
Buchdahl = statistician who writes for Pinnacle. This book bridges betting strategy with cognitive psychology and statistical rigor. Heavy on the "why most bettors fail" angle.

### Core Thesis
**Most betting success is luck mistaken for skill.** The book ruthlessly applies statistical tests to separate real edge from noise.

### Key Concepts

#### 1. The Curse of Small Samples
- **100 bets at 55% = statistically meaningless**
- Need 1000+ bets to confirm skill with confidence
- Formula for required sample size:
  ```
  n = (z² × p × (1-p)) / E²
  where z=1.96 (95% CI), p=win rate, E=margin of error
  ```
- A 55% bettor needs ~1,000 bets to be 95% confident they're not just lucky
- **Implication: Don't trust small sample results (including ours at 1-3)**

#### 2. Regression to the Mean
- Hot streaks cool off; cold streaks warm up
- Bettors who crush it early often regress
- **Don't overfit to recent performance**
- True edge is revealed over LONG samples
- "Past performance does not guarantee future results" — statistically proven

#### 3. Cognitive Biases in Betting

| Bias | Description | How It Hurts |
|------|-------------|--------------|
| **Confirmation bias** | Seek info that confirms beliefs | Ignore contradicting evidence |
| **Hindsight bias** | "I knew it all along" | Overconfidence in predictions |
| **Gambler's fallacy** | "Due for a win" | Bet size after losses |
| **Recency bias** | Overweight recent events | Chase hot teams |
| **Narrative fallacy** | Create stories to explain randomness | Overthink analysis |
| **Overconfidence** | Believe you're better than you are | Bet too large |

**Key insight**: The brain is wired to find patterns even in randomness. Fight this.

#### 4. The Efficient Market Hypothesis (Applied to Betting)
- Betting markets are MOSTLY efficient
- Closing lines reflect collective wisdom
- Consistent edge requires either:
  - Superior information
  - Superior models
  - Faster execution
- Most "systems" are just curve-fitting to past data

#### 5. Tipster Evaluation
Buchdahl's framework for evaluating any tipster/model:
1. **Sample size**: 500+ bets minimum
2. **Track record verification**: Independent, not self-reported
3. **Closing line value**: Do they beat the close?
4. **Yield consistency**: Stable over time, not boom/bust
5. **Stake weighting**: Did they bet heavy on winners?

**Red flags**:
- Cherry-picked results
- Vague or changing staking plans
- No closing line data
- "Guaranteed" returns

#### 6. P-Hacking & Data Mining
- If you test enough variables, you'll find "significant" patterns by chance
- **Danger**: Backtests that look amazing but fail forward
- Example: "Teams wearing red on Tuesdays cover 68%!" → spurious
- **Solution**: Out-of-sample testing, forward-testing, skepticism

#### 7. Bayesian Thinking
- Start with a prior belief (base rate)
- Update based on new evidence
- Don't swing wildly based on single results
- **Example**:
  - Prior: 52% of bets win on average
  - You go 7-3 in first 10 bets
  - Bayesian update: ~54% (not 70%)
  - Small samples barely move the needle

#### 8. The Long Run Problem
- "In the long run we're all dead" — Keynes
- Even +EV bettors can go broke before the long run arrives
- Variance is brutal over 100-500 bets
- **Must survive short-term variance to reach long-term EV**
- This is why bankroll management > edge size

#### 9. When to Quit
Buchdahl's honest assessment:
- Most bettors should quit (negative EV)
- If you can't prove positive CLV over 1000+ bets, you're probably losing
- Entertainment value ≠ investment return
- **Know the difference between hobby and business**

#### 10. The Psychology of Losing
- Losses hurt ~2x as much as wins feel good (Kahneman)
- This creates irrational behavior:
  - Chasing losses
  - Cutting winners short
  - Increasing stakes when down
- **Counter**: Pre-commit to stakes, automate decisions, remove emotion

---

### Buchdahl's Brutal Truths
1. "You're probably not as good as you think"
2. "Your hot streak is probably luck"
3. "Your model is probably overfit"
4. "Most tipsters are frauds or lucky"
5. "If you can't beat closing line, you're losing"

---

### Model V3 Implications

| Buchdahl Insight | V3 Implementation |
|------------------|-------------------|
| Small sample warning | Add confidence intervals, don't overreact to 1-3 start |
| CLV as key metric | Already added — reinforce this |
| Cognitive bias awareness | Document reasoning BEFORE result to avoid hindsight |
| Out-of-sample testing | Split backtest data: train on 70%, test on 30% |
| Regression to mean | Don't chase hot trends, trust long-term model |
| Bayesian updates | Slowly adjust model weights, not drastic changes |

### Statistical Benchmarks
- **Minimum sample**: 500 bets before trusting results
- **CLV target**: +1% or better closing line value
- **Yield target**: 2-5% ROI is elite
- **Confidence interval**: Report range, not point estimate

---

## Book 4: Mathletics – Wayne Winston (2009, updated 2012)

### Background
Winston = Indiana University prof, consulted for Dallas Mavericks (helped build their analytics department). This is THE sports analytics textbook. Covers baseball, basketball, and football with actual math.

### Focus: Basketball Analytics (Most Relevant to Us)

#### 1. Pythagorean Expectation
Original (baseball): Win% = RS² / (RS² + RA²)
Basketball adaptation:
```
Expected Win% = PF^14 / (PF^14 + PA^14)
where PF = points for, PA = points against
```
- Exponent varies by sport (14 for NBA, 2.37 for MLB, 2.5 for NFL)
- **Use case**: Identify teams over/underperforming their point differential
- Over-performers regress down; under-performers regress up

#### 2. The Four Factors (Dean Oliver via Winston)
What wins basketball games, in order of importance:

| Factor | Weight | Formula |
|--------|--------|---------|
| eFG% | 40% | (FG + 0.5×3P) / FGA |
| TOV% | 25% | TO / (FGA + 0.44×FTA + TO) |
| OREB% | 20% | OREB / (OREB + Opp DREB) |
| FT Rate | 15% | FT / FGA |

**For model**: Weight shooting efficiency highest, turnovers second

#### 3. Offensive & Defensive Ratings (Per 100 Possessions)
```
Possessions ≈ FGA - OREB + TO + 0.44×FTA

ORtg = (Points / Possessions) × 100
DRtg = (Opp Points / Opp Possessions) × 100
Net Rating = ORtg - DRtg
```
- **Already using this in our model** ✅
- Net rating is best single predictor of team quality

#### 4. Pace Adjustments
Raw stats are meaningless without pace context:
```
Pace = Possessions / Minutes × 48

Pace-Adjusted Stat = (Raw Stat / Team Pace) × League Avg Pace
```
- Fast teams inflate counting stats
- **Must adjust for pace when comparing players/teams**
- We have pace data — good ✅

#### 5. Adjusted Plus/Minus (APM)
- Measures player impact with/without on court
- Ridge regression to stabilize estimates
- **Basis for modern metrics like RPM, RAPTOR, EPM**
- Single best measure of player value

#### 6. Player Value Models
Winston's hierarchy of basketball metrics:
1. **APM/RAPM**: Best but noisy in small samples
2. **BPM (Box Plus/Minus)**: Box score approximation of APM
3. **Win Shares**: Credit for team wins
4. **PER**: Overweights volume, flawed but common

For injury adjustments:
```
Player Impact ≈ (Player APM - Replacement APM) × Minutes%
```

#### 7. Home Court Advantage Analysis
Winston's findings:
- NBA HCA ≈ 3-4 points (we use 3.9 ✅)
- HCA varies by arena (altitude, noise)
- HCA declining over time (travel improvements)
- Back-to-backs reduce HCA effect

#### 8. Hot Hand Research
Winston examines the "hot hand":
- Original Gilovich study: Hot hand is myth
- Modern reanalysis: Small hot hand effect exists
- **For betting**: Don't overweight recent shooting performances
- Regression to mean dominates

#### 9. Predicting Game Outcomes
Winston's framework:
```
Predicted Margin = (Home ORtg - Away DRtg)/2 + (Away ORtg - Home DRtg)/2 + HCA
                 = (Home NetRtg - Away NetRtg)/2 + HCA
```
- Adjust for pace matchup
- Adjust for rest
- Adjust for injuries (using APM impact)

#### 10. Totals Prediction
```
Predicted Total = (Home ORtg + Away ORtg) × Expected Pace / 100

Expected Pace = (Home Pace + Away Pace) / 2  [simplified]
             = Adjusted for opponent pace tendencies [better]
```
- Fast vs fast = OVER lean
- Slow vs slow = UNDER lean
- **We have this in totals_model.py** ✅

#### 11. Regression Applications
Winston uses regression for:
- Predicting future performance from past
- Adjusting for strength of schedule
- Isolating variables (pace, opponent, location)
- **Key insight**: R² in sports is low; embrace uncertainty

#### 12. The Value of a Possession
Every possession matters equally:
- Don't value "clutch" possessions more (statistically)
- Late-game heroics are overrated
- Consistent efficiency > dramatic moments
- **Implication**: Model full-game efficiency, not clutch stats

---

### Model V3 Implications

| Winston Concept | Current State | V3 Action |
|-----------------|---------------|-----------|
| Pythagorean Win% | Not using | Add to identify regression candidates |
| Four Factors | Implicit | Explicitly weight eFG% > TOV% > OREB% > FT Rate |
| ORtg/DRtg | Using ✅ | Keep as primary metric |
| Pace adjustment | Using ✅ | Verify all stats are pace-adjusted |
| APM for injuries | Using tiers | Upgrade to actual APM data if available |
| Predicted margin formula | Similar | Verify math matches Winston |
| Totals formula | Using ✅ | Confirm pace calculation |

### Key Formulas to Implement
```python
# Pythagorean expected wins (regression detector)
def pythagorean_wins(pf, pa, games):
    exp_win_pct = pf**14 / (pf**14 + pa**14)
    return exp_win_pct * games

# Four Factors composite
def four_factors_score(efg, tov, oreb, ft_rate):
    return 0.40*efg + 0.25*(1-tov) + 0.20*oreb + 0.15*ft_rate

# Predicted margin (clean version)
def predict_margin(home_net, away_net, hca=3.9):
    return (home_net - away_net) / 2 + hca
```

---

## Book 5: Basketball on Paper – Dean Oliver (2004)

### Background
Oliver = Godfather of basketball analytics. Worked for Sonics, Nuggets, Kings, ESPN. This book INVENTED modern basketball analytics. The Four Factors, offensive/defensive ratings, pace — all Oliver.

### Core Philosophy
> "Basketball is a game of possessions, not minutes."

Everything flows from this. Possessions are the unit of analysis.

### The Four Factors (Definitive Version)

Oliver's original formulation with exact weights:

| Factor | Offense Formula | Defense Formula | Weight |
|--------|-----------------|-----------------|--------|
| **eFG%** | (FG + 0.5×3P) / FGA | Same (opponent) | **40%** |
| **TOV%** | TOV / (FGA + 0.44×FTA + TOV) | Same (opponent) | **25%** |
| **OREB%** | OREB / (OREB + Opp DRB) | DRB / (Opp ORB + DRB) | **20%** |
| **FT Rate** | FT / FGA | Same (opponent) | **15%** |

**Why these weights?**
- Shooting has highest correlation with winning
- Turnovers = lost possessions (can't score if you don't have the ball)
- Offensive rebounds = extra possessions
- Free throws = efficient points (0.44 accounts for and-ones)

### Possession Estimation
```
Possessions ≈ FGA - OREB + TOV + 0.44 × FTA
```
- The 0.44 coefficient accounts for and-one situations
- More precise than simple FGA + TO

### Offensive & Defensive Ratings (Oliver's Creation)
```
Offensive Rating = (Points Scored / Possessions) × 100
Defensive Rating = (Points Allowed / Possessions) × 100
```
- League average ≈ 110 (varies by era)
- Elite offense: 115+
- Elite defense: <108
- **Net Rating = ORtg - DRtg** (best single team metric)

### Individual Offensive Rating
Oliver's formula for player ORtg (complex):
```
Individual ORtg considers:
- Points produced (including assists)
- Possessions used
- Team context adjustments
```
- Available on Basketball-Reference
- More nuanced than points per game

### Pace Analysis
```
Pace = Possessions per 48 minutes

Team Expected Pace = f(own pace tendency, opponent pace tendency)
```
- Fast teams (100+ pace): More possessions, more variance
- Slow teams (<97 pace): Fewer possessions, lower totals
- **Matchup pace = weighted average** (not simple average)

### Skill Curves & Diminishing Returns
Oliver's insight on team building:
- Adding shooting when you can't shoot = high value
- Adding shooting when you already shoot well = low value
- **Balance across Four Factors > excellence in one**

### Playoff vs. Regular Season
Key Oliver finding:
- Pace SLOWS in playoffs (more half-court)
- Defense becomes more important
- Stars matter more (more possessions to them)
- **Regular season models need playoff adjustment**

### The 0.44 Free Throw Coefficient
Why 0.44 and not 0.5?
- 2 FTA = ~1 possession (makes sense)
- But and-ones: 1 FTA doesn't end possession
- Technical FTs: don't use possession
- 0.44 is empirically derived correction

### Player Replacement Value
Oliver's concept of "replacement level":
- Replacement player ≈ -2 to -3 ORtg impact
- Stars can be +5 to +8 ORtg
- Role players cluster around 0
- **Injury impact = (Star ORtg - Replacement ORtg) × Minutes%**

### Clutch Analysis (Oliver's Take)
- "Clutch" is mostly noise
- Sample sizes too small
- Players don't suddenly become different
- **Model full-game performance, not "clutch"**

### The Three Pointer Revolution (Predicted)
Oliver (in 2004!) noted:
- 3-pt attempt = 1.5× value of 2-pt attempt (when made)
- League undervaluing threes
- eFG% captures this: 3P made counts as 1.5 FG
- **He predicted the shooting revolution**

---

### Model V3 Implications

| Oliver Principle | V3 Implementation |
|------------------|-------------------|
| Four Factors weights | Apply 40/25/20/15 weighting to team eval |
| Possessions as unit | Already pace-adjusting ✅ |
| ORtg/DRtg | Primary metric ✅ |
| Pace matchup | Use weighted average, not simple |
| Replacement level | Refine injury adjustments with actual ORtg deltas |
| Playoff adjustments | Add flag for playoff games (future) |
| eFG% > FG% | Use eFG% in any shooting analysis |

### Four Factors Quick Reference (For Each Game)
```python
def four_factors_edge(team, opponent):
    """Compare Four Factors to find edges"""
    factors = {
        'efg': (team.efg - opp.efg_allowed) * 0.40,
        'tov': (opp.tov_rate - team.tov_rate) * 0.25,  # lower is better
        'oreb': (team.oreb_rate - opp.dreb_rate) * 0.20,
        'ft': (team.ft_rate - opp.ft_rate_allowed) * 0.15
    }
    return sum(factors.values())
```

### The Oliver Hierarchy
When analyzing any game:
1. **Net Rating differential** (most predictive)
2. **Four Factors matchup** (why they'll win/lose)
3. **Pace expectation** (sets the total)
4. **Context** (rest, injuries, travel)

---

## Book 6: Thinking Basketball – Ben Taylor (2016, updated)

### Background
Taylor = Modern analytics guru, YouTube educator, created Backpicks GOAT rankings. Bridges film study with advanced stats. His work focuses on PROCESS not just outcomes.

### Core Philosophy
> "What a player does without the ball is as important as what they do with it."

Stats miss half the game. Taylor combines tracking data + film to capture full impact.

### Key Concepts

#### 1. Offensive Roles & The Creation Spectrum

| Role | Description | Value |
|------|-------------|-------|
| **Primary Creator** | Ball-handler who creates for self/others | Highest ceiling, most load |
| **Secondary Creator** | Can create off dribble occasionally | Versatile |
| **Spacer** | Gravity through shooting threat | Enables creators |
| **Finisher** | Scores on others' creation | Dependent value |
| **Connector** | Short rolls, swing passes, DHOs | Underrated glue |

**Insight**: Teams need balance. Too many creators = inefficiency. Too few = predictability.

#### 2. Gravity (Taylor's Key Concept)
"Gravity" = How much defensive attention a player commands

- High gravity: Defense must account for them even without ball
- Creates open shots for teammates
- **NOT captured in box score**
- Examples: Steph Curry warps defenses; even his misses have value

**Betting implication**: Teams with high-gravity players are more efficient than stats suggest

#### 3. Offensive Load vs. Efficiency

Taylor's discovery:
```
As usage increases, efficiency decreases (for most players)
```
| Usage | Expected TS% Drop |
|-------|-------------------|
| 20% → 25% | -1.5% |
| 25% → 30% | -2.0% |
| 30% → 35% | -3.0% |

**Key insight**: Stars who maintain efficiency at high usage (Jokić, peak LeBron) are unicorns.

**Injury implication**: When star is out, remaining players' efficiency drops AS their usage increases. Double whammy.

#### 4. Shot Quality Analysis

Not all shots are equal:
| Shot Type | Avg eFG% | Quality |
|-----------|----------|---------|
| Rim (uncontested) | 70%+ | Elite |
| Rim (contested) | 50-55% | Good |
| Corner 3 | 40%+ | Good |
| Above-break 3 (open) | 38% | Good |
| Midrange | 40-42% | Meh |
| Long 2 | 35-38% | Bad |

**Team evaluation**: Shot profile matters as much as makes/misses

#### 5. Playmaking Value

Taylor's playmaking hierarchy:
1. **Creation** — Making something from nothing
2. **Passing** — Delivering the ball well
3. **Decision-making** — Right play at right time

Assists don't capture creation. Some assists are "easy" (Draymond to wide-open Klay). Some are hard (LeBron creating from nothing).

**Box +/- limitation**: Overvalues assist totals, misses creation

#### 6. Defensive Impact

Taylor's defensive categories:
| Type | Measurable? | Value |
|------|-------------|-------|
| **Rim Protection** | Yes (DFG% at rim) | Highest impact |
| **Perimeter Stopper** | Partially | Moderate impact |
| **Help Defense** | Film only | Underrated |
| **Switchability** | Context-dependent | Playoff premium |
| **Positioning/IQ** | Film only | Hardest to measure |

**Insight**: Elite rim protectors (Gobert, Wemby) worth ~4-6 pts per 100

#### 7. Spacing & Modern Offense

The spacing math:
- 5 shooters = defense can't help
- 1 non-shooter = defense helps off them
- 2 non-shooters = cramped offense

**Team evaluation**: Count real shooting threats (>35% on volume), not just listed positions

#### 8. Historical Context for Player Evaluation

Taylor's era adjustments:
- Pace varies wildly (1960s: 120+, 2000s: 90s, 2020s: 100+)
- 3PT era changed everything
- Rule changes affect stats (hand-checking, freedom of movement)

**Lesson**: Compare players to their era's league average, not raw numbers

#### 9. Playoff vs. Regular Season Value

Taylor's findings on playoff success:
1. **Rim protection scales** — More valuable in playoffs
2. **Creation scales** — Can't hide in half-court
3. **Shooting is volatile** — Hot/cold swings
4. **Defensive versatility scales** — Switching matters more

**Betting implication**: Weight rim protection + creation higher for playoff games

#### 10. The Eye Test + Stats Synthesis

Taylor's approach:
1. Start with impact metrics (RAPM, EPM, etc.)
2. Watch film to understand WHY
3. Look for what stats MISS (gravity, off-ball, help D)
4. Context matters (teammates, role, opponent)

> "Stats tell you WHAT happened. Film tells you WHY."

---

### Model V3 Implications

| Taylor Concept | V3 Action |
|----------------|-----------|
| Gravity | Can't directly model, but respect star impact beyond stats |
| Load vs efficiency | When star out, penalize team MORE than just their rating |
| Shot quality | Add shot profile data if available |
| Rim protection | Weight teams with elite rim protectors higher on defense |
| Spacing | Count 3PT threats; cramped offenses underperform |
| Playoff adjustments | Different weights for playoff model (future) |

### Injury Adjustment Upgrade
```python
def injury_impact_taylor(player_usage, player_ts, team_context):
    """
    Taylor-informed injury adjustment:
    1. Lose player's direct production
    2. Remaining players' efficiency drops as usage increases
    3. Lose player's gravity (off-ball value)
    """
    direct_loss = player_usage * player_ts * minutes_share
    efficiency_drop = estimate_usage_redistribution_cost()
    gravity_loss = estimate_gravity_value()  # harder to quantify
    return direct_loss + efficiency_drop + gravity_loss
```

### Thinking Basketball Data Sources
- thinkingbasketball.net — Free daily stats
- Player cards with percentiles
- Team trends (hot/cold last month)
- **Useful for recent form analysis**

---

## Book 7: Basketball Analytics: Spatial Tracking – Stephen M. Shea (2014)

### Background
Shea = Academic (St. Johns) who pioneered spatial analytics using tracking data. Wrote this as tracking tech (SportVU, later Second Spectrum) was emerging. Runs squared2020.com for advanced research.

### Core Innovation
> "Where players ARE on the court matters as much as what they DO."

Tracking data captures X,Y coordinates 25x per second. This unlocks analysis impossible with box scores.

### Key Concepts

#### 1. Shot Quality Models (Expected eFG%)

Every shot has an expected value based on:
```
xeFG% = f(location, defender_distance, shot_clock, dribbles, touch_time)
```

| Factor | Impact on xeFG% |
|--------|-----------------|
| Distance to rim | Largest factor |
| Defender distance | +5% per foot of space |
| Catch & shoot vs off-dribble | C&S +4-5% |
| Shot clock (<4 sec) | -3-5% |
| Dribbles before shot | Each dribble -1% |

**Application**: Compare actual eFG% to xeFG% to find shooters running hot/cold

#### 2. Spatial Spacing Metrics

Measuring court spacing mathematically:
```
Convex Hull Area = Area of polygon formed by 5 offensive players
Larger area = better spacing
```

| Spacing Quality | Convex Hull |
|-----------------|-------------|
| Elite | 650+ sq ft |
| Good | 550-650 sq ft |
| Poor | <500 sq ft |

**Why it matters**: Cramped spacing = easier help defense = lower eFG%

#### 3. Defender Distance Analysis

Tracking captures closest defender on every shot:
| Defender Distance | eFG% Impact |
|-------------------|-------------|
| 0-2 ft (tight) | Baseline |
| 2-4 ft (close) | +3-5% |
| 4-6 ft (open) | +8-10% |
| 6+ ft (wide open) | +12-15% |

**Betting insight**: Teams generating more "wide open" looks outperform box score efficiency

#### 4. Player Speed & Movement

Tracking captures player velocity:
```
Average Speed = Distance traveled / Time
Acceleration patterns = Explosiveness
```

| Metric | Use Case |
|--------|----------|
| Offensive speed | Fast break tendency |
| Defensive speed | Close-out quality |
| Distance traveled | Fatigue indicator |
| Speed differential | Blow-by potential |

**Fatigue detection**: Players average speed drops in 4th quarter, B2Bs

#### 5. Rebounding Positioning

Where players are when shot goes up:
```
Rebound Probability = f(distance_to_rim, box_out_position, trajectory)
```

- Long rebounds (3PA) travel further from rim
- Second Spectrum tracks "box out" events
- **Offensive rebound% is partially predictable from positioning**

#### 6. Drive Analysis

Tracking defines "drives" precisely:
```
Drive = Player moves ball from outside paint → into paint
```

| Drive Outcome | Value |
|---------------|-------|
| Finish at rim | High |
| Kick to corner 3 | High |
| Kick to above-break 3 | Medium |
| Midrange pull-up | Low |
| Turnover | Very negative |

**Team profile**: High drive rate + high kick-out rate = modern elite offense

#### 7. Defensive Coverage Schemes

Tracking reveals defensive assignments:
```
Drop coverage vs Hedge vs Switch vs Blitz
```

| Scheme | Gives Up | Takes Away |
|--------|----------|------------|
| Drop | Pull-up 3s | Rim pressure |
| Hedge | Corner 3s | Ball-handler 3s |
| Switch | Mismatches | Scheme reads |
| Blitz | Roll man | Ball-handler |

**Matchup analysis**: Know defense's tendency to predict shot distribution

#### 8. Transition vs Half-Court Splits

Tracking separates possession types:
| Type | Avg Points/Poss |
|------|-----------------|
| Transition (early) | 1.15+ |
| Semi-transition | 1.05-1.10 |
| Half-court | 0.95-1.00 |

**Pace implication**: Fast teams get more transition opps = higher ORtg

#### 9. Expected Possession Value (EPV)

Most advanced tracking metric:
```
EPV = Probability-weighted value of possession at any moment
```
- Updates in real-time as play develops
- Measures decision-making quality
- "EPV Added" = actual outcome vs expected

**Star evaluation**: High EPV Added = elite decision-makers (CP3, LeBron, Jokić)

#### 10. Touch Time & Ball Movement

Tracking ball location:
```
Touch Time = How long each player holds ball
Ball Movement = Passes per possession
```

| Metric | Good Sign | Bad Sign |
|--------|-----------|----------|
| Low touch time | Ball movement | Indecision |
| High touch time | ISO creation | Ball stopping |
| More passes | Open shots | Wasted clock |

**Team style**: Spurs/Warriors-style = low touch, many passes. ISO-heavy = high touch, few passes.

---

### Model V3 Implications

| Tracking Concept | V3 Possibility |
|------------------|----------------|
| Shot quality (xeFG%) | NBA.com has basic shot charts; limited public data |
| Spacing metrics | Not public; proxy with 3PT attempt rate |
| Defender distance | Not public; proxy with open 3PT% |
| Drive rate | Available on NBA.com |
| Transition frequency | Available on NBA.com |
| EPV | Not public (proprietary) |

### Available Public Proxies
Since tracking data is mostly proprietary, use these proxies:

```python
# Spacing proxy
spacing_proxy = team_3pa_rate  # More 3PA = likely better spacing

# Shot quality proxy  
shot_quality_proxy = rim_fga_rate + corner_3_rate  # Best shot types

# Transition proxy
transition_proxy = fast_break_pts_per_game / pace

# Open shot proxy
open_shot_proxy = wide_open_3pt_pct  # Available on NBA.com
```

### Data Source
- **NBA.com/stats** — Has some tracking stats publicly
- **Second Spectrum** — Powers NBA tracking (not public)
- **squared2020.com** — Shea's research blog

---

## Book 8: Basketball Analytics: Objective and Efficient Strategies – Shea & Baker (2013)

### Background
Shea & Baker's earlier work, focused on STRATEGY optimization rather than tracking. Game theory, decision-making, roster construction. More actionable for betting than the spatial book.

### Core Theme
> "Most in-game decisions are suboptimal. Math can fix them."

Coaches make decisions based on tradition/intuition. Analytics often disagrees.

### Key Concepts

#### 1. Optimal Shot Selection

The math of shot selection:
```
Expected Points = P(make) × Points

3PA: 0.36 × 3 = 1.08 pts
2PA: 0.50 × 2 = 1.00 pts
FT: 0.75 × 2 = 1.50 pts (if fouled on 2PA)
```

**Key insight**: Even 33% 3PT shooting = 1.00 pts (same as 50% 2PT)
- Most teams should shoot MORE threes
- Long 2s are almost always bad
- Fouling to get to line can be +EV

#### 2. When to Foul (Down 3, End of Game)

Classic debate: Foul up 3 with seconds left?
```
If opponent shoots 3:
  P(make) ≈ 35% → Lose/OT
  P(miss) ≈ 65% → Win

If you foul:
  They shoot FTs, you get ball back
  Multiple scenarios play out
```

**Shea's finding**: Fouling is often BETTER than defending 3, but coaches rarely do it.

#### 3. Intentional Fouling Bad FT Shooters

The "Hack-a-Shaq" math:
```
Target FT%: 50%
Expected pts per 2 FTs: 1.00
League avg half-court poss: 1.05

If opponent FT% < 52%, fouling is +EV
```

**Thresholds**:
- <50% FT = foul aggressively
- 50-60% FT = situational
- >60% FT = don't bother

#### 4. Lineup Optimization

Finding optimal 5-man units:
```
Maximize: Lineup NetRtg
Subject to: Minutes constraints, rest, matchups
```

Problems with lineup data:
- Small samples (most lineups <100 min)
- Opponent quality varies
- Score effects (garbage time)

**Solution**: Regularized estimates (like RAPM but for lineups)

#### 5. Clutch Time Strategy

Defining "clutch":
```
NBA.com: Last 5 min, margin ≤5
```

Clutch findings:
- Pace slows dramatically
- ISO rate increases
- 3PA rate decreases (questionable choice)
- Stars get higher usage (correct choice)

**Betting angle**: Teams with clutch-ISO stars (KD, Kawhi) outperform in close games

#### 6. Timeout Optimization

When to call timeouts:
```
Optimal: After opponent run (breaks momentum)
Suboptimal: Saving for end (may not need them)
```

Shea found coaches UNDERUSE timeouts early in games.

**Momentum indicator**: Team on 8-0 run without timeout = coach issue

#### 7. Roster Construction Theory

Building an optimal roster:
```
Maximize: Team Win Probability
Subject to: Salary cap, roster spots
```

Key findings:
- Star concentration > depth (in playoffs)
- Spacing is non-negotiable
- Defensive versatility has premium
- 3&D wings are undervalued (were at time of writing)

#### 8. Rest vs. Rust Trade-off

Optimal rest patterns:
```
1 day rest = optimal
2 days rest = slight decline (rust)
3+ days rest = more rust
Back-to-back = fatigue
```

**B2B quantified**: ~3-4% drop in win probability

#### 9. Home Court Advantage Deep Dive

HCA components (Shea's breakdown):
| Factor | Contribution |
|--------|--------------|
| Travel fatigue | 30% |
| Crowd noise | 25% |
| Referee bias | 20% |
| Familiarity/routine | 15% |
| Altitude (select) | 10% |

**Altitude effect**: Denver/Utah = +1 additional HCA point

#### 10. Playoff vs. Regular Season Adjustments

Playoff changes:
| Factor | Regular Season | Playoffs |
|--------|----------------|----------|
| Pace | Normal | Slower |
| Ref whistle | Normal | Tighter (fewer fouls) |
| Star minutes | 32-34 | 38-42 |
| Rotation depth | 9-10 | 7-8 |
| Scheme preparation | Generic | Specific |

**Betting implication**: Regular season data overvalues depth, undervalues stars

---

### Model V3 Implications

| Strategy Concept | V3 Implementation |
|------------------|-------------------|
| Shot selection | Compare team shot profile to optimal |
| Clutch performance | Track clutch NetRtg separately |
| B2B impact | Already included (+3-4 pts) ✅ |
| Altitude | Add Denver/Utah HCA boost |
| Playoff adjustments | Build separate playoff model weights |
| Roster concentration | Weight star-heavy teams higher |

### Actionable Betting Angles

```python
# Shot selection edge
def shot_selection_score(team):
    """Teams taking efficient shots have hidden edge"""
    optimal_mix = 0.40  # 40% of shots from 3 or rim
    actual_mix = team.rim_rate + team.three_rate
    return actual_mix - optimal_mix

# Altitude adjustment
def altitude_hca(home_team):
    """Denver and Utah get extra HCA"""
    if home_team in ['DEN', 'UTA']:
        return 1.0  # extra point
    return 0.0

# Clutch team identifier
def clutch_rating(team):
    """Teams with ISO closers perform better in close games"""
    return team.clutch_net_rtg - team.overall_net_rtg
```

---

## Book 9: Basketball Data Science with R – Zuccolotto & Manisera (2020)

### Background
Academic text from University of Brescia (Italy). Comes with **BasketballAnalyzeR** R package on CRAN. Bridges theory → implementation. Very practical, code-heavy.

### Core Value
> "Here's how to actually BUILD the analytics, not just understand them."

Every concept has working R code. Translatable to Python.

### Key Techniques

#### 1. Shot Chart Visualization & Analysis

```r
# Kernel density estimation for shot charts
shotchart(data, type="kde", ...)
```

Key outputs:
- Hexbin shot charts
- Hot/cold zone detection
- Expected vs actual by zone
- Shot selection profiles

**Betting use**: Compare team shot profiles to league optimal

#### 2. Player Clustering

Unsupervised learning to group similar players:
```r
# K-means on player stat profiles
player_clusters <- kmeans(player_stats, centers=5)
```

Cluster types typically found:
| Cluster | Profile |
|---------|---------|
| 1 | High-usage scorers |
| 2 | 3&D wings |
| 3 | Rim-running bigs |
| 4 | Floor generals |
| 5 | Stretch bigs |

**Use**: Identify replacement-level matches for injury adjustments

#### 3. Network Analysis (Passing Networks)

Visualize ball movement as graph:
```r
# Assist network
assist_network(data, player1, player2, assists)
```

Metrics derived:
- **Centrality**: Who's the hub?
- **Betweenness**: Who connects sub-groups?
- **Clustering coefficient**: Clique-y or distributed?

**Insight**: Teams with high network centrality (one playmaker) are volatile

#### 4. Principal Component Analysis (PCA) on Stats

Reduce dimensionality of player stats:
```r
# Find underlying factors
pca_result <- prcomp(player_stats, scale=TRUE)
```

Typical components:
| PC | Interpretation |
|----|----------------|
| PC1 | Overall production (scoring + rebounds) |
| PC2 | Perimeter vs interior |
| PC3 | Efficiency vs volume |

**Use**: Simplify player comparison, reduce overfitting

#### 5. Possession-Based Metrics Implementation

Code for all the Oliver metrics:
```r
# Offensive rating calculation
ORtg <- (PTS / POSS) * 100

# Possessions estimate
POSS <- FGA - OREB + TOV + 0.44 * FTA

# Four Factors
eFG <- (FG + 0.5 * FG3) / FGA
TOVrate <- TOV / (FGA + 0.44 * FTA + TOV)
OREBrate <- OREB / (OREB + OppDREB)
FTrate <- FT / FGA
```

**Already implemented in our model** ✅

#### 6. Expected Points Models

Building xPts from shot data:
```r
# Logistic regression for shot probability
shot_model <- glm(made ~ distance + defender_dist + shot_clock, 
                  family=binomial, data=shots)
xPts <- predict(shot_model, type="response") * point_value
```

**Key features**:
- Shot distance
- Shot type (catch/shoot, off-dribble)
- Shot clock
- Previous action

#### 7. Lineup Analysis

Evaluating 5-man combinations:
```r
# Plus-minus by lineup
lineup_pm <- aggregate(plus_minus ~ lineup_id, data, sum)
lineup_poss <- aggregate(possessions ~ lineup_id, data, sum)
lineup_rating <- (lineup_pm / lineup_poss) * 100
```

**Caution**: Massive sample size issues. Need regularization.

#### 8. Variability Analysis

Measuring consistency vs volatility:
```r
# Coefficient of variation
CV <- sd(player_pts) / mean(player_pts)
```

| Player Type | CV |
|-------------|-----|
| Consistent star | 0.3-0.4 |
| Volatile scorer | 0.5-0.6 |
| Role player | 0.6+ |

**Betting use**: High-CV players = wider prop distributions

#### 9. Spatial Analysis Techniques

Court geography with R:
```r
# Voronoi tessellation for spacing
# Convex hull for team spread
# Heat maps for position tendencies
```

Applicable even without tracking:
- Shot chart locations (NBA.com)
- Play-by-play locations
- Zone-based analysis

#### 10. Time Series for Performance Trends

Rolling averages and change detection:
```r
# Moving average
rolling_mean <- zoo::rollmean(pts, k=10)

# Structural break detection
break_points <- strucchange::breakpoints(pts ~ time)
```

**Use cases**:
- Detect shooting slumps/hot streaks
- Identify fatigue patterns (late season)
- Spot lineup change impacts

---

### Model V3 Implementation Ideas

| Technique | V3 Application |
|-----------|----------------|
| Shot charts | Add team shot profile score |
| Player clustering | Match injured players to replacements |
| Network analysis | Flag iso-heavy vs ball-movement teams |
| PCA | Reduce stat dimensions for model inputs |
| xPts | If shot-level data available |
| Lineup regularization | Don't trust small lineup samples |
| CV for volatility | Adjust prop confidence by player consistency |
| Time series | Detect recent form changes |

### Tools Found

**BasketballAnalyzeR** (R package):
```r
install.packages("BasketballAnalyzeR")
```

Functions available:
- `shotchart()` — Visualize shooting
- `assistnet()` — Passing networks  
- `barline()` — Player comparison
- `radialprofile()` — Skill profiles
- `variability()` — Consistency metrics

**Python equivalent**: Would need to build, but concepts transfer directly

---

## Book 10: The Signal and the Noise – Nate Silver (2012)

### Background
Silver = FiveThirtyEight founder, famous for election + sports predictions. PECOTA baseball system creator. This book is about prediction ITSELF — why most forecasts fail and what the good ones do right.

### Core Thesis
> "The signal is the truth. The noise is what distracts us from the truth."

Most predictions fail because we mistake noise for signal. Humility + Bayesian thinking = better forecasts.

### Key Concepts

#### 1. The Prediction Paradox

More data ≠ better predictions automatically
```
Data growth: Exponential
Useful signal growth: Linear (at best)
Noise growth: Exponential
```

**Implication**: More stats can make models WORSE if you overfit

#### 2. Foxes vs. Hedgehogs (Isaiah Berlin Framework)

| Type | Approach | Prediction Quality |
|------|----------|-------------------|
| **Hedgehog** | One big idea, high confidence | Poor |
| **Fox** | Many small ideas, uncertainty | Better |

Silver's finding: Experts with "one big theory" are LESS accurate than generalists who aggregate.

**Betting lesson**: Don't marry one model. Ensemble approaches win.

#### 3. Overfitting: The Cardinal Sin

```
In-sample fit ≠ Out-of-sample accuracy
```

Signs of overfitting:
- Too many variables
- Perfect historical fit
- Fails on new data
- Complex interactions without theory

**Rule of thumb**: Need 10-20x more data points than parameters

#### 4. Bayesian Thinking (Silver's Core Method)

```
Prior belief + New evidence → Updated belief

P(A|B) = P(B|A) × P(A) / P(B)
```

In practice:
1. Start with base rate (prior)
2. Observe new information
3. Update probability modestly
4. Don't overreact to single data points

**Betting example**:
- Prior: Team is 52% to cover
- New info: Star is questionable
- Update: Maybe 48% now
- NOT: "They're definitely losing!"

#### 5. Calibration > Accuracy

Good forecasters are **calibrated**:
- Events they say are 70% likely happen ~70% of the time
- Events they say are 30% likely happen ~30% of the time

Most people are **overconfident**:
- Their "90% confident" predictions happen 70% of the time

**How to improve**: Track prediction probabilities, not just W/L

#### 6. The Weather Forecasting Model

Silver holds up weather prediction as success story:
- Embraced uncertainty (probability, not certainty)
- Massive data + physical models
- Continuous improvement over decades
- Honest about limits (beyond 10 days = useless)

**Lesson**: State confidence intervals, not point estimates

#### 7. The 2008 Financial Crisis Lesson

Why models failed:
- Assumed past = future (no structural breaks)
- Ignored tail risks
- Correlated risks treated as independent
- Overconfidence in VaR models

**Betting parallel**: Don't assume market conditions stay constant. Edges disappear.

#### 8. Sports Betting Section (Yes, He Covers This!)

Silver's sports betting insights:
1. **Markets are efficient** — Hard to beat closing lines
2. **Look for structural edges** — Information asymmetries
3. **The vig kills you** — Need 52.4%+ just to break even
4. **Consensus is usually right** — Contrarian for the sake of it fails
5. **Injury news moves fast** — Be early or don't bother

#### 9. The Importance of Process Over Outcome

```
Good process + bad luck = bad outcome (short term)
Good process + long run = good outcome
```

**Key**: Judge decisions by quality, not results
- A +EV bet that loses was still correct
- A -EV bet that wins was still wrong

**Track**: Edge at time of bet, not just W/L

#### 10. Embracing Uncertainty

The best forecasters:
- Express predictions as probabilities
- Acknowledge what they don't know
- Update frequently with new information
- Maintain intellectual humility

The worst forecasters:
- Make bold, certain predictions
- Never admit error
- Ignore disconfirming evidence
- Confuse confidence with accuracy

---

### Model V3 Implications

| Silver Principle | V3 Implementation |
|------------------|-------------------|
| Signal vs noise | Fewer variables, more robust |
| Overfitting risk | Out-of-sample validation mandatory |
| Bayesian updating | Small adjustments, not overreactions |
| Calibration tracking | Log probability estimates, check calibration |
| Process over outcome | Track EV at bet time, not just result |
| Uncertainty intervals | Report confidence ranges, not just picks |
| Ensemble > single model | Consider blending multiple models |

### Calibration Tracking Template

```python
# Track for every pick
pick_log = {
    'game': 'NYK @ BOS',
    'pick': 'NYK +3.5',
    'confidence': 0.58,  # Our probability estimate
    'edge': 2.3,         # Points of perceived edge
    'closing_line': 3.0, # What it closed at (CLV)
    'result': 'W',       # Actual outcome
    'ev_at_bet': +0.04   # Expected value when placed
}

# Later: Check calibration
# Are our 58% picks winning ~58% of the time?
```

### Silver's Humility Test

Ask yourself:
1. "How would I know if I was wrong?"
2. "What's my track record, honestly?"
3. "Am I updating when evidence contradicts me?"
4. "Would I bet my own money at these odds?"

---

## Book 11: Statistical Sports Models in Excel (Vol. 1 & 2) – Andrew Mack (2017-2018)

### Background
Mack = Practical modeler, focuses on BUILDING not theory. These books are step-by-step guides to creating working betting models in Excel. No fluff — just formulas and methodology.

### Core Value
> "Anyone can build a working sports model. Here's exactly how."

Excel-based but concepts translate to any language. Perfect for understanding the mechanics.

### Volume 1: Fundamentals

#### 1. Power Ratings (Foundation of Everything)

The core concept:
```
Power Rating = Team Strength on neutral court
Predicted Margin = Home PR - Away PR + HCA
```

Building power ratings:
```excel
=SUMPRODUCT(Results, Adjustments) / Games
```

Iterative approach:
1. Start with simple win%
2. Adjust for strength of schedule
3. Adjust for margin of victory
4. Adjust for home/away
5. Iterate until stable

#### 2. Margin-Based Ratings (MOV)

```
Adjusted MOV = Actual MOV - Expected MOV (based on opponent)
```

| Metric | Formula |
|--------|---------|
| Simple MOV | (PF - PA) / Games |
| SOS-Adjusted | MOV - Avg Opponent Rating |
| Capped MOV | min(max(MOV, -20), 20) |

**Why cap?** Blowouts add noise, not signal. Cap at 15-20 points.

#### 3. The Least Squares Method

Solving for ratings using regression:
```
Minimize: Σ(Actual Margin - Predicted Margin)²
```

Excel Solver setup:
- Variables: Team ratings (30 cells)
- Objective: Minimize sum of squared errors
- Constraint: Average rating = 0 (centering)

#### 4. Pythagorean Projection

Excel implementation:
```excel
=PF^14 / (PF^14 + PA^14)
```

Use to find:
- Teams due for regression (actual W% >> expected)
- Undervalued teams (actual W% << expected)

#### 5. Basic Spread Prediction

```excel
=Home_Rating - Away_Rating + HCA
```

Where HCA ≈ 3 for NBA (adjust by era)

Then compare to market:
```excel
=Model_Spread - Market_Spread  // Edge
```

### Volume 2: Advanced Techniques

#### 6. Poisson Distribution for Totals

Modeling scoring as Poisson process:
```excel
=POISSON(points, lambda, FALSE)  // Probability of exactly X points
```

For game totals:
```
Expected Total = Home Expected + Away Expected
P(Over) = Σ P(combined > line)
```

#### 7. Monte Carlo Simulation

Run 10,000 game simulations:
```excel
=NORM.INV(RAND(), predicted_margin, std_dev)
```

Outputs:
- Win probability
- Cover probability  
- Distribution of outcomes
- Confidence intervals

**Key insight**: Captures variance, not just point estimate

#### 8. Recency Weighting (EWMA)

Recent games matter more:
```excel
=SUMPRODUCT(Results, Weights) / SUM(Weights)

Where Weights = λ^(games_ago)
λ = 0.9 typical (10% decay per game)
```

| Lambda | Half-life |
|--------|-----------|
| 0.95 | ~14 games |
| 0.90 | ~7 games |
| 0.85 | ~4 games |

#### 9. Home/Away Splits

Not all teams have equal HCA:
```excel
Home_Rating = (Home_MOV + SOS_Adj_Home) - League_Avg_Home_MOV
Away_Rating = (Away_MOV + SOS_Adj_Away) - League_Avg_Away_MOV
```

Some teams are road warriors; some are home-only

#### 10. Rest & Schedule Adjustments

Excel lookup for rest:
```excel
=VLOOKUP(Days_Rest, Rest_Table, 2, FALSE)
```

| Days Rest | Adjustment |
|-----------|------------|
| 0 (B2B) | -3.0 |
| 1 | 0.0 |
| 2 | +0.5 |
| 3+ | +1.0 |

#### 11. Combining Models (Ensemble)

Blend multiple approaches:
```excel
=0.4*Power_Rating + 0.3*MOV_Rating + 0.2*Recent_Form + 0.1*Pythag
```

Weights determined by:
- Historical accuracy
- Or use regression to optimize

#### 12. Tracking & Evaluation

Build a tracking sheet:
```
Date | Game | Pick | Line | Close | Result | CLV | Profit
```

Key metrics to calculate:
- ROI = Profit / Amount Wagered
- CLV = Avg(My Line - Closing Line)
- Calibration = Actual W% vs Predicted W%

---

### Model V3 Implementation

| Mack Technique | V3 Status/Action |
|----------------|------------------|
| Power ratings | Using ORtg/DRtg (similar concept) ✅ |
| Margin capping | Add cap at ±15 for blowouts |
| Least squares | Could add as alternative to simple diff |
| Pythagorean | Add for regression detection |
| EWMA for recency | Implement λ=0.9 weighting |
| Monte Carlo | Add for probability distributions |
| Rest adjustments | Already included ✅ |
| Ensemble blend | Consider multi-model approach |
| Tracking sheet | Build comprehensive log |

### Excel → Python Translation

```python
# Power rating iteration (Mack's method)
def iterate_ratings(games, ratings, iterations=100):
    for _ in range(iterations):
        for team in teams:
            adj_mov = []
            for game in team_games[team]:
                opp = game.opponent
                expected = ratings[team] - ratings[opp] + hca(game)
                error = game.margin - expected
                adj_mov.append(error)
            ratings[team] += np.mean(adj_mov) * 0.5  # damping
    return ratings

# Monte Carlo simulation
def simulate_game(home_rating, away_rating, hca=3, std=12, n=10000):
    margins = np.random.normal(home_rating - away_rating + hca, std, n)
    return {
        'win_prob': np.mean(margins > 0),
        'cover_prob': lambda line: np.mean(margins > -line),
        'mean_margin': np.mean(margins),
        'std': np.std(margins)
    }
```

---

## Book 12: Bayesian Sports Models in R – Andrew Mack (2019)

### Background
Mack's advanced follow-up. Moves from Excel to R, from frequentist to Bayesian. More sophisticated but same practical spirit.

### Core Philosophy
> "Bayesian models let you incorporate what you KNOW before looking at data."

Frequentist: "What does the data say?"
Bayesian: "What does the data say, given what I already knew?"

### Why Bayesian for Sports?

| Problem | Frequentist | Bayesian |
|---------|-------------|----------|
| Small samples | Unreliable | Regularized by prior |
| Early season | Garbage | Shrink to prior (last season) |
| Rare events | Can't estimate | Prior helps |
| Uncertainty | Point estimate | Full distribution |

**Key insight**: Season starts with 0 games. Bayesian lets you use last year's data as prior.

### Key Concepts

#### 1. Priors, Likelihood, Posteriors

```
Posterior ∝ Likelihood × Prior

P(θ|data) ∝ P(data|θ) × P(θ)
```

In sports terms:
- **Prior**: What we believed before (last season's rating)
- **Likelihood**: What the new games tell us
- **Posterior**: Updated belief (blend of both)

#### 2. Shrinkage (Regularization)

Early season problem:
- Team A: 3-0, +15 MOV
- Team B: 0-3, -15 MOV

Frequentist: Team A is +15, Team B is -15
Bayesian: Both shrink toward league average

```r
posterior_rating = weight * observed + (1-weight) * prior
# Early season: weight ≈ 0.2 (shrink heavily)
# Late season: weight ≈ 0.8 (trust data more)
```

#### 3. Hierarchical Models

Model structure:
```
League → Team → Game
```

Each level informs the others:
- Teams shrink toward league average
- Games inform team rating
- Similar teams share information

```r
# Stan/brms syntax
team_rating ~ normal(league_mean, league_sd)
game_margin ~ normal(home_rating - away_rating + hca, game_sd)
```

#### 4. Time-Varying Ratings (State Space)

Ratings change over time:
```
Rating[t] = Rating[t-1] + drift + noise
```

Kalman filter approach:
- Track rating AND uncertainty
- Uncertainty grows between observations
- Uncertainty shrinks after each game

**Benefit**: Captures team improvement/decline during season

#### 5. MCMC Sampling (The Engine)

How Bayesian models work:
```r
# Using Stan
stan_model <- stan(model_code = model, data = data, iter = 4000)
posterior_samples <- extract(stan_model)
```

Output: 1000s of samples from posterior distribution
- Mean = point estimate
- SD = uncertainty
- Quantiles = credible intervals

#### 6. Bradley-Terry Model (Game Outcomes)

Model win probability:
```
P(Home wins) = logit^-1(home_rating - away_rating + hca)
```

Bayesian extension:
```r
home_wins ~ bernoulli(inv_logit(home_strength - away_strength + hca))
home_strength ~ normal(0, prior_sd)
```

#### 7. Poisson Regression for Scoring

Model points as Poisson:
```r
home_points ~ poisson(exp(home_off - away_def + hca))
away_points ~ poisson(exp(away_off - home_def))
```

Benefits:
- Natural for count data
- Can model O/U directly
- Handles correlation between scoring

#### 8. Credible Intervals (Better than Confidence)

Bayesian output:
```
Rating = 5.2, 95% CI [3.1, 7.4]
```

Interpretation: "95% probability rating is between 3.1 and 7.4"
(Frequentist CI doesn't mean this!)

**Betting use**: Bet only when CI doesn't overlap market line

#### 9. Model Comparison (LOO-CV)

Compare models using Leave-One-Out Cross-Validation:
```r
loo_compare(model1_loo, model2_loo)
```

Pick model with best out-of-sample prediction, not best fit.

#### 10. Posterior Predictive Checks

Does your model make sense?
```r
# Simulate from posterior
y_rep <- posterior_predict(model, draws = 500)

# Compare to actual data
ppc_dens_overlay(y, y_rep)  # Distributions should match
```

If simulated games look nothing like real games, model is broken.

---

### Implementation in R

```r
# Simple Bayesian team ratings with brms
library(brms)

model <- brm(
  margin ~ 0 + home_team + away_team + (1|game_id),
  data = games,
  prior = c(
    prior(normal(0, 5), class = "b")  # Shrink toward 0
  ),
  iter = 4000, chains = 4
)

# Extract team ratings
posterior_summary(model)
```

### Python Equivalent (PyMC)

```python
import pymc as pm

with pm.Model() as nba_model:
    # Priors
    team_ratings = pm.Normal('ratings', mu=0, sigma=5, shape=30)
    hca = pm.Normal('hca', mu=3, sigma=1)
    sigma = pm.HalfNormal('sigma', sigma=10)
    
    # Likelihood
    home_idx = games['home_team_idx']
    away_idx = games['away_team_idx']
    mu = team_ratings[home_idx] - team_ratings[away_idx] + hca
    margin = pm.Normal('margin', mu=mu, sigma=sigma, observed=games['margin'])
    
    # Sample
    trace = pm.sample(2000, return_inferencedata=True)
```

---

### Model V3 Implications

| Bayesian Concept | V3 Implementation |
|------------------|-------------------|
| Priors from last season | Initialize ratings with prior year |
| Shrinkage early season | Trust model less in Oct-Nov |
| Uncertainty quantification | Output confidence intervals |
| Time-varying ratings | Consider Kalman filter for in-season drift |
| Posterior predictive | Validate model generates realistic games |
| Hierarchical structure | Share info across similar teams |

### When to Go Bayesian

✅ **Do use Bayesian when:**
- Small sample size (early season)
- Want uncertainty estimates
- Have good prior information
- Need regularization

❌ **Maybe skip when:**
- Huge dataset (less benefit)
- Speed critical (MCMC is slow)
- Simple model sufficient

### Practical Takeaway

Start simple:
```python
# Quick Bayesian shrinkage
def bayesian_rating(observed_mov, games_played, prior_mov=0, prior_weight=10):
    """
    Shrink toward prior, weight by sample size
    """
    weight = games_played / (games_played + prior_weight)
    return weight * observed_mov + (1 - weight) * prior_mov
```

This captures 80% of the benefit without full MCMC.

---

## Book 13: Sports Analytics and Data Science — Thomas W. Miller (2015)

### Background
Miller = Northwestern professor, data science practitioner. This is a comprehensive textbook covering the full analytics pipeline from data to decisions. Uses R/Python with real examples.

### Core Framework
> "Analytics is not about data. It's about decisions."

The full pipeline:
```
Data → Preparation → Analysis → Modeling → Validation → Decision
```

### Key Concepts

#### 1. The Sports Analytics Hierarchy

| Level | Question | Method |
|-------|----------|--------|
| Descriptive | What happened? | Summary stats |
| Diagnostic | Why did it happen? | Correlations, breakdowns |
| Predictive | What will happen? | Models, forecasting |
| Prescriptive | What should we do? | Optimization |

**Betting focus**: Predictive + a bit of prescriptive (bet sizing)

#### 2. Data Quality Principles

Before modeling, check:
```
Completeness — Missing values?
Accuracy — Data entry errors?
Consistency — Same definitions over time?
Timeliness — How fresh?
Relevance — Does it matter for prediction?
```

**Common sports data issues**:
- Different stat definitions across sources
- Missing play-by-play for older games
- Injury reports incomplete/delayed

#### 3. Feature Engineering for Sports

Transform raw stats into predictive features:
```python
# Raw: Points scored
# Engineered: 
points_per_100 = points / possessions * 100
points_vs_expected = actual - opponent_avg_allowed
rolling_10_game_avg = df.rolling(10).mean()
home_away_split = home_pts - away_pts
```

**Key insight**: Engineered features often outperform raw stats

#### 4. The Train/Test Split Religion

Never evaluate on training data:
```python
train = seasons[2020:2024]
test = season[2025]

model.fit(train)
predictions = model.predict(test)
evaluate(predictions, test_actuals)  # This is truth
```

**Time series note**: Always split by TIME, not random. Future data can't leak into training.

#### 5. Model Selection Framework

Compare models systematically:
| Metric | Use When |
|--------|----------|
| RMSE | Care about margin accuracy |
| MAE | Robust to outliers |
| AUC | Binary outcomes (W/L) |
| Log Loss | Probability calibration |
| Accuracy | Simple W/L |
| CLV | Betting (our key metric) |

**For betting**: CLV + ROI > raw prediction accuracy

#### 6. Regression Models for Spreads

Linear regression baseline:
```python
spread_prediction = β₀ + β₁(home_rating) + β₂(away_rating) + β₃(rest_diff) + ...
```

Key diagnostics:
- R² (variance explained)
- Residual plots (patterns = problems)
- VIF (multicollinearity check)

**Typical sports R²**: 0.15-0.30 (low by ML standards, but useful)

#### 7. Classification for Game Outcomes

Logistic regression for W/L or cover:
```python
P(cover) = logit⁻¹(β₀ + β₁X₁ + β₂X₂ + ...)
```

Random forests often beat logistic:
```python
from sklearn.ensemble import RandomForestClassifier
rf = RandomForestClassifier(n_estimators=100, max_depth=5)
```

**Caution**: Complex models overfit. Regularize or keep simple.

#### 8. Time Series Components

Sports data has structure:
```
Y[t] = Trend + Seasonality + Noise

Trend: Team improving/declining over season
Seasonality: Start of season rust, late season rest
Noise: Game-to-game variance
```

Capture with:
- Rolling averages (trend)
- Month dummies (seasonality)
- Autoregressive terms (momentum)

#### 9. Simulation for Decision-Making

Monte Carlo for bet sizing:
```python
def simulate_season(picks, edge_per_pick, n_sims=10000):
    results = []
    for _ in range(n_sims):
        season_profit = 0
        for pick in picks:
            outcome = np.random.binomial(1, pick.win_prob)
            season_profit += outcome * pick.payout - (1-outcome) * pick.stake
        results.append(season_profit)
    return {
        'mean': np.mean(results),
        'std': np.std(results),
        'p_profitable': np.mean(np.array(results) > 0),
        'var_5': np.percentile(results, 5)  # Value at Risk
    }
```

#### 10. Optimization for Bet Allocation

Kelly Criterion as optimization:
```
Maximize: E[log(wealth)]
Subject to: Sum of bets ≤ bankroll
```

Fractional Kelly in practice:
```python
def kelly_fraction(prob, odds, fraction=0.25):
    b = odds - 1  # Decimal odds minus 1
    q = 1 - prob
    kelly = (prob * b - q) / b
    return max(0, kelly * fraction)  # Never negative, use fraction
```

#### 11. Cross-Validation for Sports

Standard k-fold doesn't work (time leakage):
```python
# Wrong
kfold = KFold(n_splits=5, shuffle=True)  # Future leaks!

# Right: Time series CV
from sklearn.model_selection import TimeSeriesSplit
tscv = TimeSeriesSplit(n_splits=5)
```

Each fold: Train on past, test on future.

#### 12. Ensemble Methods

Combine multiple models:
```python
predictions = {
    'linear': linear_model.predict(X),
    'rf': rf_model.predict(X),
    'xgb': xgb_model.predict(X)
}

# Simple average
ensemble = np.mean([predictions[m] for m in predictions], axis=0)

# Weighted by past performance
weights = [0.3, 0.4, 0.3]  # From validation
ensemble = np.average([predictions[m] for m in predictions], weights=weights, axis=0)
```

**Finding**: Simple ensembles often beat complex single models.

---

### Miller's Analytics Workflow

```
1. Define Question
   └── What are we predicting? (spread, total, W/L)

2. Gather Data
   └── Multiple sources, clean thoroughly

3. Engineer Features
   └── Transform raw → predictive

4. Split Train/Test
   └── By TIME, not random

5. Train Models
   └── Start simple, add complexity if needed

6. Validate
   └── Out-of-sample performance only

7. Ensemble
   └── Blend top models

8. Deploy & Monitor
   └── Track live performance, update regularly
```

---

### Model V3 Implications

| Miller Concept | V3 Action |
|----------------|-----------|
| Feature engineering | Create more derived features |
| Time-based CV | Validate on holdout season |
| R² expectations | Don't chase high R² (0.2 is fine) |
| Ensemble approach | Blend multiple model types |
| Simulation for sizing | Use Monte Carlo for bankroll |
| CLV as key metric | Already tracking ✅ |
| Regular revalidation | Rebuild model monthly |

### Quick Wins from Miller

```python
# 1. Rolling features
df['margin_last_10'] = df.groupby('team')['margin'].transform(
    lambda x: x.rolling(10).mean()
)

# 2. Opponent-adjusted
df['margin_vs_avg'] = df['margin'] - df['opp_avg_allowed']

# 3. Home/away splits
df['home_edge'] = df['home_margin'] - df['away_margin']

# 4. Time-series CV
from sklearn.model_selection import TimeSeriesSplit
for train_idx, test_idx in TimeSeriesSplit(5).split(df):
    # train on past, test on future
    pass
```

---

## Book 14: Analyzing Baseball Data with R — Ryan Elmore & Andrew Urbaczewski (2015)

*(Note: Title may vary — Elmore/Urbaczewski are known for baseball-focused R analytics. Concepts transfer to basketball.)*

### Background
Denver-based professors focusing on practical R implementation for sports. Heavy on data manipulation, visualization, and reproducible analysis.

### Core Value
> "Reproducible analysis = trustworthy analysis."

Every step documented in code. No black boxes.

### Key Techniques (Transferable to NBA)

#### 1. Tidyverse Data Pipeline

The modern R workflow:
```r
library(tidyverse)

games %>%
  filter(season == 2025) %>%
  group_by(team) %>%
  summarize(
    avg_margin = mean(margin),
    games = n(),
    win_pct = mean(win)
  ) %>%
  arrange(desc(avg_margin))
```

**Python equivalent** (pandas):
```python
(games
 .query('season == 2025')
 .groupby('team')
 .agg(avg_margin=('margin', 'mean'),
      games=('margin', 'count'),
      win_pct=('win', 'mean'))
 .sort_values('avg_margin', ascending=False))
```

#### 2. Web Scraping for Sports Data

Getting data from Basketball-Reference:
```r
library(rvest)

url <- "https://www.basketball-reference.com/leagues/NBA_2025.html"
page <- read_html(url)
tables <- page %>% html_table()
standings <- tables[[1]]
```

**Key sources**:
- Basketball-Reference (historical)
- NBA.com/stats (current + tracking)
- ESPN API (schedules, scores)

#### 3. Join Operations for Context

Combine game data with context:
```r
games %>%
  left_join(team_ratings, by = "team") %>%
  left_join(rest_data, by = c("team", "date")) %>%
  left_join(injuries, by = c("team", "date"))
```

**Insight**: Rich context = better predictions. Single-source models are limited.

#### 4. Rolling Calculations

Compute trailing stats properly:
```r
games %>%
  arrange(team, date) %>%
  group_by(team) %>%
  mutate(
    margin_L5 = zoo::rollmean(margin, 5, fill = NA, align = "right"),
    margin_L10 = zoo::rollmean(margin, 10, fill = NA, align = "right")
  )
```

**Critical**: Use `align = "right"` to prevent future leakage.

#### 5. Visualization Best Practices

Shot charts with ggplot2:
```r
ggplot(shots, aes(x = x, y = y, color = made)) +
  geom_point(alpha = 0.5) +
  coord_fixed() +  # Keep court proportions
  theme_minimal()
```

Principles:
- Always label axes
- Use colorblind-friendly palettes
- Don't overcomplicate

#### 6. Hypothesis Testing for Edges

Is your edge real or noise?
```r
# Binomial test: 55% win rate on 100 bets
binom.test(55, 100, p = 0.524)  # 0.524 = break-even at -110

# Result: p-value = 0.15
# Not significant — could be luck
```

**Need 300+ bets at 55%** to be 95% confident you're skilled.

#### 7. Bootstrap for Uncertainty

When distributions are unknown:
```r
library(boot)

boot_fn <- function(data, idx) {
  mean(data$margin[idx])
}

results <- boot(games, boot_fn, R = 1000)
boot.ci(results, type = "perc")  # 95% CI
```

**Use**: Get confidence intervals for any metric.

#### 8. Linear Models with Diagnostics

Full regression workflow:
```r
model <- lm(margin ~ home_rating + away_rating + rest_diff + 
            b2b_home + b2b_away, data = train)

# Diagnostics
summary(model)        # Coefficients, R²
plot(model)           # Residual plots
vif(model)            # Multicollinearity
```

**Check for**:
- Non-linear patterns in residuals
- Outliers with high leverage
- VIF > 5 (multicollinearity problem)

#### 9. Model Comparison Framework

Compare candidate models:
```r
models <- list(
  simple = lm(margin ~ home_rtg - away_rtg, data),
  with_rest = lm(margin ~ home_rtg - away_rtg + rest_diff, data),
  full = lm(margin ~ home_rtg - away_rtg + rest_diff + b2b + travel, data)
)

# Compare AIC (lower = better, penalizes complexity)
sapply(models, AIC)

# Compare out-of-sample RMSE
sapply(models, function(m) sqrt(mean(residuals(m)^2)))
```

#### 10. Reproducibility with R Markdown

Document everything:
```r
---
title: "NBA Model V3 Analysis"
output: html_document
---

## Data
{r load-data}
games <- read_csv("data/games.csv")

## Model
{r model}
model <- lm(margin ~ ..., data = games)
summary(model)
```

**Benefits**:
- Shareable
- Auditable
- Prevents "I can't remember what I did"

---

### Data Pipeline Architecture

```
Raw Data Sources          Cleaned Data              Analysis
─────────────────        ────────────             ──────────
BBall-Ref ─────┐
               ├──→ games.csv ──→ features.csv ──→ model.R
NBA.com ───────┤
               ├──→ players.csv ──→ injuries.csv
ESPN ──────────┘
```

Automate with scripts:
```r
# daily_update.R
source("scripts/scrape_games.R")
source("scripts/update_ratings.R")
source("scripts/generate_picks.R")
```

---

### Model V3 Implications

| Elmore/Urbaczewski Technique | V3 Action |
|------------------------------|-----------|
| Tidyverse pipeline | Port to pandas equivalent |
| Web scraping | Automate BBall-Ref pulls |
| Rolling stats | Ensure right-aligned (no leakage) |
| Bootstrap CIs | Add uncertainty to predictions |
| Binomial testing | Validate edge is real (need 300+ bets) |
| R Markdown / Jupyter | Document all analysis steps |
| Diagnostic plots | Check residuals after model updates |

### Sample Size Requirements

To be 95% confident your edge is real:
| Win Rate | Bets Needed |
|----------|-------------|
| 53% | 1,000+ |
| 55% | 300+ |
| 57% | 150+ |
| 60% | 70+ |

**Reality check**: At 1 bet/day, 55% takes ~1 year to confirm.

---

## Book 15: Data Science and Predictive Analytics — Ivo D. Dinov (2018)

### Background
Dinov = UCLA professor, comprehensive DS textbook. NOT sports-specific but covers all the core methods. Academic rigor + practical examples.

### Core Philosophy
> "Prediction without understanding is dangerous. Understanding without prediction is useless."

Both matter. Know WHY your model works, not just THAT it works.

### Relevant Techniques for Sports Betting

#### 1. The Bias-Variance Tradeoff

The fundamental DS concept:
```
Total Error = Bias² + Variance + Irreducible Noise

High Bias: Model too simple, misses patterns (underfit)
High Variance: Model too complex, fits noise (overfit)
```

| Model Type | Bias | Variance |
|------------|------|----------|
| Linear regression | Higher | Lower |
| Random forest | Lower | Higher |
| Deep neural net | Lowest | Highest |

**Sweet spot for sports**: Slightly higher bias (simpler models) because:
- Data is noisy
- Sample sizes limited
- Patterns change over time

#### 2. Regularization Methods

Prevent overfitting:
```python
# Ridge (L2) - shrinks coefficients
from sklearn.linear_model import Ridge
model = Ridge(alpha=1.0)

# Lasso (L1) - zeros out weak features
from sklearn.linear_model import Lasso
model = Lasso(alpha=0.1)

# ElasticNet - both
from sklearn.linear_model import ElasticNet
model = ElasticNet(alpha=0.1, l1_ratio=0.5)
```

**For sports**: Ridge usually better (don't want to zero features entirely)

#### 3. Cross-Validation Deep Dive

Types and when to use:
| CV Type | Use When |
|---------|----------|
| K-Fold | i.i.d. data (not time series) |
| Time Series Split | Sequential data ✓ |
| Leave-One-Out | Very small samples |
| Nested CV | Tuning + evaluation |

**Sports requirement**: Always time-based CV
```python
from sklearn.model_selection import TimeSeriesSplit
tscv = TimeSeriesSplit(n_splits=5, gap=0)  # gap prevents leakage
```

#### 4. Probability Calibration

Your model outputs 60% confidence. Does that mean 60%?
```python
from sklearn.calibration import calibration_curve

prob_true, prob_pred = calibration_curve(y_true, y_prob, n_bins=10)
# Plot: Should be diagonal line
```

Calibration methods:
- **Platt scaling**: Logistic regression on outputs
- **Isotonic regression**: Non-parametric
- **Temperature scaling**: Simple divisor

**For betting**: Calibrated probabilities → correct Kelly sizing

#### 5. Feature Selection Methods

Too many features = overfit. Reduce:
```python
# Filter: Correlation with target
correlations = X.corrwith(y).abs().sort_values(ascending=False)
top_features = correlations.head(10).index

# Wrapper: Recursive elimination
from sklearn.feature_selection import RFE
rfe = RFE(estimator=model, n_features_to_select=10)

# Embedded: Lasso coefficients
lasso = Lasso(alpha=0.1).fit(X, y)
important = np.where(lasso.coef_ != 0)[0]
```

**Rule of thumb**: 10-20 observations per feature minimum

#### 6. Dimensionality Reduction

When features are correlated:
```python
from sklearn.decomposition import PCA

pca = PCA(n_components=5)
X_reduced = pca.fit_transform(X)
print(pca.explained_variance_ratio_)  # How much info retained
```

**Use for**: Player clustering, team style profiles

#### 7. Classification Metrics Deep Dive

Beyond accuracy:
| Metric | Formula | Use When |
|--------|---------|----------|
| Accuracy | (TP+TN)/Total | Balanced classes |
| Precision | TP/(TP+FP) | False positives costly |
| Recall | TP/(TP+FN) | False negatives costly |
| F1 | 2×(P×R)/(P+R) | Balance P and R |
| AUC-ROC | Area under curve | Ranking quality |
| Log Loss | -Σ(y×log(p)) | Probability quality |

**For betting**: Log loss (probability calibration matters most)

#### 8. Ensemble Methods Taxonomy

| Type | Method | Combines |
|------|--------|----------|
| Bagging | Random Forest | Parallel models, average |
| Boosting | XGBoost, LightGBM | Sequential, fix errors |
| Stacking | Meta-learner | Model predictions as features |
| Blending | Simple average | Weighted combination |

```python
# Stacking example
from sklearn.ensemble import StackingRegressor

estimators = [
    ('ridge', Ridge()),
    ('rf', RandomForestRegressor())
]
stack = StackingRegressor(estimators=estimators, 
                          final_estimator=LinearRegression())
```

#### 9. Handling Imbalanced Data

Betting context: Most games don't have huge edges (imbalanced)
```python
# Oversample minority (strong edges)
from imblearn.over_sampling import SMOTE
X_res, y_res = SMOTE().fit_resample(X, y)

# Or: Adjust class weights
model = LogisticRegression(class_weight='balanced')

# Or: Adjust threshold
# Default: predict 1 if P > 0.5
# Adjusted: predict 1 if P > 0.4 (more sensitive)
```

#### 10. Model Interpretability

Understand what your model learned:
```python
# Feature importance (tree models)
importances = model.feature_importances_
sorted_idx = np.argsort(importances)[::-1]

# SHAP values (any model)
import shap
explainer = shap.Explainer(model, X)
shap_values = explainer(X)
shap.summary_plot(shap_values, X)
```

**Critical for betting**: If model relies on spurious feature, edge won't persist

#### 11. Dealing with Missing Data

Sports data often incomplete:
```python
# Simple: Drop
df.dropna()

# Better: Impute
from sklearn.impute import SimpleImputer
imputer = SimpleImputer(strategy='median')
X_imputed = imputer.fit_transform(X)

# Best: Model-based imputation
from sklearn.impute import IterativeImputer
imputer = IterativeImputer()
X_imputed = imputer.fit_transform(X)
```

**For injuries**: Missing = not reported = probably healthy (domain knowledge)

#### 12. Production Deployment

Getting model into production:
```python
# Save model
import joblib
joblib.dump(model, 'nba_model_v3.pkl')

# Load and predict
model = joblib.load('nba_model_v3.pkl')
predictions = model.predict(new_data)

# Monitor for drift
if new_rmse > 1.2 * training_rmse:
    alert("Model degradation detected!")
```

---

### The DS Workflow (Dinov's Framework)

```
1. Problem Definition
   └── What decision does this inform?

2. Data Collection
   └── What data is available and relevant?

3. Data Cleaning
   └── Handle missing, outliers, errors

4. Exploratory Analysis
   └── Understand distributions, relationships

5. Feature Engineering
   └── Create predictive inputs

6. Model Selection
   └── Choose appropriate algorithms

7. Training & Tuning
   └── Fit and optimize hyperparameters

8. Validation
   └── Out-of-sample testing

9. Interpretation
   └── Understand what model learned

10. Deployment
    └── Put into production

11. Monitoring
    └── Track performance, retrain as needed
```

---

### Model V3 Implications

| Dinov Concept | V3 Action |
|---------------|-----------|
| Bias-variance | Prefer simpler models, regularize |
| Ridge regression | Add L2 regularization to ratings |
| Probability calibration | Check if 60% picks win 60% |
| Feature selection | Limit to 10-15 key features |
| Log loss metric | Track for probability quality |
| SHAP interpretability | Understand what drives predictions |
| Model monitoring | Alert if RMSE degrades |

### Key Formulas

```python
# Bias-Variance decomposition (conceptual)
expected_error = bias**2 + variance + noise

# Regularization strength selection
alphas = [0.01, 0.1, 1.0, 10.0]
cv_scores = [cross_val_score(Ridge(alpha=a), X, y).mean() for a in alphas]
best_alpha = alphas[np.argmax(cv_scores)]

# Calibration check
from sklearn.calibration import calibration_curve
fraction_positive, mean_predicted = calibration_curve(y_true, y_prob, n_bins=10)
calibration_error = np.mean(np.abs(fraction_positive - mean_predicted))
```

---

## Book 16: Calculated Bets — Steven Skiena (2001)

### Background
Skiena = Stony Brook CS professor who ACTUALLY built and ran a profitable Jai Alai betting system. This isn't theory — he made real money and documented everything. One of the few honest accounts of building a winning system.

### Core Value
> "This is what it actually takes to beat the market with math."

Real experience: the wins, the losses, the grind, the edge decay.

### Key Lessons

#### 1. The Importance of a Weak Market

Skiena chose Jai Alai specifically because:
- Low liquidity (less sharp money)
- Simple game structure (modelable)
- Pari-mutuel (bet against public, not bookmaker)
- Inefficient odds (public has biases)

**Lesson**: Don't fight efficient markets. Find weak ones.

| Market | Efficiency | Beatable? |
|--------|------------|-----------|
| NFL sides | Very high | Hard |
| NBA sides | High | Hard |
| NBA props | Moderate | Maybe |
| Jai Alai | Low | Yes (in 1990s) |
| Niche sports | Low | Possibly |

#### 2. Monte Carlo Simulation (Core Method)

Skiena's approach:
```python
def simulate_match(player_ratings, n_sims=10000):
    outcomes = []
    for _ in range(n_sims):
        # Simulate each point/game based on ratings
        result = run_single_simulation(player_ratings)
        outcomes.append(result)
    
    # Calculate win/place/show probabilities
    probs = calculate_probabilities(outcomes)
    return probs
```

**Key insight**: Simulation handles complex scenarios better than closed-form math.

#### 3. Finding Overlays

Compare your probabilities to market odds:
```
Your estimate: Player A wins 25%
Market odds: 5-1 (16.7% implied)
Overlay: 25% - 16.7% = 8.3% edge

Kelly bet: edge / odds = 8.3% / 5 = 1.66% of bankroll
```

**Only bet when overlay exceeds vig + uncertainty margin**

#### 4. The Reality of Edge Sizes

Skiena's actual edges:
- Average edge per bet: ~5-10%
- Win rate: ~55-60% on +EV bets
- ROI: ~10-15% over years

**Not glamorous**: Small edges, many bets, slow grind.

#### 5. Data Collection is 80% of the Work

Skiena spent more time on data than modeling:
```
Year 1: Collect historical results manually
Year 2: Build database, clean data
Year 3: Actually model and bet
```

**For us**: Data pipeline (BBall-Ref, ESPN, injuries) is critical infrastructure.

#### 6. Model Iteration and Failure

Skiena's journey:
1. First model: Too simple, didn't work
2. Second model: Overfit, failed out-of-sample
3. Third model: Finally profitable
4. Ongoing: Continuous tweaks

**Lesson**: Expect first attempts to fail. Keep iterating.

#### 7. Bankroll Survival

Skiena's rules:
- Never bet more than 2% per wager
- Stop if down 50% (reassess)
- Separate betting bankroll from life money
- Track everything obsessively

```python
def bet_size(edge, odds, bankroll, kelly_fraction=0.25):
    full_kelly = edge / odds
    return bankroll * full_kelly * kelly_fraction
```

#### 8. Edge Decay

Skiena observed his edge shrinking over time:
- Market got more efficient
- Others found similar strategies
- Rules changed

**Lesson**: Edges are temporary. Always be looking for the next one.

#### 9. The Psychology of Betting

Skiena's honest account:
- Losing streaks hurt even when +EV
- Temptation to increase bets after losses
- Overconfidence after wins
- The grind wears you down

**Counter**: Pre-commit to stake sizes, automate where possible.

#### 10. When to Quit

Skiena eventually stopped because:
- Edge eroded below vig
- Time investment not worth diminished returns
- Jai Alai declining as sport

**Lesson**: Have an exit criteria. Don't grind a dead edge.

---

### Skiena's Practical Framework

```
1. Find an inefficient market
   └── Where is the "dumb money"?

2. Collect extensive data
   └── More than you think you need

3. Build simulation model
   └── Monte Carlo > closed-form

4. Validate out-of-sample
   └── Paper trade before real money

5. Start small
   └── Fractional Kelly, tiny stakes

6. Track relentlessly
   └── Every bet, every outcome

7. Iterate continuously
   └── Model is never "done"

8. Monitor edge decay
   └── Be ready to pivot or quit
```

---

### Model V3 Implications

| Skiena Lesson | V3 Action |
|---------------|-----------|
| Weak markets | Focus on props (less efficient) |
| Monte Carlo | Add simulation for probability distributions |
| Data obsession | Strengthen data pipeline |
| Small edges | Expect 3-5% edges, not 10%+ |
| Iteration | Plan for model v4, v5, v6... |
| Edge decay | Monitor CLV over time for degradation |
| Psychology | Pre-set bet sizes, minimize decisions |

### Realistic Expectations (from Skiena)

| Metric | Reality |
|--------|---------|
| Edge per bet | 3-8% |
| Win rate | 53-58% |
| ROI | 5-15% annually |
| Time to confirm skill | 500+ bets |
| Model iterations | 3-5 before profitable |
| Lifespan of edge | 1-5 years |

### The Honest Truth

Skiena's takeaway after years of profitable betting:
> "It was intellectually rewarding but not a path to riches. The hourly rate, accounting for all the work, was modest. I did it because it was interesting, not because it was lucrative."

**For us**: This is a learning exercise and side income, not retirement plan.

---

## Book 17: Sprawlball — Kirk Goldsberry (2019)

### Background
Goldsberry = ESPN analyst, Spurs consultant, invented modern shot charts. "Sprawlball" documents how the 3-pointer revolutionized basketball. Heavy on visualization + spatial analysis.

### Core Thesis
> "The 3-point line is the most important innovation in basketball history. Teams that adapted won. Teams that didn't died."

The NBA literally reshaped around one rule.

### Key Concepts

#### 1. The Shot Value Revolution

Goldsberry's core math:
```
Expected value by zone:
- Rim: 1.30 pts/shot (65% × 2)
- Corner 3: 1.20 pts/shot (40% × 3)
- Above-break 3: 1.11 pts/shot (37% × 3)
- Long 2: 0.80 pts/shot (40% × 2)
- Midrange: 0.84 pts/shot (42% × 2)
```

**The death of the midrange**:
| Era | Midrange % of shots |
|-----|---------------------|
| 2000 | 35%+ |
| 2010 | 25% |
| 2020 | 15% |
| 2025 | <10% |

#### 2. The Only Good Shots

Goldsberry's "3 good shots":
1. **At the rim** (layups, dunks)
2. **Corner 3** (shortest 3, highest %)
3. **Open 3** (any above-break if uncontested)

Everything else is suboptimal.

**Team evaluation**: Shot profile quality = % of shots from these 3 zones

#### 3. Shot Charts as Scouting

Goldsberry's visual innovation:
```
Hexbin charts showing:
- Shot frequency (hex size)
- Efficiency (hex color)
- League comparison (relative coloring)
```

**For betting**: Teams with "red" (efficient) shot profiles outperform stats

#### 4. The Spacing Revolution

Pre-3PT era: Pack the paint
Modern era: Stretch to the arc

```
Spacing effect:
5-out (5 shooters): Defense stretched, driving lanes open
4-out: Still good
3-out: Getting cramped
2-out or less: Offense dies
```

**Roster evaluation**: Count legitimate 3PT threats (>35% on volume)

#### 5. The Death of the Traditional Center

Old centers: Post up, shoot 8-footers
New centers: Either:
- Elite rim protector + finisher (Gobert)
- Stretch 5 who shoots 3s (Brook Lopez)
- Do everything (Jokić, Embiid)

**Non-shooting bigs are liabilities** (unless elite defender)

#### 6. Corner 3 Obsession

Why corners matter:
- Shorter distance (22 ft vs 23.75 ft)
- Higher percentage league-wide
- Often open (help defense collapses to paint)

```
Corner 3 rate = Corner 3 attempts / Total 3PA
Elite offenses: 20%+ from corners
```

#### 7. The Curry Effect

Before Steph: 3s were supplementary
After Steph: 3s are primary weapon

Steph's impact:
- Proved high-volume 3PA can be efficient
- Forced defenses to guard 30+ feet out
- Created "gravity" (defense warps to him)
- Other teams copied, league transformed

#### 8. Transition vs Half-Court

Goldsberry's findings:
```
Transition: ~1.12 pts/poss
Half-court: ~0.96 pts/poss
```

Pace matters because more possessions = more transition opportunities.

**Fast teams get 5-10 extra transition possessions/game = +5-10 points**

#### 9. The 3-Point Variance Problem

3-pointers are high-variance:
```
Game-to-game 3P% variance: ±10-15%
40% shooter can go 2-10 or 7-10 on any night
```

**Betting implication**: 
- 3PT-heavy teams = higher game variance
- UNDER/OVER swings more wildly
- Upsets more common

#### 10. The Analytics Arms Race

Goldsberry on team adoption:
- Early adopters (Rockets, Warriors): Won championships
- Late adopters: Scrambling to catch up
- Holdouts: Extinct

**The edge shifted**: Everyone shoots 3s now. Next edge = defense? Playmaking? 

---

### Goldsberry's Shot Quality Framework

| Zone | eFG% | Value/Shot | Verdict |
|------|------|------------|---------|
| Restricted area | 65% | 1.30 | ✅ Best |
| Corner 3 | 40% | 1.20 | ✅ Great |
| Above-break 3 | 37% | 1.11 | ✅ Good |
| Paint (non-RA) | 42% | 0.84 | ⚠️ Meh |
| Midrange | 42% | 0.84 | ⚠️ Meh |
| Long 2 | 38% | 0.76 | ❌ Bad |

**Simple formula**:
```python
shot_quality = (rim_rate × 1.30) + (corner3_rate × 1.20) + 
               (above3_rate × 1.11) + (midrange_rate × 0.84)
```

---

### Model V3 Implications

| Goldsberry Insight | V3 Action |
|--------------------|-----------|
| Shot profile quality | Add shot distribution metric |
| 3PT variance | Factor for O/U volatility |
| Corner 3 rate | Track as efficiency indicator |
| Spacing (shooters) | Count 3PT threats per lineup |
| Transition rate | Already in pace; verify weighting |
| Midrange extinction | Penalize midrange-heavy teams |

### Shot Profile Score (V3 Addition)

```python
def shot_profile_score(team):
    """
    Higher = better shot selection
    """
    weights = {
        'rim_rate': 1.30,
        'corner3_rate': 1.20,
        'above3_rate': 1.11,
        'midrange_rate': 0.84,
        'long2_rate': 0.76
    }
    score = sum(getattr(team, zone) * weight 
                for zone, weight in weights.items())
    return score

# Compare to league average (~1.05)
# Score > 1.10 = elite shot selection
# Score < 1.00 = poor shot selection
```

### Data Source
- NBA.com/stats has shot zone data
- Basketball-Reference has basic splits
- Shot quality correlates with ORtg but adds nuance

---

## Book 18: Design, Testing, and Optimization of Trading Systems — Robert Pardo (1992, updated 2008)

### Background
Pardo = Trading systems pioneer. This book is THE bible for backtesting methodology. Written for financial markets but directly applicable to sports betting systems.

### Core Warning
> "A backtest that looks too good is probably wrong. The market will humble you."

Backtesting is EASY to do wrong. This book teaches how to do it right.

### Key Concepts

#### 1. The Optimization Trap

The danger:
```
Overfit backtest → Amazing historical results → Fails live
```

Why it happens:
- Too many parameters tuned to past data
- Curve-fitting to noise
- Survivorship bias in variable selection

**Pardo's Rule**: If it looks too good, it is.

#### 2. In-Sample vs Out-of-Sample

**Critical split**:
```
Total Data
├── In-Sample (70%): Develop and tune model
└── Out-of-Sample (30%): Final validation (touch ONCE)
```

**Never** tune on out-of-sample. Once you peek, it's contaminated.

#### 3. Walk-Forward Analysis (WFA)

Pardo's signature method:
```
Period 1: Train on months 1-6, test on month 7
Period 2: Train on months 2-7, test on month 8
Period 3: Train on months 3-8, test on month 9
...continue...
```

Simulates real-world conditions:
- Model only sees past data
- Tested on unseen future
- Re-optimized periodically

```python
def walk_forward_analysis(data, train_window, test_window):
    results = []
    for i in range(len(data) - train_window - test_window):
        train = data[i : i + train_window]
        test = data[i + train_window : i + train_window + test_window]
        
        model = train_model(train)
        predictions = model.predict(test)
        results.append(evaluate(predictions, test))
    
    return aggregate_results(results)
```

#### 4. Degrees of Freedom

Rule for parameters:
```
Max parameters = Observations / 10 (conservative)
Max parameters = Observations / 20 (very safe)
```

Example:
- 82 games per team = 82 observations
- Max parameters: 4-8

**More parameters = more overfit risk**

#### 5. Statistical Significance Requirements

Minimum trades/bets for validity:
| Confidence | Min Trades |
|------------|------------|
| 90% | 100+ |
| 95% | 200+ |
| 99% | 500+ |

**For NBA season**: 
- ~1,200 games total
- ~600 at midpoint
- If picking 1/day = ~80 picks by now
- **Not yet statistically significant**

#### 6. Robustness Testing

Does your system survive parameter changes?
```python
# Test sensitivity
for param in range(base_value - 2, base_value + 3):
    results = backtest(model, param=param)
    print(f"Param {param}: ROI = {results.roi}")

# Good: Similar results across range
# Bad: Only works at exact parameter
```

**Robust system**: Works across reasonable parameter ranges

#### 7. Monte Carlo Validation

Randomize to test robustness:
```python
def monte_carlo_validation(trades, n_sims=1000):
    results = []
    for _ in range(n_sims):
        # Shuffle trade order
        shuffled = np.random.permutation(trades)
        equity_curve = calculate_equity(shuffled)
        results.append({
            'max_drawdown': max_drawdown(equity_curve),
            'final_equity': equity_curve[-1]
        })
    
    return {
        'p95_drawdown': np.percentile([r['max_drawdown'] for r in results], 95),
        'p5_final': np.percentile([r['final_equity'] for r in results], 5)
    }
```

#### 8. Transaction Costs (Vig)

Always include costs:
```python
def net_profit(bet, won, odds=-110):
    vig = 1 - (1 / (1 + 100/abs(odds)))  # ~4.5% for -110
    if won:
        return bet * (100 / abs(odds))
    else:
        return -bet
```

**Ignoring vig = fake results**

#### 9. Survivorship Bias

Don't only test on current teams:
- Include teams that relocated
- Include injured players who are now out
- Include strategies you tried and abandoned

**Test on data as it existed at the time, not hindsight**

#### 10. The Backtest Checklist

Before trusting results:
```
□ Out-of-sample validation (untouched)
□ Walk-forward analysis performed
□ Parameter count reasonable (<10)
□ Statistical significance (200+ bets)
□ Robustness tested (parameter sensitivity)
□ Vig/costs included
□ No lookahead bias
□ No survivorship bias
□ Results aren't "too good" (>10% ROI suspicious)
□ Documented methodology
```

---

### Pardo's Walk-Forward Framework

```
┌─────────────────────────────────────────────────────────┐
│                    FULL DATASET                         │
├──────────────────────┬──────────────────────────────────┤
│      IN-SAMPLE       │          OUT-OF-SAMPLE           │
│    (Development)     │      (Final Validation)          │
│         70%          │              30%                 │
└──────────────────────┴──────────────────────────────────┘

Walk-Forward within In-Sample:
┌────────┬────────┬────────┬────────┬────────┬─────┐
│Train 1 │ Test 1 │        │        │        │     │
├────────┼────────┼────────┼────────┼────────┼─────┤
│        │Train 2 │ Test 2 │        │        │     │
├────────┼────────┼────────┼────────┼────────┼─────┤
│        │        │Train 3 │ Test 3 │        │     │
├────────┼────────┼────────┼────────┼────────┼─────┤
│        │        │        │Train 4 │ Test 4 │     │
└────────┴────────┴────────┴────────┴────────┴─────┘
```

---

### Model V3 Backtest Plan

**For our NBA backtest:**

```python
# Data split
full_season = games_2025_26  # Through Feb 8

# Approach 1: Simple holdout
train = games[games.date < "2026-01-01"]  # Oct-Dec
test = games[games.date >= "2026-01-01"]  # Jan-Feb (out-of-sample)

# Approach 2: Walk-forward
for week in weeks:
    train = games[games.date < week.start]
    test = games[games.date.isin(week)]
    
    model = retrain(train)
    picks = select_best_pick_per_day(test, model)
    evaluate(picks)
```

**Constraints:**
- 1 pick per day
- Must have been playable (line available pre-game)
- Include vig (-110 standard)
- Track CLV (did we beat the close?)

---

### Realistic Expectations (Pardo-Informed)

| Metric | Suspicious | Believable |
|--------|------------|------------|
| ROI | >15% | 3-10% |
| Win Rate | >60% | 52-57% |
| Sharpe | >2.0 | 0.5-1.5 |
| Max Drawdown | <5% | 15-30% |

**If backtest shows 70% win rate, something is wrong.**

---

*FINAL BOOK - Ready for V3 Synthesis*
