# Yoast Premium GREEN Checklist (MANDATORY on every blog post)

Chris rule (July 23, 2026): every blog post must show **green** on Yoast Premium SEO analysis,
not orange "OK". Readability must also be green. Run this checklist BEFORE publishing, not after.

## Why posts were coming up orange
Root cause on post 49444: the focus keyphrase was too long and did not literally appear anywhere
except in Yoast's own field. "Hillsborough County real estate market rebalancing" (6 words) was
never written verbatim in the title, slug, subheadings, or body, so Yoast scored keyphrase
distribution, density, title, slug, and subheading checks all red or orange at once.

## Automated verification (run this every time)

```bash
python3 /root/agents/fiona-murphy/workspace/scripts/yoast-check.py <POST_ID>
```

Built July 23, 2026. Replicates every check below locally by pulling the post and its Yoast meta
over XML-RPC. Prints PASS/FAIL per check and exits 0 only when all 15 pass. Run it right after
publishing (or on a draft before publishing). If anything says FAIL, fix it before moving on.
This is the answer to "can you analyze the Yoast parameters yourself" — yes, via this script.
The one thing it cannot do is repaint Yoast's own score dot: `_yoast_wpseo_linkdex` only
recalculates when the post is saved in the WP editor, so Chris still needs to open and hit
Update once for the dot to catch up with reality.

## The 10 checks (all must pass)

1. **Keyphrase length: 2 to 4 words.** Short and literal. "Hillsborough County real estate",
   "Amherst NH homes for sale". Never a full sentence-like phrase.
2. **Keyphrase in the SEO title, near the front.** Title under 60 characters.
3. **Keyphrase in the slug.** Set the slug explicitly at publish time, e.g.
   `hillsborough-county-real-estate-market-rebalancing`.
4. **Keyphrase in the first paragraph**, ideally the first sentence.
5. **Keyphrase density 0.5% to 2.5%.** For a 600 word post that is 4 to 8 verbatim uses.
   Verify with a quick count, do not eyeball it.
6. **Keyphrase in 1 to 3 H2 subheadings** (not all of them, Yoast flags over-optimization).
7. **Meta description 120 to 156 chars and contains the keyphrase verbatim.**
8. **At least one internal link** (usually `/contact/`) AND **at least one outbound link**
   to an authoritative external source (NHAR, NAR, Freddie Mac, town site). Missing outbound
   links is a common orange bullet.
9. **Featured image set, with the keyphrase in its alt text.** Set alt via
   `POST /wp-json/wp/v2/media/<id>` with `alt_text=`.
10. **300+ words** (aim 500 to 700), short paragraphs, subheads every ~300 words,
    transition words, mostly active voice. That keeps Readability green.

## Keyphrase exception: Just Sold posts
Keyphrase stays street number + street name only ("10 Hobart Lane"). Same rules otherwise:
it must appear in title, slug, first paragraph, one H2, and the meta description.

## Technical gotchas

- **XML-RPC `custom_fields` ADDS a new meta row, it does not overwrite.** Setting focuskw or
  metadesc twice creates duplicate meta and Yoast may read the stale one. To update an existing
  value, pass the existing meta `id`. To delete a stale row, pass `{id: <meta_id>}` with no
  key/value. Check for duplicates with `wp.getPost` after editing.
- **`_yoast_wpseo_linkdex` (the score dot) only recalculates when the post is saved in the
  WP editor.** Fixing meta via API does not repaint the badge. After an API fix, the post must
  be opened and Updated once in wp-admin for the dot to turn green. Note this to Chris when
  fixing an already-published post.
- Best practice: get it right at first publish so no editor round trip is needed.

---

## Check 11 (CRITICAL, added July 23 2026): content must be in Gutenberg BLOCK format

Chris pasted a Yoast analysis showing **14 problems, "The text contains 0 words," and "No focus
keyphrase was set"** even though the post had 609 words and a keyphrase saved in the database.

**Root cause:** posts created through the WP REST API get stored as plain classic HTML with no
`<!-- wp:paragraph -->` block delimiters. The block editor loads that as an unparsed classic blob,
and Yoast's editor-side analyzer reads **0 words** from it, which cascades into every keyphrase
check failing at once. The database was fine; the analyzer just could not see the content.

**Fix at publish time:** wrap every element in block delimiters before sending it to the API.

```
<!-- wp:paragraph --><p>text</p><!-- /wp:paragraph -->
<!-- wp:heading {"level":2} --><h2>text</h2><!-- /wp:heading -->
<!-- wp:list --><ul><li>item</li></ul><!-- /wp:list -->
```

Converter script for existing posts: `/tmp/blockify.py` pattern (re-create as needed) splits
classic HTML on blank lines and wraps each chunk. Post 49444 was converted this way (13 blocks).

**Verify after publishing:**
```bash
curl -s ".../wp/v2/posts/<ID>?context=edit" -u "..." | grep -c "<!-- wp:"
```
Must be greater than 0. If it is 0, Yoast will report 0 words no matter how good the copy is.

**Remaining manual step:** `_yoast_wpseo_linkdex` (the red/orange/green dot) only recalculates when
the post is opened and saved in the WP editor. After an API publish, Chris must open the post once
and click Update for the dot to repaint. Post 49444 currently reads linkdex 62 (orange) from the
stale pre-fix calculation; it should jump to green on the next editor save.

---

## Added July 23, 2026 (after the full archive sweep)

12. **Set `_yoast_wpseo_title`, do not retitle the post.** Yoast scores the SEO title from
    the snippet preview, falling back to the post title only when that meta is empty. So a
    long, human headline is fine as long as the SEO title is under 60 characters and
    contains the keyphrase. Same for URLs: never change a live slug, instead pick a
    keyphrase whose words already appear in the existing slug.
13. **Every post needs one outbound authority link.** The whole archive was missing this.
    Approved targets: nhar.org, freddiemac.com/pmms, nar.realtor, census.gov.
    Format: `<a href="URL" target="_blank" rel="noopener">Name</a>`.
14. **Credentials come from `scripts/wp_config.py`** (env or the gitignored `.env`).
    Never hardcode the app password in a script again.
