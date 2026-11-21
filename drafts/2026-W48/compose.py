#!/usr/bin/env python3
"""Pre-composites for W48: whole-photo school composites (W48-01 Gissa staden) and product
cards/slides (W48-05). Same helpers as drafts/2026-W46/compose.py; output to renderer/assets/media/w48."""
import importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location("c46", Path(__file__).resolve().parent.parent / "2026-W46" / "compose.py")
c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
c.OUT = Path("/home/claude/renderer/assets/media/w48"); c.OUT.mkdir(parents=True, exist_ok=True)
S = [  # credit without school/city name – the city is the quiz answer
    ("skolor/katedralskolan-lund.jpg", "Foto: Dguendel / Wikimedia Commons, CC BY 4.0", "lund"),
    ("skolor/hvitfeldtska-goteborg.jpg", "Foto: Historiker / Wikimedia Commons, CC BY-SA 3.0", "goteborg"),
    ("skolor/rudbeckianska-vasteras.jpg", "Foto: Christer Johansson / Wikimedia Commons, CC BY-SA 2.5", "vasteras"),
    ("skolor/katedralskolan-uppsala.jpg", "Foto: Wazzaa97 / Wikimedia Commons, CC BY-SA 3.0", "uppsala"),
    ("skolor/malmo-latinskola.jpg", "Foto: jorchr / Wikimedia Commons, CC BY-SA 3.0", "malmo"),
    ("skolor/sodra-latin-stockholm.jpg", "Foto: Helge Høifødt / Wikimedia Commons, CC BY-SA 3.0", "stockholm"),
]
for src, cr, n in S:
    print(c.school(src, cr, n, "reel"))
P = {
    "olivtval": "produkter/olivtval-handkram/olivtval-handkram-studio-01.jpg",
    "pepparmix": "produkter/vild-pepparmix/vild-pepparmix-studio-01.jpg",
    "chilisalt": "produkter/havssalt-chili-vitlok/havssalt-chili-vitlok-studio-01.jpg",
    "badrumskit": "produkter/haxan-badrumskit/haxan-badrumskit-studio-01.jpg",
    "herrgardsljus": "produkter/herrgardsljus/herrgardsljus-studio-01.jpg",
}
for n, src in P.items():
    print(c.card(src, n, "post"))
    print(c.product(src, n, "reel", center_y=round(1920 * 0.62)))
