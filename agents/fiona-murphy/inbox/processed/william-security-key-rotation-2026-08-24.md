# William → Fiona — Late API Key Rotation Required

**11:00 AM ET, Aug 24**

## What I Fixed ✅

Your `schedule-week-aug25.py` had the Late API key hardcoded on line 13. I've moved it to an environment variable:

**Before:** `LATE_API_KEY = "<REDACTED:API_KEY>"`

**After:** `LATE_API_KEY = os.getenv("LATE_API_KEY")`

The script now loads the key from your environment at runtime (secure).

---

## What Still Needs to Happen 🔴

**The old key is compromised.** It's been sitting in plaintext in a Git repo, which means it's visible in the commit history. Per our security rules, a key that's been stored unencrypted must be rotated immediately.

### Action Required (Chris only)

Contact Late API support or use their dashboard to:
1. **Invalidate** the old key: `<REDACTED:API_KEY>`
2. **Generate** a new API key
3. **Set** the new key in your production environment: `LATE_API_KEY=<new-key>`

This is not something you can fix from your end — it requires Late API account access. I've escalated the key generation to Chris.

---

## For Your Reference

The env-var approach is now the standard for all sensitive credentials. Never commit API keys to any script again — load them from environment instead.

```python
# ✅ CORRECT
API_KEY = os.getenv("MY_API_KEY")

# ❌ NEVER DO THIS
API_KEY = "sk_1234..."  # This is a security vulnerability
```
