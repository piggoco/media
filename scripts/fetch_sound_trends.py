#!/usr/bin/env python3
"""
Fetch TikTok Creative Center trending songs (Sweden, approved for business use)
and save them to ljud/trender-<YYYY>-W<WW>.json + .md and ljud/trender-senaste.json.

Runs in GitHub Actions (scheduled) because Claude's workspace can't reach Creative Center.
How it works: open the public Creative Center music page in a headless browser, capture the
signed API request the page itself makes, then replay it with our filters (country SE,
last 7 days, commercial music only) for both the "popular" and "breakout/surging" lists.
"""
import datetime as dt
import json
import sys
from pathlib import Path
from urllib.parse import urlencode, urlparse, parse_qsl

from playwright.sync_api import sync_playwright

PAGE = "https://ads.tiktok.com/business/creativecenter/inspiration/popular/music/pc/en"
API_PART = "popular_trend/sound/rank_list"
COUNTRY = "SE"
PERIOD = 7
LIMIT = 20
OUT = Path(__file__).resolve().parent.parent / "ljud"


def main():
    captured = {}
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(
            locale="en-US",
            user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"),
        )
        page = ctx.new_page()

        def on_request(req):
            if API_PART in req.url and "url" not in captured:
                captured["url"] = req.url
                captured["headers"] = req.headers

        page.on("request", on_request)
        page.goto(PAGE, wait_until="domcontentloaded", timeout=90_000)
        for _ in range(30):
            if "url" in captured:
                break
            page.wait_for_timeout(1000)
        if "url" not in captured:
            print("Could not capture the Creative Center API request. Page title:", page.title())
            print(page.inner_text("body")[:1500])
            sys.exit(1)
        print("Captured:", captured["url"])

        base = urlparse(captured["url"])
        base_params = dict(parse_qsl(base.query))
        headers = {k: v for k, v in captured["headers"].items()
                   if k.lower() not in ("content-length", "host", "accept-encoding")}

        results = {}
        for rank_type, label in (("popular", "Popular"), ("surging", "Breakout")):
            params = dict(base_params, page="1", limit=str(LIMIT), period=str(PERIOD),
                          country_code=COUNTRY, rank_type=rank_type, commercial_music="true",
                          new_on_board="false")
            url = f"{base.scheme}://{base.netloc}{base.path}?{urlencode(params)}"
            r = ctx.request.get(url, headers=headers, timeout=60_000)
            try:
                data = r.json()
            except Exception:
                print(f"{label}: HTTP {r.status}, not JSON: {r.text()[:300]}")
                continue
            if data.get("code") not in (0, None):
                print(f"{label}: API code {data.get('code')} {data.get('msg')}")
            items = (data.get("data") or {}).get("sound_list") or []
            print(f"{label}: {len(items)} songs")
            results[label] = [simplify(i, n) for n, i in enumerate(items, 1)]
        browser.close()

    if not any(results.values()):
        print("No songs returned – Creative Center may require login or have changed.")
        sys.exit(1)
    write(results)


def simplify(i, n):
    trend = i.get("trend") or []
    curve = [t.get("value") for t in trend if isinstance(t, dict)]
    return {
        "rank": i.get("rank", n),
        "title": i.get("title"),
        "artist": i.get("author"),
        "clip_id": i.get("clip_id") or i.get("song_id"),
        "duration_s": i.get("duration"),
        "rank_diff": i.get("rank_diff"),
        "rank_diff_type": i.get("rank_diff_type"),
        "is_new": i.get("on_list_times") in (None, 1) and i.get("rank_diff_type") == 4,
        "commercial": True,  # the commercial_music filter was applied
        "trend_curve": curve,
        "rising": len(curve) >= 2 and curve[-1] is not None and curve[0] is not None and curve[-1] > curve[0],
        "link": i.get("link"),
    }


def write(results):
    OUT.mkdir(exist_ok=True)
    now = dt.datetime.now(dt.timezone.utc)
    y, w, _ = now.isocalendar()
    payload = {"fetched_at": now.isoformat(timespec="seconds"), "country": COUNTRY,
               "period_days": PERIOD, "filter": "Approved for business use", "lists": results}
    name = f"trender-{y}-W{w:02d}"
    for target in (OUT / f"{name}.json", OUT / "trender-senaste.json"):
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [f"# Trendande ljud – Sverige, godkända för företag ({now:%Y-%m-%d})", "",
             "Källa: TikTok Creative Center, senaste 7 dagarna. Hämtat automatiskt.", ""]
    for label, songs in results.items():
        lines += [f"## {label}", "", "| # | Titel | Artist | Stigande |", "|---|---|---|---|"]
        lines += [f"| {s['rank']} | {s['title']} | {s['artist']} | {'ja' if s['rising'] else ''} |"
                  for s in songs]
        lines.append("")
    (OUT / f"{name}.md").write_text("\n".join(lines), encoding="utf-8")
    print("Wrote", name)


if __name__ == "__main__":
    main()
