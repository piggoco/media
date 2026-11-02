from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_context(locale="en-US",viewport={"width":1400,"height":1000}).new_page()
    for u in ["https://ads.tiktok.com/creative/creativeCenter/trends/hashtag?region=SE&period=7",
              "https://ads.tiktok.com/creative/creativeCenter/trends/hashtag?region=US&period=7"]:
        pg.goto(u,wait_until="networkidle",timeout=120000); pg.wait_for_timeout(15000)
        t=pg.inner_text("body"); print("=== ",u,"len",len(t)); print("TXT",t[:1200].replace("\n"," | "))
        for h in sorted(set(pg.eval_on_selector_all("a","els=>els.map(e=>e.href)"))): print("HREF",h[:150])
    b.close()
