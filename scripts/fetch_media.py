#!/usr/bin/env python3
"""Download every image listed in wanted.yaml that isn't in media/ yet.

- Scales images so the long edge is at most MAX_EDGE px (keeps the repo small).
- Writes media/CREDITS.md with source, credit and licence for every file.
- Exits non-zero only if every new download failed (partial failures are reported).
"""
import io
import sys
import urllib.request
from pathlib import Path

import yaml
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
MEDIA = ROOT / "media"
MAX_EDGE = 2160


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "piggo-media-fetcher"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def save(data, dest):
    im = Image.open(io.BytesIO(data))
    im = im.convert("RGB")
    im.thumbnail((MAX_EDGE, MAX_EDGE))
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, "JPEG", quality=88, optimize=True)
    return im.size


def main():
    spec = yaml.safe_load((ROOT / "wanted.yaml").read_text(encoding="utf-8")) or {}
    items = spec.get("images", [])
    new, failed = 0, []
    for it in items:
        dest = MEDIA / it["file"]
        if dest.exists() or not it.get("url"):
            continue
        try:
            size = save(fetch(it["url"]), dest)
            print(f"OK   {it['file']}  {size[0]}x{size[1]}")
            new += 1
        except Exception as e:  # noqa: BLE001
            print(f"FAIL {it['file']}: {e}")
            failed.append(it["file"])

    lines = ["# Credits and licences", "",
             "| File | Source | Credit | Licence | People | Page |",
             "|---|---|---|---|---|---|"]
    for it in items:
        if (MEDIA / it["file"]).exists():
            lines.append(f"| {it['file']} | {it.get('source','')} | {it.get('credit','')} | "
                         f"{it.get('license','')} | {it.get('people','')} | {it.get('page','')} |")
    MEDIA.mkdir(exist_ok=True)
    (MEDIA / "CREDITS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"\n{new} new, {len(failed)} failed")
    if failed and new == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
