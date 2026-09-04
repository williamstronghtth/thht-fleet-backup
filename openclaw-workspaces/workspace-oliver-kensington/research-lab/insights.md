# Insights Log

What I'm learning about what works.

---

## 2026-03-08: Initial Observations

### High Engagement Pattern (Experiment #1)
- Manual briefing on 2026-03-04
- Chris asked 4 follow-up questions
- Topics that sparked curiosity:
  - Gold investment methods
  - Ray Dalio's 15% gold thesis
  - Why gold has no yield
  - Short-term vs long-term capital gains
- **Insight:** Connecting market data to *actionable personal decisions* drives engagement

### Low Engagement Pattern (Experiments #2, #3)
- Cron-delivered briefings
- No direct response
- Possible reasons:
  - Delivered during busy periods
  - No clear "hook" to personal situation
  - Already got the info he needed earlier

### Hypotheses to Test

1. **Personal relevance wins:** Briefings that connect to Chris's portfolio/decisions outperform generic market updates
2. **Questions > statements:** End with a question to invite response?
3. **Timing matters:** 7am might be too early? Test engagement at different times
4. **Action items:** "Consider doing X" might drive more engagement than "watch for Y"

### Variables to Experiment With

| Variable | Current | Test Next |
|----------|---------|-----------|
| End with question | No | Yes |
| Personal portfolio hook | No | Yes |
| Length | Medium | Shorter |
| Experts featured | 3 | 1-2 (more depth) |

---

## Experiment Queue

1. **Next briefing (Mon 3/9):** Add a direct question at the end
2. **Following briefing:** Reference something Chris is already doing (gold purchase)
3. **Week 2:** Test shorter format with one deep expert insight

---

## Running Tally

| Metric | Value |
|--------|-------|
| Total experiments | 8 |
| Experiments with feedback | 3 |
| Avg engagement score | 2.3 (of tracked) |
| Best performing | #1 (score: 7) |
| Worst performing | #2, #3 (score: 0) |

---

## 2026-03-15: Weekly Review

### Week 2 Summary (Mar 9-13)
- 5 briefings delivered via cron (experiments 4-8)
- All included "ended_with_question" variable
- **Problem:** No feedback data recorded for these experiments
- **Fix needed:** Must track engagement signals for experiments 4-8

### Confirmed Hypotheses
1. ✅ **Personal relevance wins:** Exp #1 (gold discussion) got 7/10 engagement; generic market updates got 0
2. ⚠️ **Questions help:** Tested in experiments 4-8 but no data to confirm yet

### Rejected/Inconclusive
1. ❓ **Expert depth:** Featured 1-3 experts across experiments, no clear pattern with only 3 data points
2. ❓ **Format (bullets vs tables):** Insufficient data

### New Hypotheses to Test
1. **Briefing as conversation starter:** What if I ask Chris what he's thinking about *before* giving data?
2. **Shorter = better:** Current "medium" length may be too long for morning consumption
3. **Fewer sections, more depth:** 2-3 sections deeply vs 6 sections superficially

### Changes for Week 3
| Variable | Was | Now |
|----------|-----|-----|
| Sections | 6 | 3-4 (focused) |
| Question | End | Start AND end |
| Personal hook | Occasional | Every briefing |
| Feedback tracking | Manual | Must close loop |

### Key Insight
> The problem isn't the briefing content—it's the feedback loop. I'm flying blind without engagement data. Priority: establish reliable tracking before further experiments.

---

*Updated: 2026-03-15*

---

## 2026-03-22: Week 3 Review

### Week 3 Summary (Mar 16-20)
- 5 briefings delivered via cron (experiments 9-12, plus duplicate id 9 on Mar 17)
- All using config v2: short_to_medium, start+end questions, personal hooks
- **Critical issue persists:** No new feedback entries since Mar 15
- Feedback gap now covers experiments 4-12 (9 experiments without engagement data)

### What We Know
1. ✅ **Data dumps valued** — Chris confirmed Mar 15 he likes them
2. ✅ **Weekly cadence confirmed** — Direct positive feedback
3. ❌ **"Shorter = better" rejected** — Chris wants MORE data, not less
4. ❓ **Start/end questions** — Still no data to confirm if this drives responses
5. ❓ **Personal hooks** — Theoretically strong (Exp #1 was 7/10) but untested at scale

### Content Staleness Risk
- Expert coverage narrowing: last 5 briefings feature only Damodaran + Batnick
- Same themes recurring: AI scenarios, ERP bias, private credit, Schwab CEO
- Risk of "same briefing every day" fatigue

### Market Context
- S&P dropped from ~6816 to ~6632 over the period — sustained correction
- Briefings tracked this well but may be too reactive (daily noise vs weekly signal)

### Hypotheses Updated

| Hypothesis | Status | Evidence |
|-----------|--------|----------|
| Personal relevance wins | ✅ Confirmed | Exp #1 vs rest |
| Data dumps > brevity | ✅ Confirmed | Direct feedback Mar 15 |
| Questions drive response | ❓ Inconclusive | 9 experiments, 0 feedback |
| 2 experts max = better depth | ❓ Inconclusive | No engagement data |
| Expert variety prevents staleness | 🆕 New | To test week 4 |
| Weekly digest > daily drip | 🆕 New | Chris said weekly valuable |

### Changes for Week 4
| Variable | Was | Now | Rationale |
|----------|-----|-----|-----------|
| Length | short_to_medium | medium | Chris wants data dumps |
| Expert rotation | Same 2 daily | Rotate across full list | Prevent staleness |
| Feedback tracking | Broken | Must fix — add self-check | 9 experiments blind |
| Experiment ID | Duplicate id 9 | Fix numbering | Data integrity |

### Key Insight
> **The feedback loop is the #1 problem.** Content quality is decent — Chris confirmed he values the briefings. But without engagement tracking, I can't optimize. Week 4 priority: find a reliable way to measure if briefings land.

### Possible Feedback Mechanisms
1. Ask Chris directly once a week what he found useful
2. Track if he references briefing content in later conversations
3. Monitor reply rate to end-of-briefing questions
4. Simple thumbs up/down prompt occasionally

*Updated: 2026-03-22*

---

## 2026-03-29: Week 4 Review

### Week 4 Summary (Mar 23-27)
- 4 briefings delivered via cron (experiments 14-17)
- Config v3: medium length, end questions, personal hooks
- **Feedback loop still broken:** 0 new entries since Mar 15 (now 3 weeks)
- Market volatility high: S&P dropped to ~6592, gold surged to $4591+, Iran tensions

### Content Quality Assessment
- **Strong:** Tracked volatile week well — 200-DMA breach, gold-yields divergence, stagflation signals
- **Weak:** Expert rotation NOT executed — still Damodaran + Batnick despite 12-expert list
- **Risk:** Content staleness accelerating if rotation doesn't happen

### Hypothesis Status Update

| Hypothesis | Status | Update |
|-----------|--------|--------|
| Personal relevance wins | ✅ Confirmed | Still the core insight |
| Data dumps > brevity | ✅ Confirmed | Medium format works |
| Start with question | ❌ Rejected | 10+ experiments, 0 evidence of impact |
| Expert rotation prevents staleness | ⚠️ UNTESTED | Failed to execute 2 weeks in a row |
| Friday feedback check | ⚠️ UNTESTED | Never implemented |

### Critical Issue: The Feedback Gap
- **13 experiments without engagement data** (exp 4-17)
- Can't optimize without knowing what lands
- Flying blind for 3 weeks

### Committed Changes for Week 5 (Mar 30 - Apr 4)

| Change | Why | How |
|--------|-----|-----|
| Strict expert rotation | Prevent staleness | Queue: Howard Marks → Lyn Alden → Matt Levine |
| Friday feedback ask | Close the loop | Direct Telegram message: "What landed this week?" |
| Drop start_with_question | No evidence it works | Keep end question only |
| Manual engagement logging | Stop the bleeding | Note any reply/reference in feedback.jsonl same day |

### Key Insight
> **Execution is the problem, not strategy.** The config has said "rotate experts" and "add Friday check" for two weeks. Neither happened. Week 5 commitment: DO the things, don't just plan them.

### Metrics to Watch
- Did I actually feature a non-Damodaran/Batnick expert? (Y/N each day)
- Did I send the Friday feedback ask?
- Did Chris respond to anything?

*Updated: 2026-03-29*

---

## 2026-04-05: Week 5 Review

### Week 5 Summary (Mar 30-Apr 3)
- 5 briefings delivered via cron (experiments 18-22)
- Config v4 executed more faithfully than prior weeks
- **Improvement:** expert rotation finally happened — Howard Marks and Lyn Alden appeared across the week
- **Problem still unresolved:** no new structured feedback entries were logged

### Engagement Readout
- **Highest measured engagement remains Experiment #1 (score: 7)**
- No later experiment has recorded measurable engagement, so all newer conclusions remain directional rather than validated
- Direct feedback still says Chris values **weekly briefings** and **more data, not less**

### What Worked This Week
1. ✅ **Execution improved** — the planned rotation actually happened
2. ✅ **Fresher expert mix** — Howard Marks + Lyn Alden created more variety than the repeated Damodaran/Batnick loop
3. ✅ **Medium-length data-rich format remains aligned** with Chris's stated preference

### What Did Not Work
1. ❌ **Feedback capture still failed** — experiments 4-22 remain largely blind
2. ❌ **Friday feedback mechanism did not generate a recorded measurable response**
3. ⚠️ **Rotation breadth still too narrow** — freshness improved, but only partially; not enough to test the full thesis

### Hypothesis Status Update

| Hypothesis | Status | Update |
|-----------|--------|--------|
| Personal relevance wins | ✅ Confirmed | Still the strongest evidence from Exp #1 + direct feedback |
| Data dumps > brevity | ✅ Confirmed | Supported by Mar 15 feedback |
| Start with question helps | ❌ Rejected | Already removed; no evidence |
| Expert rotation reduces staleness | ⚠️ Directionally positive, not confirmed | Better execution this week, but no engagement measurement |
| Friday feedback ask closes the loop | ❓ Inconclusive | Implemented, but no recorded evidence of success |
| Specific asks beat generic asks | 🆕 New | Test next with one-line targeted Friday prompt |

### Changes for Week 6
| Change | Why | How |
|--------|-----|-----|
| Make Friday ask more specific | Generic asks may be too easy to ignore | Ask: "Which section was most useful this week — market snapshot, expert radar, risk radar, or strategic thought?" |
| Broaden rotation | Need a cleaner test of freshness | Move next queue to Matt Levine, Nick Timiraos, Tracy Alloway, Joe Weisenthal |
| Force same-day logging | Stop losing evidence | Log any reply/reference/action to feedback.jsonl immediately |
| Keep medium format | Matches stated preference | No shortening |

### Key Insight
> **This week proved execution can improve, but optimization is still bottlenecked by measurement.** The briefing format is probably good enough; the analytics loop is not.

### Current Priority Order
1. Fix measurement discipline
2. Keep explicit personal relevance
3. Test broader expert freshness
4. Refine feedback ask wording before changing core format again

*Updated: 2026-04-05*
