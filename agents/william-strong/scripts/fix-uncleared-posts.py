"""Rewrite scheduled Late posts that contain NOT-CLEARED figures.

Why: CLEARED-FIGURES-2026-08-24.md is the canonical figure list. These posts
cite 11% inventory, 1.4 months supply, "7-day DOM", "hottest market in America",
and an NH-vs-MA tax claim -- none of which are sourced. Two of them also
contradict posts we already published (24-day DOM on Aug 18, prices UP ~3%).
"""
import json
import os
import sys
import urllib.request

API_KEY = os.getenv("LATE_API_KEY")
if not API_KEY:
    print("ERROR: LATE_API_KEY not set in environment.")
    sys.exit(1)

BASE_URL = "https://getlate.dev/api/v1"

REPLACEMENTS = {
    # Tonight 7:30 PM ET -- "inventory jumped 11%", "prices are negotiating"
    # (prices are UP ~3% YoY; the copy says the opposite)
    "6a8c2c0313bcc2a19625e0f5": """A correction worth making, because we would rather be right than loud.

You will see a lot of "the market is cooling" content right now. In Hillsborough County, prices are not cooling. Redfin's July numbers put the median in the mid-$500Ks, up roughly 3% year over year. The New Hampshire Association of Realtors, measuring single-family only, has it higher still. Different methodologies, same direction: up.

What has genuinely moved is the cost of borrowing. The 30-year fixed came in at 6.65% for the week ending August 20, the second consecutive weekly decline.

So the accurate read is not "prices are falling." It is "money got a little cheaper while homes kept appreciating."

If someone is telling you to wait for a price drop in Southern NH, ask them which number they are looking at.""",

    "6a8c2c05ec364647d9a94d29": """"The market is cooling" - not in Hillsborough County. July median is mid-$500Ks, up ~3% YoY (Redfin). What actually moved is borrowing: 30-yr fixed at 6.65% for the week ending Aug 20, second straight weekly decline. Cheaper money, not cheaper homes.""",

    # Thu 8 AM ET -- "hottest housing market in America" + "1.4 months inventory"
    "6a8c2c07ec364647d9a94dfd": """Nashua under $500,000 is still competitive. Above it, the picture changes.

In the $500,000 to $900,000 range, where most relocating families actually land, Amherst, Hollis, and Bow are worth a hard look. More negotiating room, more time to decide, and school districts that hold their value.

You will see plenty of market-wide headlines about Southern NH. They are not that useful. Your price band and your town matter far more than the regional average.

Tell us your number and the commute you can live with, and we will tell you which towns actually fit.""",

    "6a8c2c08ec364647d9a94e5c": """Nashua under $500K: still competitive. $500K-$900K in Amherst, Hollis, Bow: real negotiating room. Market-wide headlines do not help you much - your price band and your town do. What is your number?""",

    # Sat 8 AM ET -- "7-day average sales time" (we published "24-day" on Aug 18)
    "6a8c2c39e7d11f6543888c90": """The question we get most from Boston-area families: what does Southern New Hampshire actually get me?

Fair question, and the honest answer is that it depends more on town than on budget. Twenty minutes of driving in this valley can change what your money buys more than fifty thousand dollars can.

Amherst and Hollis carry a school-district premium. Milford gives you more house for the same number. Mont Vernon trades convenience for quiet and a very good elementary school. Nashua gives you services and commuter rail access.

None of those is the right answer. One of them is the right answer for you.

Send us your budget and your must-haves. We will map it against towns, not averages.""",

    "6a8c2c3aec364647d9a963d3": """Boston families ask: what does Southern NH actually get me? Depends more on town than budget. Amherst and Hollis carry a school premium. Milford gets you more house. Mont Vernon trades convenience for quiet. Nashua gets you commuter rail. Which tradeoff is yours?""",

    # Sat 7:30 PM ET -- unsourced "lower taxes" vs MA (NH property rates are
    # among the highest in the US; the claim may be flatly false)
    "6a8c2c3de7d11f6543888ddb": """What does your money buy in Boston's suburbs versus Southern New Hampshire?

In Newton, Wellesley, or Brookline, $1.2 to $1.5 million is roughly a four-bedroom. That same budget in Southern NH generally buys a newer home, meaningfully more land, and a commute that is longer in miles but often not much longer in minutes outside rush hour.

One thing we are not going to tell you: that your total tax bill will be lower. New Hampshire has no income or sales tax, but property tax rates here are among the highest in the country, and the net depends entirely on your income, your town, and your assessment. Anyone who promises you a number without seeing yours is guessing.

Run it properly before you move. We will help you do that, and we will tell you if the math does not work.""",

    "6a8c2c3ee7d11f6543888e57": """$1.2-$1.5M in Newton or Wellesley buys about four bedrooms. Same budget in Southern NH: newer home, more land. On taxes - NH has no income or sales tax but some of the highest property rates in the country. The net depends on YOUR numbers. Run it before you move.""",
}

TWITTER_LIMIT = 280


def request_json(method, path, payload=None):
    """Call the Late API and return parsed JSON, or raise with a useful message."""
    url = f"{BASE_URL}{path}"
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {API_KEY}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as err:
        body = err.read().decode()[:400]
        raise RuntimeError(f"{method} {path} -> HTTP {err.code}: {body}") from err


def build_platforms(post):
    """Flatten platform entries to the {platform, accountId} shape PUT expects."""
    platforms = []
    for entry in post.get("platforms", []):
        account = entry.get("accountId")
        account_id = account.get("_id") if isinstance(account, dict) else account
        platforms.append({"platform": entry.get("platform"), "accountId": account_id})
    return platforms


def update_post(post_id, new_content):
    post = request_json("GET", f"/posts/{post_id}")
    post = post.get("post", post)
    platforms = build_platforms(post)

    is_twitter = any(p["platform"] == "twitter" for p in platforms)
    if is_twitter and len(new_content) > TWITTER_LIMIT:
        raise RuntimeError(f"{post_id}: twitter copy is {len(new_content)} chars, over {TWITTER_LIMIT}")

    payload = {
        "content": new_content,
        "platforms": platforms,
        "scheduledFor": post.get("scheduledFor"),
        "mediaItems": post.get("mediaItems") or [],
    }
    # PATCH returns 405 on this API -- PUT is the only working update verb.
    request_json("PUT", f"/posts/{post_id}", payload)
    return platforms, len(new_content)


def main():
    failures = []
    for post_id, content in REPLACEMENTS.items():
        try:
            platforms, length = update_post(post_id, content)
            names = ",".join(p["platform"] for p in platforms)
            print(f"OK   {post_id}  {length:>4} chars  [{names}]")
        except Exception as exc:  # surface every failure, never swallow
            print(f"FAIL {post_id}: {exc}")
            failures.append(post_id)
    if failures:
        print(f"\n{len(failures)} post(s) failed: {', '.join(failures)}")
        sys.exit(1)
    print(f"\nAll {len(REPLACEMENTS)} posts updated.")


if __name__ == "__main__":
    main()
