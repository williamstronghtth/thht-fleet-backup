# Oliver's Research Lab

Self-improving system for morning briefings + cognitive state tracking.

Inspired by Karpathy's autoresearch + OpenAlice brain system.

## Concept

```
Run briefing → Measure engagement → Keep what works → Iterate
Track state → Log convictions → Review outcomes → Learn
```

---

## Brain System (Phase 1 — Implemented 2026-03-14)

### Working Memory (`working-memory.md`)
Read at START of each session. Update at END.
- Current macro view
- Chris's situation & active items
- What changed since last session
- Active hypotheses

### Conviction Tracking (`convictions.jsonl`)
Log every market view and advice with:
- Timestamp
- Subject
- Conviction level (low/medium/high)
- Thesis with reasoning
- Price at call (if applicable)
- Status (active/closed/tracking)

Creates audit trail for post-mortems.

---

## Briefing Optimization (Original System)

## Feedback Signals

How I measure "did this work?":

| Signal | Weight | Meaning |
|--------|--------|---------|
| Chris responded | +1 | He read it |
| Asked follow-up question | +2 | It sparked curiosity |
| Mentioned it later | +3 | It stuck |
| Took action (bought gold, etc.) | +5 | Real impact |
| No response | 0 | Didn't land |
| "Too long" or "skip this" | -2 | Wrong format |

## Experiment Variables

Things I can tweak:

1. **Format** - Length, sections, bullet vs prose
2. **Sources** - Which experts to feature
3. **Depth** - Headlines only vs analysis
4. **Tone** - Data-heavy vs narrative
5. **Timing** - What time works best
6. **Sections** - Which to include/exclude

## Files

- `experiments.jsonl` - Log of each briefing + variables used
- `feedback.jsonl` - Chris's engagement signals
- `insights.md` - What I've learned (human-readable)
- `current-config.json` - Active briefing configuration
- `best-config.json` - Best performing config so far

## Process

1. Morning cron runs briefing with current config
2. I log the experiment (variables used, content sent)
3. Throughout day, I track engagement signals
4. Weekly: Review results, update config toward what works
5. Repeat

## Version History

- v1 (2026-03-08): Initial setup
