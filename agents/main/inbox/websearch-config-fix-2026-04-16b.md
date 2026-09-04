# WebSearch Permission Fix — Direct Apply

Chris is in the VPS terminal right now. Here's the one-liner he can paste directly into bash to fix WebSearch permissions permanently:

```bash
echo '{"permissions":{"allow":["WebSearch"]}}' > /root/.claude/settings.json
```

That replaces the empty `{}` with the correct config. After running it, WebSearch will be auto-allowed in all Claude Code sessions — no more prompts.

If you want to add more tools later (like Bash, Read, Edit, etc.), the format is:
```json
{
  "permissions": {
    "allow": [
      "WebSearch",
      "Bash(npm:*)",
      "Read",
      "Edit"
    ]
  }
}
```

— Ryan
