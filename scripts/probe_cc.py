from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_context(locale="en-US").new_page()
    for u in ["https://ads.tiktok.com/creative/creativeCenter/trends/hashtag?region=SE&period=7",
              "https://ads.tiktok.com/business/creativecenter/music/pc/en"]:
        pg.goto(u,wait_until="domcontentloaded",timeout=90000); pg.wait_for_timeout(10000)
        print("=== ",u,"->",pg.url)
        hrefs=sorted(set(pg.eval_on_selector_all("a","els=>els.map(e=>e.href)")))
        for h in hrefs:
            if "tiktok.com" in h: print("HREF",h[:160])
        print(pg.inner_text("body")[:800].replace("\n"," | "))
    b.close()
