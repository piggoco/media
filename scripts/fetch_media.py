#!/usr/bin/env python3
"""Download every image listed in wanted.yaml that isn't in media/ yet.

- Scales images so the long edge is at most MAX_EDGE px (keeps the repo small).
- Writes media/CREDITS.md with source, credit and licence for every file.
- Exits non-zero only if every new download failed (partial failures are reported).
"""
import io
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import yaml
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
MEDIA = ROOT / "media"
MAX_EDGE = 2160


UA = "piggo-media-fetcher/1.1 (https://piggo.se; github.com/piggoco/media)"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def save(data, dest):
    im = Image.open(io.BytesIO(data))
    im = im.convert("RGB")
    im.thumbnail((MAX_EDGE, MAX_EDGE))
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, "JPEG", quality=88, optimize=True)
    return im.size


def commons_info(name):
    """Look up a Wikimedia Commons file: download URL (2000 px wide), author, licence, size."""
    api = ("https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=imageinfo"
           "&iiprop=url|size|extmetadata&iiurlwidth=2000&titles=" + urllib.parse.quote("File:" + name))
    page = next(iter(json.loads(fetch(api))["query"]["pages"].values()))
    ii = page["imageinfo"][0]
    md = {k: re.sub(r"<[^>]+>", "", str(v.get("value", ""))).strip() for k, v in ii.get("extmetadata", {}).items()}
    return {
        "download": ii.get("thumburl") or ii["url"],
        "author": md.get("Artist", ""),
        "license": md.get("LicenseShortName", ""),
        "license_url": md.get("LicenseUrl", ""),
        "attribution_required": md.get("AttributionRequired", ""),
        "size": f"{ii.get('width')}x{ii.get('height')}",
        "description": md.get("ImageDescription", "")[:300],
        "page": ii.get("descriptionurl", ""),
    }


def main():
    spec = yaml.safe_load((ROOT / "wanted.yaml").read_text(encoding="utf-8")) or {}
    items = spec.get("images", [])
    new, failed = 0, []
    for it in items:
        dest = MEDIA / it["file"]
        if dest.exists() or not (it.get("url") or it.get("commons_file")):
            continue
        try:
            url = it.get("url")
            if it.get("commons_file"):
                info = commons_info(it["commons_file"])
                url = info["download"]
                meta_dir = MEDIA / "commons-meta"
                meta_dir.mkdir(parents=True, exist_ok=True)
                (meta_dir / (Path(it["file"]).stem + ".json")).write_text(
                    json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
            size = save(fetch(url), dest)
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
