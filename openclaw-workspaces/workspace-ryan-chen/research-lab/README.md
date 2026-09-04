# Ryan's Research Lab 🔬

Self-improvement loop for engineering + tech scouting. Two jobs:
1. Track my own work → get better at shipping
2. Scout new tech → find efficiencies for the team

Inspired by Karpathy's autoresearch — iterate on yourself.

---

## Part 1: Engineering Tracking

### Structure

| File | Purpose |
|------|---------|
| `experiments.jsonl` | Every task logged with config used |
| `outcomes.jsonl` | Results — success, time, bugs, rework |
| `current-config.json` | Active settings I'm testing |
| `insights.md` | Human-readable learnings |

### How It Works

```
Start task → Log experiment (estimate, approach, stack)
     ↓
Complete task → Log outcome (actual time, success, bugs)
     ↓
Sunday 6pm ET → Analyze week's data
     ↓
Update insights + config → Repeat forever
```

### Logging Format

**experiments.jsonl**
```json
{
  "id": "exp-001",
  "timestamp": "2026-03-08T22:25:00Z",
  "task": "build_research_lab",
  "type": "feature|bugfix|integration|deployment",
  "stack": "express_vanilla|react|supabase|browser",
  "estimate_hours": 0.5,
  "approach": "description of approach",
  "config_version": 1
}
```

**outcomes.jsonl**
```json
{
  "id": "exp-001",
  "timestamp": "2026-03-08T22:26:00Z",
  "task": "build_research_lab",
  "success": true,
  "actual_hours": 0.25,
  "bugs": 0,
  "rework": false,
  "notes": "Clean first-try deploy"
}
```

### Metrics

1. **Estimation accuracy**: estimate_hours vs actual_hours
2. **First-try success rate**: success && !rework
3. **Stack effectiveness**: which stacks for which task types
4. **Bug rate**: bugs per task type

---

## Part 2: Tech Scouting

Weekly research to find tools and techniques that help the team.

### Focus Areas

| Area | Why | Who Benefits |
|------|-----|--------------|
| AI/Agent tooling | We're an AI-first team | Everyone |
| Prediction market tools | Elliot's edge | Elliot |
| Sports data/APIs | Nolan's edge | Nolan |
| Marketing automation | Content pipeline | Fiona |
| Real estate tech | Core business | Chris, William |
| Financial data | Oliver's domain | Oliver |
| Developer tools | Ship faster | Ryan |

### Files

| File | Purpose |
|------|---------|
| `scouting.jsonl` | Tools/techniques discovered |
| `evaluations.jsonl` | Tested tools with verdict |
| `tech-radar.md` | Current recommendations |

### Scouting Format

**scouting.jsonl**
```json
{
  "id": "scout-001",
  "timestamp": "2026-03-30T00:00:00Z",
  "name": "polyterm",
  "category": "prediction_markets",
  "source": "William forwarded from Elliot",
  "url": "github.com/NYTEMODEONLY/polyterm",
  "summary": "Polymarket whale tracking, smart money detection",
  "potential_value": "high|medium|low",
  "effort_to_implement": "high|medium|low",
  "benefits_who": ["elliot"],
  "status": "discovered|evaluating|tested|adopted|rejected"
}
```

**evaluations.jsonl**
```json
{
  "id": "scout-001",
  "timestamp": "2026-03-31T00:00:00Z",
  "tested": true,
  "works": true,
  "integration_hours": 4,
  "verdict": "adopt|hold|reject",
  "notes": "Works well, needs Kalshi market mapping"
}
```

---

## Weekly Cadence

### Sunday 5pm EST — Tech Scout
1. Search for new tools in focus areas
2. Check HN, GitHub trending, Twitter/X, Product Hunt
3. Review any forwarded leads (like polyterm)
4. Log discoveries to scouting.jsonl
5. Pick 1-2 high-potential items to evaluate this week

### Sunday 6pm EST — Engineering Review  
1. Calculate success rates by task type
2. Identify estimation drift
3. Update insights.md with patterns
4. Adjust config if data supports it

### Sunday 6:30pm EST — Report to Chris
Combined report:
- Engineering: X tasks, Y% success, estimation accuracy
- Tech Scout: X new tools found, Y evaluated, Z adopted
- Recommendations: Top 1-2 things worth exploring

---

## Success Criteria

### Engineering
- [ ] Estimation accuracy within 20%
- [ ] First-try success rate > 80%
- [ ] Bug rate < 0.5 per task

### Tech Scouting
- [ ] 5+ tools evaluated per month
- [ ] 1+ adopted tool per month that saves time
- [ ] No major tech miss (competitor uses something we should have found)

---

*"Ship better code. Find better tools. Make the team faster."*
