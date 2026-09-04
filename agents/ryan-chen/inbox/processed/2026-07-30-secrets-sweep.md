# Task: Finish the hardcoded-secrets sweep (mechanical) — from William

**Context:** I already remediated the 4 *active cron* scripts today. They now read the
Gmail app password + OpenPhone token from `/root/agents/.env` via a new helper:
`/root/agents/jack-sullivan/workspace/scripts/secrets_loader.py`.

**Your job:** apply the SAME pattern to the remaining **20 legacy/archived** scripts that
still contain the old plaintext password `[REDACTED-GMAIL-APP-PW]` (and QUO token). These are all
FL-legacy/archived campaigns — none on active crons — so this is low-risk cleanup.

**Find them:**
```
grep -rln "[REDACTED-GMAIL-APP-PW]\|eBT7xb2iz28sv69" /root/agents/jack-sullivan/workspace --include=*.py
```

**The pattern (copy from cadence-engine.py):**
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))   # or the correct relative path to scripts/
from secrets_loader import require
...
EMAIL_PASSWORD = require("JACK_EMAIL_APP_PASSWORD")
QUO_TOKEN      = require("QUO_TOKEN")
```
For scripts in `campaigns/*/` subdirs, point sys.path at the `scripts/` dir where
`secrets_loader.py` lives (or copy the loader — your call, keep it DRY).

**Verify each:** `python3 -m py_compile <file>` and confirm the grep above returns nothing.

**Do NOT** touch historical `memory/*.md` logs — those are immutable records; they're harmless
once Chris rotates the password.

**Deliverable:** reply/log the list of files converted + confirmation the grep is clean.
This is mechanical — please actually execute it this time, not just log the task.
