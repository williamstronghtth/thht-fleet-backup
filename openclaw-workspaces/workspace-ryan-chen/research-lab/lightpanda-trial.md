# Lightpanda Week-Long Trial

**Start Date:** 2026-03-30
**End Date:** 2026-04-06
**Goal:** Evaluate if Lightpanda can replace Chrome for most headless browser tasks

---

## Baseline (Chrome)

- **Memory usage:** ~8.5 GB (20+ processes)
- **Server RAM:** 7.8 GB total (over-committed)
- **Startup time:** Already running (persistent)

---

## Test Cases

### Daily Tests (run each morning)

| Test | URL | Chrome | Lightpanda | Notes |
|------|-----|--------|------------|-------|
| Simple page | example.com | ✓ | ✓ | |
| JS-heavy SPA | clientlist.onrender.com | | | Our CRM |
| Data scrape | ESPN MLB scores | | | Nolan's data |
| Kalshi markets | kalshi.com | | | Elliot's platform |
| Protected site | zillow.com | | | Anti-bot test |

### Metrics to Track

1. **Memory:** `ps aux | grep lightpanda` RSS vs Chrome
2. **Speed:** Time to render page (wall clock)
3. **Success rate:** Did it render correctly?
4. **JS execution:** Did dynamic content load?
5. **Compatibility:** Any sites that fail?

---

## Daily Log

### Day 1 (2026-03-30) — Setup

- [x] Installed Lightpanda binary
- [x] Verified basic fetch works
- [ ] Run comparison tests
- [ ] Document memory usage

**Memory test:**
```
Chrome: ~8.5 GB
Lightpanda: TBD
```

---

### Day 2 (2026-03-31)



---

### Day 3 (2026-04-01)



---

### Day 4 (2026-04-02)



---

### Day 5 (2026-04-03)



---

### Day 6 (2026-04-04)



---

### Day 7 (2026-04-05)



---

## Final Verdict (2026-04-06)

**Recommendation:** TBD

**Use cases where Lightpanda wins:**
- 

**Use cases where Chrome still needed:**
- 

**Cost/benefit:**
- Memory saved:
- Speed improvement:
- Compatibility issues:
