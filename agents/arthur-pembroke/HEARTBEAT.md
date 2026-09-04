# HEARTBEAT.md

## Morning Story Delivery — THE LONG HISTORY PROJECT

**Active as of: 2026-06-20**
**System:** The Long History Project (chronological narrative, Big Bang → present)
**State file:** `memory/long-history/progress.json`
**Index file:** `memory/long-history/index.md`

---

### Daily Loop (do this every morning, in order)

1. **Read the bookmark.** Open `memory/long-history/progress.json`. Note: current era, time reached, last topic, open threads, coming up.

2. **Pick today's subject.** The next logical step forward in time from `time_reached`. One clear focal subject. Use the pacing table (in the Long History Project PDF) to stay on track.

3. **Write the entry (~1,000 words)** using this format:
```
Entry #[N] · [date]
Era: [era]  |  Time: [time]  |  Place: [region]

[EVOCATIVE TITLE IN CAPS]

[~1,000 words: hook, development, arc, forward pull]

---
Where we are: [1-2 sentences orienting the reader in the full Big Bang → today journey, gesturing at what comes next]
```

4. **Send via Telegram.** If the entry is too long for one message (>4,096 chars), split at a natural paragraph break and send as two consecutive messages:
```bash
curl -s -X POST "https://api.telegram.org/bot<REDACTED:TELEGRAM_BOT_TOKEN>/sendMessage" \
  -d chat_id="8560812913" \
  --data-urlencode "text=PART_TEXT"
```

5. **Update the bookmark.** In `memory/long-history/progress.json`:
   - Increment `entry_number`
   - Update `time_reached`
   - Update `last_topic` and `last_entry_date`
   - Update `open_threads` and `coming_up`
   - Update `pacing` counts

6. **Append to the index.** Add one row to `memory/long-history/index.md`:
   `| [N] | [date] | [era] | [time] | [region] | [title] |`

7. **Append session summary** to `memory/YYYY-MM-DD.md`

---

### Pacing Reference (Era budgets for ~4-year / ~1,460-entry run)

| Era | Span | Budget |
|-----|------|--------|
| Cosmic Origins (Big Bang → Earth) | 13.8 Gya–4.5 Gya | ~30 entries |
| Early Earth & origin of life | 4.5 Gya–541 Mya | ~45 entries |
| Rise of complex life | 541 Mya–2.5 Mya | ~75 entries |
| Human prehistory | 2.5 Mya–3000 BCE | ~100 entries |
| Ancient world | 3000–500 BCE | ~190 entries |
| Classical antiquity | 500 BCE–500 CE | ~235 entries |
| Post-classical / medieval | 500–1500 | ~275 entries |
| Early modern | 1500–1800 | ~235 entries |
| Long 19th century | 1800–1914 | ~130 entries |
| 20th century to present | 1914–today | ~145 entries |

Do a pacing self-check weekly: compare entries used vs. budget per era.

---

### Entry Type Rotation (vary these to keep a long-running reader engaged)
- Event entries
- Person/profile entries
- Everyday-life entries
- Big-idea/turning-point entries
- Zoom-out/interlude entries ("meanwhile, around the world")

---

### Craft Rules (non-negotiable)
- Open with a hook, never "On this day"
- One focal subject per entry
- Make abstractions physical — show the hand, the stone, the firelight
- Give it an arc: tension, stakes, consequence
- Convey scale honestly (cosmic calendar analogies in deep time)
- End with forward pull
- Reward loyal readers with callbacks to earlier entries
- Never fabricate. Honor uncertainty. Stay in chronological order.
