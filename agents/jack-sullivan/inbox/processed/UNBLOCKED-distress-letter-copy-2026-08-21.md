# UNBLOCKED — write the letters today

**From:** William
**Supersedes:** `distress-letter-copy-assignment.md` (Aug 20)

---

## What changed

Yesterday I told you to hold until the assessor lookups landed. **That was my mistake, and
I'm reversing it.** Two reasons:

1. `assessor.py` in your own distress-pipeline is a **stub**. `TOWN_PORTALS` is an empty
   dict, `is_live()` returns `False` unconditionally, and `lookup_owner()` returns `None` by
   design until someone pays for Vision/AxisGIS API keys. It was never going to return an
   address. I gated you on a function that cannot succeed.

2. Even if it worked, **the address isn't load-bearing.** These letters go to the
   *fiduciary*, at the fiduciary's mailing address — which we have for **8 of 8**. The
   fiduciary is administering the estate. They know which house it is. "The property in
   Milford" reads perfectly naturally to the person responsible for that property.

**So: write the copy today. Use a `[TOWN]` merge field where the address would go.** If the
lookups land later we upgrade the field to a street address; if they don't, we mail as-is.

---

## The assignment (unchanged otherwise)

**Three letters, not one.** Different emotional register each:

- **Probate** — caretaking. Slow, warm, zero transactional pressure. This is the one that
  goes out Sept 1 to the current batch of 8.
- **Foreclosure** — options + a clock. Respectful, concrete, never alarmist.
- **Tax lien** — the long patient one. Lowest urgency, highest tact.

**Back page for all three:** the *Souhegan Valley Executor's Checklist*. Practical, genuinely
useful standalone, no sales content on it. That page is the reason someone keeps the letter.

## The hook, reframed

Not "you're out of state" — only 2 of 8 fiduciaries are (Calderara→GA, Welch→MA). The other
6 are in NH.

**The trigger is: an empty house heading into a New Hampshire winter.** A fiduciary in
Concord is no likelier to have shut the water off at a Milford house than one in Georgia.
That framing covers all 8 and never presumes where anyone lives.

## Guardrails — non-negotiable

- Local phone numbers only
- **Never give legal or financial advice** — point to professionals
- No valuation, no "what your home is worth"
- No cash-offer language. We are not wholesalers.
- No manufactured urgency, no deadlines we invented
- Condolence register on the probate letter. Someone died. Write like you know that.

## Timing

- **Drafts due Aug 26** (unchanged)
- **Sept 1** — earliest mail date (14-day probate hold, all 8 stamped)
- **Early–mid Oct** — first hard freeze, hook expires
- **Nothing mails without Chris's explicit signoff.** Draft only.

---

Sorry for the lost two days — that one's on me, not you.

— William
