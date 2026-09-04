# William's Research Lab 🔬

Self-improvement loop for leadership & communication. Iterate on what works.

## Structure

| File | Purpose |
|------|---------|
| `experiments.jsonl` | Every task logged with approach used |
| `outcomes.jsonl` | Results — accepted, edited, followup needed |
| `current-config.json` | Active settings (tone, detail levels) |
| `insights.md` | Human-readable learnings |

## How It Works

```
Start task → Log experiment (type, approach, who it's for)
     ↓
Complete → Log outcome (accepted? edited? followup?)
     ↓
Sunday 6pm ET → Analyze week's data
     ↓
Update insights + config → Repeat forever
```

## Key Metrics

1. **Acceptance rate**: drafts used as-is vs edited vs rewritten
2. **Delegation clarity**: tasks completed without clarification
3. **Handoff quality**: team outputs match expectations
4. **Resolution speed**: time to solve problems

## Logging Format

### experiments.jsonl
```json
{
  "id": "exp-001",
  "timestamp": "2026-03-08T22:35:00Z",
  "task": "client_message_draft",
  "type": "communication|delegation|analysis|content",
  "approach": "professional_warm",
  "for": "chris|client|fiona|ryan",
  "config_version": 1
}
```

### outcomes.jsonl
```json
{
  "id": "exp-001",
  "timestamp": "2026-03-08T22:36:00Z",
  "task": "client_message_draft",
  "success": true,
  "accepted": "as_is|edited|rewritten",
  "followup_needed": false,
  "notes": "Client responded positively"
}
```

---

*"Quality over speed is our True North."*
