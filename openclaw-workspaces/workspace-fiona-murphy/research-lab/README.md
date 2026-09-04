# Fiona's Research Lab 🔬

Self-improvement loop for marketing & content. Track what resonates, iterate on what works.

## Structure

| File | Purpose |
|------|---------|
| `experiments.jsonl` | Every post/campaign logged with approach used |
| `outcomes.jsonl` | Results — engagement, reach, leads generated |
| `current-config.json` | Active settings (formats, times, topics) |
| `insights.md` | Human-readable learnings |

## How It Works

```
Create content → Log experiment (format, topic, time, platform)
     ↓
Post goes live → Log outcome (engagement, reach, leads)
     ↓
Sunday 6pm ET → Analyze week's data
     ↓
Update insights + config → Repeat forever
```

## Key Metrics

1. **Engagement rate** — likes, comments, shares per post
2. **Reach** — how many people saw it
3. **Lead generation** — did it drive inquiries?
4. **Approval rate** — content approved as-is vs revised
5. **Platform performance** — what works where

## Logging Format

### experiments.jsonl
```json
{
  "id": "exp-002",
  "timestamp": "2026-03-09T10:00:00Z",
  "task": "instagram_post",
  "type": "content",
  "format": "carousel",
  "topic": "market_update",
  "platform": "instagram",
  "posting_time": "10am",
  "config_version": 1
}
```

### outcomes.jsonl
```json
{
  "id": "exp-002",
  "timestamp": "2026-03-10T10:00:00Z",
  "task": "instagram_post",
  "success": true,
  "engagement": 127,
  "reach": 1450,
  "leads": 2,
  "approved_as_is": true,
  "notes": "Market update carousel performed well"
}
```

## Weekly Review Cron

Set this up in your session:
- **Schedule:** Sundays 6pm ET
- **Task:** Analyze experiments.jsonl and outcomes.jsonl, identify patterns, update insights.md, report to Chris

---

*"Content that doesn't convert is just noise."*
