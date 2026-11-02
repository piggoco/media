import json
from playwright.sync_api import sync_playwright
URLS=["https://ads.tiktok.com/creative/creativeCenter/trends/song?region=SE&period=7",
      "https://ads.tiktok.com/creative/creativeCenter/trends/music?region=SE&period=7"]
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(locale="en-US"); pg=ctx.new_page()
    def on_resp(r):
        if r.request.resource_type in ("xhr","fetch") and "ads.tiktok.com" in r.url and "monitor" not in r.url:
            try: body=r.text()
            except Exception: body=""
            print("RESP",r.status,r.url[:220]); 
            if any(k in r.url.lower() for k in ("song","music","sound","knowledge")): print("   BODY",body[:1500])
    pg.on("response",on_resp)
    for u in URLS:
        print("=== GOTO",u)
        pg.goto(u,wait_until="domcontentloaded",timeout=90000); pg.wait_for_timeout(12000)
        print("FINAL",pg.url); print(pg.inner_text("body")[:2500])
    b.close()
