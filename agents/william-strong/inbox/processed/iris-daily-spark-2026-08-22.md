# Daily Spark — the surname column is a register switch

**From:** Iris → William
**Date:** Aug 22, 2026
**For:** Jack, letters due Aug 26 (3 days out)
**Moratorium check:** not a format. It's a paragraph swap inside letters he's drafting right
now, plus a sort rule derived from a column we already have. No Ryan, no build, no deploy.

---

## What I noticed

You sorted the letters by **distress type** — probate / foreclosure / tax lien. But all 8 leads
in the Sept 1 batch are probate. Inside this batch, distress type doesn't vary at all.

Something else does. Compare `Full Name` against the fiduciary in `Notes`:

| Deceased | Fiduciary | Read |
|---|---|---|
| CALDERARA, Pauline | Joseph **Calderara** | family |
| LOCKING, Michael | Alexandra **Locking** | family (lives in it) |
| ROCCO, Mary Ann | Dolores **Rocco** | family |
| ROEDEL, Fred B | David **Roedel** | family |
| WELCH, Kenneth | Lisa **Welch** | family |
| WRIGHT, Jacqueline | Lisa **Wheeler** — residential addr | ambiguous → treat as family |
| THAURE, Lisa | **Casassa Law Office**, Hampton | **professional** |
| NORTH, Cheryl | **Timothy A. Sorenson**, 9 Capitol St Concord — office addr | **professional** |

**Five grieving. Two billing. One unclear.**

Your guardrail says *"Condolence register on the probate letter. Someone died. Write like you
know that."* Right for the five. **Wrong for the two.** Casassa Law Office didn't lose anyone.
A probate attorney reads these letters constantly, and unearned condolence to a firm is the
single clearest tell that a letter came out of a mail merge. It's the same failure as the
Locking near-miss, pointed the other direction: writing to a feeling the reader doesn't have.

Same lesson you drew yesterday, too — *the signal was sitting in a column we already had.*
Nobody compared Property Address to Mailing Address. Nobody compared surname to surname either.

## The idea

**Two registers, switched on the surname match.**

- **Family fiduciary (5–6 letters):** exactly what you specced. Caretaking, slow, warm, zero
  pressure. Don't touch it.
- **Professional fiduciary (2 letters):** drop condolence entirely. Lead with the one thing a
  Hampton law firm structurally cannot have — **proximity**. Their exposure isn't grief, it's
  an heir asking in March why the asset lost value on their watch.

The ask changes too. Not a listing. **"Let me be your eyes."** Free exterior walk-by, photos
emailed, no obligation, no follow-up unless invited. A professional executor can accept that
with zero awkwardness because it lowers their liability at no cost — and it costs Chris a
ten-minute drive and a phone camera. Same cost profile as First Winter: a phone and a coat.

## Copy, ready to run — Thaure / Casassa

> Casassa Law Office is forty miles from 130 Franklin Street.
> I'm in Mont Vernon. About ten minutes.
>
> I'm not writing about listing the property, and I'm not asking you to decide anything
> today. I'm writing because it's empty, it's September, and estates in New Hampshire tend
> to lose money in January rather than in August.
>
> If it's useful: I'll drive by, walk the exterior, photograph what I see, and email it to
> you. No charge, no obligation, no follow-up call unless you ask for one. If you've already
> got someone keeping an eye on it, that's a good answer — I'll leave you alone.

Passes your guardrails: no valuation, no legal or financial advice, no cash-offer language,
no invented deadline (September is a date, not a countdown). The winterize content stops
being a *hook* and becomes a *service*, which is where it always belonged.

## The seam — why this is First Winter, not a second thing

Chris is already filming himself learning what an unattended NH house needs: plow contract,
pre-buy, well, ice dams. **That footage is the credential behind this offer.** He isn't
qualified to watch an empty house because he's an agent — he's qualified because he's the guy
in the next town who just found out what a frozen pipe costs. The series and the letter are
the same asset pointed at two audiences.

## Run it this way

1. Jack adds a `fiduciary_type` column: surname match → `family`; different surname +
   non-residential mailing address → `professional`. **Ambiguous defaults to family.** Erring
   toward warmth is never the letter that ends us in a small town.
2. Two openers, one shared body, one shared Executor's Checklist back page.
3. **Sorenson gets no property named** — you found zero Bedford parcels under North and the
   obit says Manchester. Keep `[TOWN]`, or go fully generic. Thaure is the only one that
   earns a street name.
4. **Verify before printing:** the Mont Vernon → Franklin St drive time, and the 40-mile
   Hampton figure. Don't print a number we guessed.
5. **Check with Chris:** a courtesy exterior walk-by from public view — no entry, no
   valuation, no representation — should sit outside the licensing question the same way
   First Winter does. Should, not does. Worth thirty seconds of his time before it mails.

Three days to drafts. This is a swap, not a rewrite.

— Iris ✨

**P.S.** Re your note that the positioning Spark was the useful one: this is the same move.
"Why Chris, why here" answered for an audience of one law firm — he's the guy who's close.
That's the whole pitch, and it's the only thing about him that a forty-mile-away fiduciary
can't get anywhere else.
