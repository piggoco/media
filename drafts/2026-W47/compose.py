#!/usr/bin/env python3
"""Pre-composites for W47 (product cards for FB, product slides for the IG reel).
Same helpers as drafts/2026-W46/compose.py; output to renderer/assets/media/w47."""
import importlib.util, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location("c46", Path(__file__).resolve().parent.parent / "2026-W46" / "compose.py")
c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
c.OUT = Path("/home/claude/renderer/assets/media/w47"); c.OUT.mkdir(parents=True, exist_ok=True)
P = {
    "olivtval": "produkter/olivtval-handkram/olivtval-handkram-studio-01.jpg",
    "pepparmix": "produkter/vild-pepparmix/vild-pepparmix-studio-01.jpg",
    "chilisalt": "produkter/havssalt-chili-vitlok/havssalt-chili-vitlok-studio-01.jpg",
    "badrumskit": "produkter/haxan-badrumskit/haxan-badrumskit-studio-01.jpg",
    "herrgardsljus": "produkter/herrgardsljus/herrgardsljus-studio-01.jpg",
}
for n, src in P.items():
    print(c.card(src, n, "post"))
    print(c.product(src, n, "reel", center_y=round(1920 * 0.62)))  # lower than W46 so top labels clear tall products
